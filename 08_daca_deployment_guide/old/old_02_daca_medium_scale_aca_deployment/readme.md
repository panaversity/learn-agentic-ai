# Deploying DACA to Azure Container Apps with Dapr

Welcome to the nineteenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll move to the **Medium Enterprise Scale** stage of DACA’s ascent by deploying the `chat_service`, `analytics_service`, and `review_ui` to **Azure Container Apps (ACA)** with Dapr support. We’ll leverage ACA’s free tier (180,000 vCPU-s, 360,000 GiB-s/month), configure auto-scaling using HTTP traffic and KEDA triggers, integrate with managed services, and use ACA Jobs for scheduled tasks. This deployment will scale to thousands of users (e.g., 10,000 req/min), balancing cost efficiency with performance. Let’s ascend to medium enterprise scale!

---

## What You’ll Learn
- Deploying the DACA application to Azure Container Apps (ACA) with Dapr support.
- Configuring auto-scaling using HTTP traffic and KEDA triggers for RabbitMQ message queues.
- Integrating with managed services like OpenAI (or Google Gemini for cost efficiency), CloudAMQP RabbitMQ, CockroachDB Serverless, and Upstash Redis.
- Using ACA Jobs to schedule tasks (e.g., resetting analytics data).
- Monitoring costs to stay within ACA’s free tier, with guidance for scaling to paid tiers.

## Prerequisites
- Completion of **18_daca_prototyping_deployment** (Prototyping deployment with Hugging Face Docker Spaces, Google Gemini, CloudAMQP, CockroachDB, Upstash Redis, Dapr).
- An Azure account with access to Azure Container Apps (ACA) free tier.
- Azure CLI installed (`az` command).
- Existing accounts for:
  - OpenAI (or Google Gemini for cost efficiency).
  - CloudAMQP RabbitMQ (free tier, with option to scale to paid).
  - CockroachDB Serverless (free tier, with option to scale to paid).
  - Upstash Redis (free tier, with option to scale to paid).
- Basic familiarity with Azure, ACA, and Dapr.

---

## Step 1: Set Up Azure Container Apps Environment
Let’s set up an ACA environment to host the DACA application, leveraging Dapr for distributed system capabilities.

### Step 1.1: Sign Up for Azure and Install Azure CLI
1. **Create an Azure Account**:
   - Sign up at [Azure Portal](https://portal.azure.com/).
   - Activate the free tier (30-day trial with $200 credit, plus always-free services).

2. **Install Azure CLI**:
   - Follow the instructions at [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).
   - Log in to Azure:
     ```bash
     az login
     ```

3. **Set Up a Resource Group**:
   - Create a resource group for the DACA application:
     ```bash
     az group create --name daca-rg --location eastus
     ```

### Step 1.2: Create an ACA Environment with Dapr
1. **Create a Log Analytics Workspace** (required for ACA):
   ```bash
   az monitor log-analytics workspace create \
     --resource-group daca-rg \
     --workspace-name daca-logs \
     --location eastus
   ```
   - Retrieve the workspace ID and key:
     ```bash
     WORKSPACE_ID=$(az monitor log-analytics workspace show --resource-group daca-rg --workspace-name daca-logs --query customerId -o tsv)
     WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys --resource-group daca-rg --workspace-name daca-logs --query primarySharedKey -o tsv)
     ```

2. **Create an ACA Environment**:
   - Create an ACA environment with Dapr enabled:
     ```bash
     az containerapp env create \
       --name daca-env \
       --resource-group daca-rg \
       --location eastus \
       --logs-workspace-id $WORKSPACE_ID \
       --logs-workspace-key $WORKSPACE_KEY \
       --enable-dapr
     ```

---

## Step 2: Configure Managed Services
We’ll reuse most of the managed services from the prototyping stage, but switch the LLM provider back to OpenAI for better performance (or optionally use Google Gemini for cost efficiency). We’ll also evaluate scaling CloudAMQP and Upstash Redis to paid tiers if needed.

### Step 2.1: Set Up OpenAI API (or Google Gemini)
For medium enterprise scale, OpenAI’s Chat Completion API offers better performance, but it’s limited to 10,000 RPM (166 req/s). Google Gemini is more economical but may have lower throughput. We’ll use OpenAI for this tutorial, with notes on switching to Gemini.

1. **Get OpenAI API Key**:
   - Log in to [OpenAI Platform](https://platform.openai.com/).
   - Go to **API Keys** > **Create new secret key**.
   - Copy the key (e.g., `OPENAI_API_KEY`).

2. **(Optional) Use Google Gemini**:
   - If you prefer Gemini for cost efficiency, reuse the API key from **18_daca_prototyping_deployment**.

### Step 2.2: Evaluate CloudAMQP RabbitMQ
In the prototyping stage, we used CloudAMQP’s free tier (1M messages/month, 20 connections). For thousands of users (10,000 req/min), we may exceed this limit:
- **Estimate**: 10,000 req/min = 600,000 req/hour. If each request generates 1-2 messages, we’ll hit 1M messages in ~1-2 hours.
- **Upgrade to Paid Tier**: Upgrade to the **Tiger** plan ($10/month for 10M messages, 100 connections) if needed.
- For this tutorial, we’ll assume light traffic within the free tier, but note the upgrade option.

### Step 2.3: Verify CockroachDB Serverless and Upstash Redis
- **CockroachDB Serverless**: The free tier (10 GiB, 50M RUs/month) should suffice for light traffic. For 10,000 req/min, we may need to scale to the paid tier ($0.001/1M RUs, $0.0125/GiB-month).
- **Upstash Redis**: The free tier (10,000 commands/day) is too restrictive (7 req/min). Upgrade to the **Pro** plan ($10/month for 100,000 commands/day) to handle 10,000 req/min.

For this tutorial, we’ll assume we’ve upgraded Upstash Redis to the Pro plan.

---

## Step 3: Update the DACA Application for ACA
We need to update the `chat_service`, `analytics_service`, and `review_ui` to work with ACA, OpenAI (or Gemini), and ACA Jobs for scheduling.

### Step 3.1: Update `chat_service` for OpenAI
Modify `chat_service/main.py` to use OpenAI instead of Google Gemini. The rest of the application (e.g., SQLModel, Dapr) remains the same.

#### Update `chat_service/main.py`
```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateOptions, Concurrency, Consistency
import uuid
from datetime import datetime, timezone
import json
import time
import os
from sqlmodel import SQLModel, Session, create_engine
from models import Conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatService")

app = FastAPI()

# Database setup with SQLModel
connection_string = os.getenv("DB_CONNECTION")
engine = create_engine(connection_string, echo=True, connect_args={"sslrootcert": "/app/cc-ca.crt"})
SQLModel.metadata.create_all(engine)

# Pydantic models
class ChatRequest(BaseModel):
    user_id: str
    text: str
    metadata: Dict[str, Any]
    tags: list[str] = []

class ChatResponse(BaseModel):
    user_id: str
    reply: str
    metadata: Dict[str, Any]

# Sensitive keywords requiring human review
SENSITIVE_KEYWORDS = ["urgent", "help", "emergency"]

# Dapr client for interacting with Dapr APIs
dapr_client = DaprClient()

# OpenAI client setup
def get_openai_client():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not set")
    openai.api_key = openai_api_key
    return openai

def generate_reply(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    message = input["message"]
    message_count = input["message_count"]
    history = input["history"]
    
    prompt = f"User {user_id} has sent {message_count} messages. History: {history}\nMessage: {message}\nReply as a helpful assistant:"
    client = get_openai_client()
    response = client.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Rest of the activities (fetch_message_count, get_conversation_history, etc.) remain the same
def fetch_message_count(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> int:
    user_id = input["user_id"]
    with DaprClient() as d:
        resp = d.invoke_method(
            app_id="analytics-service",
            method_name=f"analytics/{user_id}",
            http_verb="GET"
        )
        data = resp.json()
        return data.get("message_count", 0)

def get_conversation_history(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    with Session(engine) as session:
        conversations = session.query(Conversation).filter(Conversation.user_id == user_id).all()
        if not conversations:
            return "No previous conversation."
        history = "\n".join([f"User: {conv.message}\nAssistant: {conv.reply}" for conv in conversations])
        return history

def store_conversation(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    reply = input["reply"]
    conversation = Conversation(user_id=user_id, message=message, reply=reply)
    with Session(engine) as session:
        session.add(conversation)
        session.commit()

def publish_message_sent_event(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="messages",
            data=json.dumps({"user_id": user_id, "event_type": "MessageSent"}),
            data_content_type="application/json"
        )

def check_sensitive_content(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    message = input["message"]
    is_sensitive = any(keyword in message.lower() for keyword in SENSITIVE_KEYWORDS)
    return {"is_sensitive": is_sensitive, "message": message}

def request_human_review(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    proposed_reply = input["proposed_reply"]
    instance_id = input["instance_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="human-review",
            data=json.dumps({
                "user_id": user_id,
                "message": message,
                "proposed_reply": proposed_reply,
                "instance_id": instance_id,
                "event_type": "HumanReviewRequired"
            }),
            data_content_type="application/json"
        )

def wait_for_human_decision(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    instance_id = input["instance_id"]
    with DaprClient() as d:
        while True:
            state_key = f"human-decision-{instance_id}"
            state = d.get_state(
                store_name="statestore",
                key=state_key,
                state_options=StateOptions(concurrency=Concurrency.first_write, consistency=Consistency.strong)
            )
            if state.data:
                decision_data = json.loads(state.data.decode('utf-8'))
                d.delete_state(store_name="statestore", key=state_key)
                return decision_data
            time.sleep(1)

def chat_workflow(context: DaprWorkflowContext, input: Dict[str, Any]) -> Dict[str, Any]:
    user_id = input["user_id"]
    message = input["message"]
    instance_id = context.instance_id

    logger.info(f"Starting workflow for user {user_id} with message: {message}")

    message_count = yield context.call_activity(fetch_message_count, input={"user_id": user_id})
    history = yield context.call_activity(get_conversation_history, input={"user_id": user_id})
    proposed_reply = yield context.call_activity(generate_reply, input={
        "user_id": user_id,
        "message": message,
        "message_count": message_count,
        "history": history
    })
    sensitive_result = yield context.call_activity(check_sensitive_content, input={"message": message})
    is_sensitive = sensitive_result["is_sensitive"]

    if is_sensitive:
        logger.info(f"Sensitive content detected in message: {message}. Requesting human review.")
        yield context.call_activity(request_human_review, input={
            "user_id": user_id,
            "message": message,
            "proposed_reply": proposed_reply,
            "instance_id": instance_id
        })
        decision = yield context.call_activity(wait_for_human_decision, input={"instance_id": instance_id})
        approved = decision["approved"]

        if not approved:
            logger.info(f"Human rejected the response for user {user_id}. Aborting workflow.")
            return {
                "user_id": user_id,
                "reply": "Message rejected by human reviewer.",
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
            }

    yield context.call_activity(store_conversation, input={
        "user_id": user_id,
        "message": message,
        "reply": proposed_reply
    })
    yield context.call_activity(publish_message_sent_event, input={"user_id": user_id})

    logger.info(f"Completed workflow for user {user_id}")
    return {
        "user_id": user_id,
        "reply": proposed_reply,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
    }

workflow_runtime = WorkflowRuntime()
workflow_runtime.register_workflow(chat_workflow)
workflow_runtime.register_activity(fetch_message_count)
workflow_runtime.register_activity(get_conversation_history)
workflow_runtime.register_activity(generate_reply)
workflow_runtime.register_activity(store_conversation)
workflow_runtime.register_activity(publish_message_sent_event)
workflow_runtime.register_activity(check_sensitive_content)
workflow_runtime.register_activity(request_human_review)
workflow_runtime.register_activity(wait_for_human_decision)

@app.on_event("startup")
async def start_workflow_runtime():
    await workflow_runtime.start()

@app.on_event("shutdown")
async def stop_workflow_runtime():
    await workflow_runtime.shutdown()

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Received chat request for user {request.user_id}: {request.text}")
    instance_id = f"chat-{request.user_id}-{int(time.time())}"
    logger.info(f"Scheduling workflow with instance_id: {instance_id}")

    with DaprClient() as d:
        d.start_workflow(
            workflow_component="dapr",
            workflow_name="chat_workflow",
            input={
                "user_id": request.user_id,
                "message": request.text
            },
            instance_id=instance_id
        )

        while True:
            state = d.get_workflow(instance_id=instance_id, workflow_component="dapr")
            if state.runtime_status == "COMPLETED":
                result = state.result
                return ChatResponse(**result)
            elif state.runtime_status == "FAILED":
                raise HTTPException(status_code=500, detail="Workflow failed")
            time.sleep(0.5)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### (Optional) Switch to Google Gemini
If you prefer Gemini for cost efficiency, replace the `generate_reply` function with the version from **18_daca_prototyping_deployment** and update the environment variable to `GEMINI_API_KEY`.

### Step 3.2: Update Dapr Components for ACA
Dapr components in ACA are configured via the `--dapr-components` flag during deployment. Ensure the `components` directory is updated:
- `pubsub.yaml` (CloudAMQP RabbitMQ): Already configured in **18_daca_prototyping_deployment**.
- `statestore.yaml` (Upstash Redis): Already configured, but ensure you’re using the Pro plan credentials.
- `cockroachdb.yaml`: Not needed since we’re using SQLModel directly with CockroachDB.

---

## Step 4: Deploy to Azure Container Apps
We’ll deploy each service (`chat_service`, `analytics_service`, `review_ui`) as a separate ACA app, configure auto-scaling, and set up an ACA Job for scheduling.

### Step 4.1: Build and Push Docker Images
We’ll reuse the `Dockerfile` from **18_daca_prototyping_deployment**, but push the images to Azure Container Registry (ACR).

1. **Create an Azure Container Registry**:
   ```bash
   az acr create \
     --resource-group daca-rg \
     --name dacacr \
     --sku Basic \
     --location eastus
   ```

2. **Log in to ACR**:
   ```bash
   az acr login --name dacacr
   ```

3. **Tag and Push Images**:
   - Build and tag each service:
     ```bash
     docker build -t dacacr.azurecr.io/chat-service:latest --target chat-service .
     docker build -t dacacr.azurecr.io/analytics-service:latest --target analytics-service .
     docker build -t dacacr.azurecr.io/review-ui:latest --target review-ui .
     ```
   - Push the images:
     ```bash
     docker push dacacr.azurecr.io/chat-service:latest
     docker push dacacr.azurecr.io/analytics-service:latest
     docker push dacacr.azurecr.io/review-ui:latest
     ```

### Step 4.2: Deploy the Chat Service
Deploy the `chat_service` with HTTP-based auto-scaling.

1. **Create the Chat Service App**:
   ```bash
   az containerapp create \
     --name chat-service \
     --resource-group daca-rg \
     --environment daca-env \
     --image dacacr.azurecr.io/chat-service:latest \
     --registry-server dacacr.azurecr.io \
     --cpu 0.25 \
     --memory 0.5Gi \
     --min-replicas 1 \
     --max-replicas 10 \
     --scale-rule-name http-scale \
     --scale-rule-type http \
     --scale-rule-http-concurrent-requests 100 \
     --env-vars "DB_CONNECTION=postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full" "OPENAI_API_KEY=<openai-api-key>" \
     --ingress external \
     --target-port 8000 \
     --dapr-enabled \
     --dapr-app-id chat-service \
     --dapr-app-port 8000 \
     --dapr-components ./components/pubsub.yaml ./components/statestore.yaml ./components/tracing.yaml
   ```
   - **Scaling**: Scales based on HTTP concurrent requests (100 requests triggers scaling up).
   - **Resources**: 0.25 vCPU, 0.5 GiB memory (fits within free tier: 180,000 vCPU-s, 360,000 GiB-s/month).
   - **Dapr**: Enabled with `pubsub.yaml`, `statestore.yaml`, and `tracing.yaml`.

2. **Get the Chat Service URL**:
   ```bash
   CHAT_URL=$(az containerapp show --name chat-service --resource-group daca-rg --query properties.configuration.ingress.fqdn -o tsv)
   echo "Chat Service URL: https://$CHAT_URL"
   ```

### Step 4.3: Deploy the Analytics Service with KEDA Trigger
Deploy the `analytics_service` with a KEDA trigger to scale based on RabbitMQ queue length.

1. **Create a KEDA Scale Rule for RabbitMQ**:
   Create a file `rabbitmq-scale-rule.json`:
   ```json
   {
     "name": "rabbitmq-scale",
     "type": "rabbitmq",
     "metadata": {
       "queueName": "messages",
       "queueLength": "20",
       "host": "amqp://<username>:<password>@<cloudamqp-host>/<vhost>"
     }
   }
   ```
   Replace `<username>`, `<password>`, `<cloudamqp-host>`, and `<vhost>` with your CloudAMQP details.

2. **Create the Analytics Service App**:
   ```bash
   az containerapp create \
     --name analytics-service \
     --resource-group daca-rg \
     --environment daca-env \
     --image dacacr.azurecr.io/analytics-service:latest \
     --registry-server dacacr.azurecr.io \
     --cpu 0.25 \
     --memory 0.5Gi \
     --min-replicas 1 \
     --max-replicas 10 \
     --scale-rule-file rabbitmq-scale-rule.json \
     --env-vars "REDIS_URL=<upstash-rest-url>" "REDIS_TOKEN=<upstash-token>" \
     --dapr-enabled \
     --dapr-app-id analytics-service \
     --dapr-app-port 8001 \
     --dapr-components ./components/pubsub.yaml ./components/statestore.yaml ./components/tracing.yaml
   ```
   - **Scaling**: Scales based on RabbitMQ queue length (20 messages triggers scaling up).
   - **Resources**: Same as `chat_service`.

### Step 4.4: Deploy the Review UI
Deploy the `review_ui` with HTTP-based auto-scaling.

1. **Create the Review UI App**:
   ```bash
   az containerapp create \
     --name review-ui \
     --resource-group daca-rg \
     --environment daca-env \
     --image dacacr.azurecr.io/review-ui:latest \
     --registry-server dacacr.azurecr.io \
     --cpu 0.25 \
     --memory 0.5Gi \
     --min-replicas 1 \
     --max-replicas 5 \
     --scale-rule-name http-scale \
     --scale-rule-type http \
     --scale-rule-http-concurrent-requests 50 \
     --ingress external \
     --target-port 8501 \
     --dapr-enabled \
     --dapr-app-id review-ui \
     --dapr-app-port 8501 \
     --dapr-components ./components/pubsub.yaml ./components/statestore.yaml ./components/tracing.yaml
   ```

2. **Get the Review UI URL**:
   ```bash
   REVIEW_URL=$(az containerapp show --name review-ui --resource-group daca-rg --query properties.configuration.ingress.fqdn -o tsv)
   echo "Review UI URL: https://$REVIEW_URL"
   ```

### Step 4.5: Set Up an ACA Job for Scheduling
Replace the cron-job.org scheduler with an ACA Job to reset analytics data daily.

1. **Create a Job Container**:
   The `analytics_service` already has a `/analytics/reset` endpoint. We’ll create a lightweight container to call this endpoint.

   Create `analytics_job/Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   RUN pip install requests
   COPY reset.py .
   CMD ["python", "reset.py"]
   ```

   Create `analytics_job/reset.py`:
   ```python
   import requests
   import time

   ANALYTICS_URL = "https://<analytics-service-url>/analytics/reset"

   response = requests.post(ANALYTICS_URL)
   if response.status_code == 200:
       print("Analytics data reset successfully")
   else:
       print(f"Failed to reset analytics data: {response.status_code}")
   ```

   Replace `<analytics-service-url>` with the URL of the `analytics-service` (you can get this after deployment, or use the internal Dapr app ID `analytics-service` within the ACA environment).

2. **Build and Push the Job Image**:
   ```bash
   docker build -t dacacr.azurecr.io/analytics-job:latest -f analytics_job/Dockerfile .
   docker push dacacr.azurecr.io/analytics-job:latest
   ```

3. **Create the ACA Job**:
   ```bash
   az containerapp job create \
     --name analytics-reset-job \
     --resource-group daca-rg \
     --environment daca-env \
     --image dacacr.azurecr.io/analytics-job:latest \
     --registry-server dacacr.azurecr.io \
     --trigger-type Schedule \
     --cron-expression "0 0 * * *" \
     --cpu 0.25 \
     --memory 0.5Gi \
     --replica-retry-limit 1 \
     --replica-completion-count 1
   ```
   - **Schedule**: Runs daily at 00:00 UTC (`0 0 * * *`).
   - **Resources**: Minimal to stay within free tier.

---

## Step 5: Test the ACA Deployment
Let’s test the deployed application to ensure it scales to thousands of users (e.g., 10,000 req/min).

### Step 5.1: Initialize Analytics Data
Initialize message counts for `alice` and `bob`:
- For `alice`:
  ```bash
  curl -X POST https://$CHAT_URL/analytics/alice/initialize -H "Content-Type: application/json" -d '{"message_count": 5}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "alice", "message_count": 5}
  ```
- For `bob`:
  ```bash
  curl -X POST https://$CHAT_URL/analytics/bob/initialize -H "Content-Type: application/json" -d '{"message_count": 3}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "bob", "message_count": 3}
  ```

### Step 5.2: Send a Message Requiring Human Review
Send a message with a sensitive keyword:
```bash
curl -X POST https://$CHAT_URL/chat/ -H "Content-Type: application/json" -d '{"user_id": "bob", "text": "This is an urgent request!", "metadata": {"timestamp": "2025-04-06T12:00:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174001"}, "tags": ["greeting"]}'
```

The request will hang, waiting for human review.

### Step 5.3: Approve the Message in the Streamlit UI
Open the Streamlit UI at `https://$REVIEW_URL` and approve the message. The `curl` request should complete with a response like:
```json
{
  "user_id": "bob",
  "reply": "Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you?",
  "metadata": {
    "timestamp": "2025-04-06T12:36:00Z",
    "session_id": "some-uuid"
  }
}
```

### Step 5.4: Simulate Load to Test Auto-Scaling
Use a tool like `ab` (Apache Benchmark) to simulate load:
```bash
ab -n 1000 -c 100 https://$CHAT_URL/health
```
- **Expected Behavior**: The `chat_service` should scale up to handle 100 concurrent requests, up to 10 replicas.
- Check the replica count:
  ```bash
  az containerapp show --name chat-service --resource-group daca-rg --query properties.runningStatus -o tsv
  ```

### Step 5.5: Verify ACA Job Execution
Check the ACA Job logs to ensure the analytics reset job ran:
```bash
az containerapp job execution list \
  --name analytics-reset-job \
  --resource-group daca-rg \
  --query "[].{Name:name, Status:properties.status, StartTime:properties.startTime}" -o table
```

---

## Step 6: Monitor Costs and Scalability
- **ACA Free Tier**: 180,000 vCPU-s and 360,000 GiB-s/month. With 1 always-on replica (0.25 vCPU, 0.5 GiB) per service:
  - 3 services (chat, analytics, review) = 0.75 vCPU, 1.5 GiB.
  - Monthly usage: 0.75 vCPU * 2,592,000 s/month = 1,944,000 vCPU-s (exceeds free tier).
  - Cost beyond free tier: ~$0.02/vCPU-s → (1,944,000 - 180,000) * $0.02 = ~$35/month.
- **OpenAI API**: At 10,000 req/min, you’ll hit the 10,000 RPM limit. Cost: ~$0.002/1K tokens → ~$10/month for light usage.
- **CloudAMQP (Paid Tier)**: $10/month (Tiger plan).
- **Upstash Redis (Paid Tier)**: $10/month (Pro plan).
- **CockroachDB Serverless**: Free tier likely sufficient; paid tier ~$5/month if exceeded.

**Total Estimated Cost**: ~$60/month for 10,000 req/min, assuming paid tiers for CloudAMQP and Upstash Redis, and ACA beyond free tier.

**Scalability**: This setup supports thousands of users (10,000 req/min), limited by OpenAI’s 10,000 RPM (166 req/s). Switching to Google Gemini reduces costs but may lower throughput.

---

## Step 7: Why ACA for Medium Enterprise Scale?
- **Azure Container Apps (ACA)**: Serverless container hosting with built-in Dapr support, auto-scaling, and a generous free tier (180,000 vCPU-s/month).
- **Auto-Scaling**: HTTP-based scaling for `chat_service` and `review_ui`, KEDA RabbitMQ trigger for `analytics_service`.
- **ACA Jobs**: Serverless scheduling for tasks like resetting analytics data, replacing cron-job.org.
- **Managed Services**: OpenAI (or Gemini), CloudAMQP, CockroachDB, and Upstash Redis provide scalable, managed solutions.
- **Cost Efficiency**: Free tier covers light traffic; paid tier (~$0.02/vCPU-s) is affordable for medium scale.

---

## Step 8: Next Steps
You’ve successfully deployed the DACA application to Azure Container Apps, scaling to thousands of users with cost efficiency! In the next tutorial, we’ll move to the **Large Enterprise Scale** stage, deploying to Kubernetes to handle tens of thousands of users, introducing advanced monitoring, and optimizing costs for planetary scale.

### Exercises for Students
1. Add a custom KEDA scaler for `chat_service` based on CockroachDB query metrics.
2. Implement rate-limiting for OpenAI API calls to stay within the 10,000 RPM limit.
3. Set up Azure Monitor to track ACA usage and set budget alerts for cost management.

---

## Conclusion
In this tutorial, we deployed the DACA application to Azure Container Apps with Dapr support, configured auto-scaling using HTTP traffic and KEDA triggers, integrated with managed services (OpenAI, CloudAMQP, CockroachDB, Upstash Redis), and used ACA Jobs for scheduling. The application now supports thousands of users (10,000 req/min), with a total cost of ~$60/month beyond free tiers. We’re now ready to ascend to planet scale in the next tutorial!

---

### Final `chat_service/main.py`
```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateOptions, Concurrency, Consistency
import uuid
from datetime import datetime, timezone
import json
import time
import os
from sqlmodel import SQLModel, Session, create_engine
from models import Conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatService")

app = FastAPI()

connection_string = os.getenv("DB_CONNECTION")
engine = create_engine(connection_string, echo=True, connect_args={"sslrootcert": "/app/cc-ca.crt"})
SQLModel.metadata.create_all(engine)

class ChatRequest(BaseModel):
    user_id: str
    text: str
    metadata: Dict[str, Any]
    tags: list[str] = []

class ChatResponse(BaseModel):
    user_id: str
    reply: str
    metadata: Dict[str, Any]

SENSITIVE_KEYWORDS = ["urgent", "help", "emergency"]

dapr_client = DaprClient()

def get_openai_client():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not set")
    openai.api_key = openai_api_key
    return openai

def generate_reply(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    message = input["message"]
    message_count = input["message_count"]
    history = input["history"]
    
    prompt = f"User {user_id} has sent {message_count} messages. History: {history}\nMessage: {message}\nReply as a helpful assistant:"
    client = get_openai_client()
    response = client.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def fetch_message_count(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> int:
    user_id = input["user_id"]
    with DaprClient() as d:
        resp = d.invoke_method(
            app_id="analytics-service",
            method_name=f"analytics/{user_id}",
            http_verb="GET"
        )
        data = resp.json()
        return data.get("message_count", 0)

def get_conversation_history(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    with Session(engine) as session:
        conversations = session.query(Conversation).filter(Conversation.user_id == user_id).all()
        if not conversations:
            return "No previous conversation."
        history = "\n".join([f"User: {conv.message}\nAssistant: {conv.reply}" for conv in conversations])
        return history

def store_conversation(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    reply = input["reply"]
    conversation = Conversation(user_id=user_id, message=message, reply=reply)
    with Session(engine) as session:
        session.add(conversation)
        session.commit()

def publish_message_sent_event(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="messages",
            data=json.dumps({"user_id": user_id, "event_type": "MessageSent"}),
            data_content_type="application/json"
        )

def check_sensitive_content(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    message = input["message"]
    is_sensitive = any(keyword in message.lower() for keyword in SENSITIVE_KEYWORDS)
    return {"is_sensitive": is_sensitive, "message": message}

def request_human_review(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    proposed_reply = input["proposed_reply"]
    instance_id = input["instance_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="human-review",
            data=json.dumps({
                "user_id": user_id,
                "message": message,
                "proposed_reply": proposed_reply,
                "instance_id": instance_id,
                "event_type": "HumanReviewRequired"
            }),
            data_content_type="application/json"
        )

def wait_for_human_decision(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    instance_id = input["instance_id"]
    with DaprClient() as d:
        while True:
            state_key = f"human-decision-{instance_id}"
            state = d.get_state(
                store_name="statestore",
                key=state_key,
                state_options=StateOptions(concurrency=Concurrency.first_write, consistency=Consistency.strong)
            )
            if state.data:
                decision_data = json.loads(state.data.decode('utf-8'))
                d.delete_state(store_name="statestore", key=state_key)
                return decision_data
            time.sleep(1)

def chat_workflow(context: DaprWorkflowContext, input: Dict[str, Any]) -> Dict[str, Any]:
    user_id = input["user_id"]
    message = input["message"]
    instance_id = context.instance_id

    logger.info(f"Starting workflow for user {user_id} with message: {message}")

    message_count = yield context.call_activity(fetch_message_count, input={"user_id": user_id})
    history = yield context.call_activity(get_conversation_history, input={"user_id": user_id})
    proposed_reply = yield context.call_activity(generate_reply, input={
        "user_id": user_id,
        "message": message,
        "message_count": message_count,
        "history": history
    })
    sensitive_result = yield context.call_activity(check_sensitive_content, input={"message": message})
    is_sensitive = sensitive_result["is_sensitive"]

    if is_sensitive:
        logger.info(f"Sensitive content detected in message: {message}. Requesting human review.")
        yield context.call_activity(request_human_review, input={
            "user_id": user_id,
            "message": message,
            "proposed_reply": proposed_reply,
            "instance_id": instance_id
        })
        decision = yield context.call_activity(wait_for_human_decision, input={"instance_id": instance_id})
        approved = decision["approved"]

        if not approved:
            logger.info(f"Human rejected the response for user {user_id}. Aborting workflow.")
            return {
                "user_id": user_id,
                "reply": "Message rejected by human reviewer.",
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
            }

    yield context.call_activity(store_conversation, input={
        "user_id": user_id,
        "message": message,
        "reply": proposed_reply
    })
    yield context.call_activity(publish_message_sent_event, input={"user_id": user_id})

    logger.info(f"Completed workflow for user {user_id}")
    return {
        "user_id": user_id,
        "reply": proposed_reply,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
    }

workflow_runtime = WorkflowRuntime()
workflow_runtime.register_workflow(chat_workflow)
workflow_runtime.register_activity(fetch_message_count)
workflow_runtime.register_activity(get_conversation_history)
workflow_runtime.register_activity(generate_reply)
workflow_runtime.register_activity(store_conversation)
workflow_runtime.register_activity(publish_message_sent_event)
workflow_runtime.register_activity(check_sensitive_content)
workflow_runtime.register_activity(request_human_review)
workflow_runtime.register_activity(wait_for_human_decision)

@app.on_event("startup")
async def start_workflow_runtime():
    await workflow_runtime.start()

@app.on_event("shutdown")
async def stop_workflow_runtime():
    await workflow_runtime.shutdown()

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Received chat request for user {request.user_id}: {request.text}")
    instance_id = f"chat-{request.user_id}-{int(time.time())}"
    logger.info(f"Scheduling workflow with instance_id: {instance_id}")

    with DaprClient() as d:
        d.start_workflow(
            workflow_component="dapr",
            workflow_name="chat_workflow",
            input={
                "user_id": request.user_id,
                "message": request.text
            },
            instance_id=instance_id
        )

        while True:
            state = d.get_workflow(instance_id=instance_id, workflow_component="dapr")
            if state.runtime_status == "COMPLETED":
                result = state.result
                return ChatResponse(**result)
            elif state.runtime_status == "FAILED":
                raise HTTPException(status_code=500, detail="Workflow failed")
            time.sleep(0.5)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Final `analytics_job/reset.py`
```python
import requests
import time

ANALYTICS_URL = "https://<analytics-service-url>/analytics/reset"

response = requests.post(ANALYTICS_URL)
if response.status_code == 200:
    print("Analytics data reset successfully")
else:
    print(f"Failed to reset analytics data: {response.status_code}")
```

---

This tutorial successfully deploys the DACA application to Azure Container Apps, scaling to thousands of users with cost efficiency. 