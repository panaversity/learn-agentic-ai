# 18_daca_prototyping_deployment: Deploying DACA to a Prototyping Stack

Welcome to the eighteenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll transition from local development to the **Prototyping** stage of DACA’s ascent, deploying the `chat_service`, `analytics_service`, and `review_ui` to a free-tier prototyping stack. The goal is to test and validate the application with minimal cost, using real-world infrastructure while staying within free-tier limits. We’ll deploy to **Hugging Face Docker Spaces** for container hosting, use **Google Gemini** (free tier) for LLM capabilities, **CloudAMQP RabbitMQ** for messaging, **cron-job.org** for scheduling, **CockroachDB Serverless** for the database, **Upstash Redis** for in-memory storage, and **Dapr** sidecars for distributed system capabilities. Let’s ascend to the prototyping stage!

---

## What You’ll Learn
- Deploying the DACA application to Hugging Face Docker Spaces for free container hosting.
- Configuring Google Gemini (free tier) as the LLM provider instead of OpenAI.
- Setting up CloudAMQP RabbitMQ for messaging and cron-job.org for scheduling tasks.
- Using CockroachDB Serverless and Upstash Redis for persistent and in-memory storage.
- Running Dapr sidecars alongside the application containers.
- Testing the application with limited scalability (10s-100s of users, 5-20 req/s) while staying within free-tier limits.

## Prerequisites
- Completion of **17_relational_sqlmodel** (Chat Service with SQLModel, CockroachDB, Dapr state management, Analytics Service, Review UI, Docker Compose setup).
- Accounts for:
  - Hugging Face (for Docker Spaces).
  - Google Cloud (for Gemini API free tier).
  - CloudAMQP (RabbitMQ free tier).
  - cron-job.org (free scheduler).
  - CockroachDB Serverless (already set up in **17_relational_sqlmodel**).
  - Upstash (for Redis free tier).
- Basic familiarity with Docker, Dapr, and the DACA application architecture.

---

## Step 1: Set Up the Prototyping Stack
Let’s configure the free-tier services for the prototyping deployment. We’ll replace local components (e.g., Redis, RabbitMQ) with cloud-based alternatives and switch the LLM provider to Google Gemini.

### Step 1.1: Set Up Hugging Face Docker Spaces
Hugging Face Docker Spaces provides free container hosting with CI/CD, ideal for prototyping. Let’s create a Space for the DACA application.

1. **Create a Hugging Face Account**:
   - Sign up at [Hugging Face](https://huggingface.co/join).
   - Verify your email.

2. **Create a Docker Space**:
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces).
   - Click **Create a Space**.
   - Name: `daca-prototype`.
   - Select **Docker** as the Space type.
   - Choose **Public** visibility (free tier requirement).
   - For now, leave the default `Dockerfile` (we’ll customize it later).

3. **Set Up a Repository Token**:
   - Go to your Hugging Face profile > **Settings** > **Access Tokens**.
   - Create a new token with **Write** access (e.g., `HF_TOKEN`).
   - Save this token securely—we’ll use it to push Docker images.

### Step 1.2: Set Up Google Gemini API (Free Tier)
Google Gemini offers a free tier for LLM capabilities, which we’ll use instead of OpenAI.

1. **Sign Up for Google Cloud**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Sign up and activate the free tier (90-day trial with $300 credit, plus always-free products).

2. **Enable the Gemini API**:
   - In the Google Cloud Console, go to **APIs & Services** > **Library**.
   - Search for **Generative Language API** (Gemini API).
   - Enable the API.
   - Go to **APIs & Services** > **Credentials** > **Create Credentials** > **API Key**.
   - Copy the API key (e.g., `GEMINI_API_KEY`).

3. **Test the Gemini API**:
   - Use a tool like `curl` to verify the API key:
     ```bash
     curl -H "Content-Type: application/json" \
          -d '{"contents":[{"parts":[{"text":"Hello, Gemini!"}]}]}' \
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=$GEMINI_API_KEY"
     ```
   - You should receive a JSON response with generated text.

### Step 1.3: Set Up CloudAMQP RabbitMQ (Free Tier)
CloudAMQP provides a free RabbitMQ instance for messaging (1M messages/month, 20 connections).

1. **Sign Up for CloudAMQP**:
   - Go to [CloudAMQP](https://www.cloudamqp.com/).
   - Sign up for a free account.
   - Create a new instance with the **Little Lemur** plan (free tier).

2. **Get Connection Details**:
   - After the instance is created, go to the instance dashboard.
   - Copy the **AMQP URL** (e.g., `amqp://user:password@lemur-01.rmq.cloudamqp.com/vhost`).
   - Note the **Host**, **Username**, **Password**, and **VHost** for Dapr configuration.

### Step 1.4: Set Up cron-job.org for Scheduling
We’ll use cron-job.org to schedule a nightly task to reset analytics data.

1. **Sign Up for cron-job.org**:
   - Go to [cron-job.org](https://cron-job.org/).
   - Sign up for a free account.

2. **Create a Cron Job**:
   - After signing in, click **Create Cronjob**.
   - Title: `Reset Analytics Data`.
   - URL: `http://<hugging-face-space-url>/analytics/reset` (we’ll update this after deployment).
   - Schedule: Daily at 00:00 UTC (`0 0 * * *`).
   - Save the cron job (we’ll update the URL later).

### Step 1.5: Verify CockroachDB Serverless Setup
We already set up CockroachDB Serverless in **17_relational_sqlmodel**. Verify the connection:
- Connection String: `postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full`.
- CA Certificate: Ensure `chat_service/cc-ca.crt` is available.

### Step 1.6: Set Up Upstash Redis (Free Tier)
Upstash provides a serverless Redis instance with a free tier (10,000 commands/day, 256 MB).

1. **Sign Up for Upstash**:
   - Go to [Upstash](https://upstash.com/).
   - Sign up for a free account.

2. **Create a Redis Database**:
   - Click **Create Database**.
   - Name: `daca-redis`.
   - Select a region (e.g., `us-east-1`).
   - Choose the free tier plan.

3. **Get Connection Details**:
   - Go to the database dashboard.
   - Copy the **REST URL** (e.g., `https://us1-rapid-12345.upstash.io`) and **Token**.
   - Note the connection details for Dapr and the application.

---

## Step 2: Update the DACA Application for Prototyping
We need to modify the `chat_service`, `analytics_service`, and `review_ui` to use the new prototyping stack components.

### Step 2.1: Update `chat_service` for Gemini and CloudAMQP
Modify `chat_service/main.py` to use the Gemini API instead of OpenAI and update Dapr components for CloudAMQP and Upstash Redis.

#### Update `chat_service/main.py`
```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
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

# Google Gemini client setup
def get_gemini_client():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return gemini_api_key

def generate_reply(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    message = input["message"]
    message_count = input["message_count"]
    history = input["history"]
    
    prompt = f"User {user_id} has sent {message_count} messages. History: {history}\nMessage: {message}\nReply as a helpful assistant:"
    api_key = get_gemini_client()
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        params={"key": api_key}
    )
    response.raise_for_status()
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"].strip()

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

#### Update Dapr Components
- **Update `components/pubsub.yaml` for CloudAMQP**:
  ```yaml
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: pubsub
  spec:
    type: pubsub.rabbitmq
    version: v1
    metadata:
    - name: host
      value: "amqp://<username>:<password>@<cloudamqp-host>/<vhost>"
    - name: durable
      value: "true"
    - name: deleted
      value: "false"
    - name: autoAck
      value: "false"
    - name: reconnectWait
      value: "0"
    - name: concurrency
      value: "parallel"
  ```
  Replace `<username>`, `<password>`, `<cloudamqp-host>`, and `<vhost>` with your CloudAMQP details.

- **Update `components/statestore.yaml` for Upstash Redis**:
  ```yaml
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: statestore
  spec:
    type: state.redis
    version: v1
    metadata:
    - name: redisHost
      value: "<upstash-rest-url>"
    - name: redisPassword
      value: "<upstash-token>"
    - name: actorStateStore
      value: "true"
  ```
  Replace `<upstash-rest-url>` and `<upstash-token>` with your Upstash Redis details.

### Step 2.2: Update `analytics_service` for Upstash Redis
The `analytics_service` uses Redis to store message counts. Update `analytics_service/main.py` to use Upstash Redis.

#### Update `analytics_service/main.py`
```python
import logging
from fastapi import FastAPI
import redis.asyncio as redis
from dapr.clients import DaprClient
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalyticsService")

app = FastAPI()

# Redis setup for Upstash
redis_url = os.getenv("REDIS_URL", "<upstash-rest-url>")
redis_token = os.getenv("REDIS_TOKEN", "<upstash-token>")
redis_client = redis.Redis.from_url(redis_url, password=redis_token, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    with DaprClient() as d:
        d.subscribe_pubsub(
            pubsub_name="pubsub",
            topic_name="messages",
            route="/messages"
        )

@app.post("/messages")
async def handle_message_event(event: dict):
    logger.info(f"Received message event: {event}")
    data = event.get("data", {})
    user_id = data.get("user_id")
    if user_id:
        await redis_client.incr(f"message_count:{user_id}")
        logger.info(f"Incremented message count for user {user_id}")
    return {"status": "success"}

@app.get("/analytics/{user_id}")
async def get_analytics(user_id: str):
    count = await redis_client.get(f"message_count:{user_id}")
    count = int(count) if count else 0
    return {"user_id": user_id, "message_count": count}

@app.post("/analytics/{user_id}/initialize")
async def initialize_analytics(user_id: str, data: dict):
    count = data.get("message_count", 0)
    await redis_client.set(f"message_count:{user_id}", count)
    return {"status": "success", "user_id": user_id, "message_count": count}

@app.post("/analytics/reset")
async def reset_analytics():
    keys = await redis_client.keys("message_count:*")
    if keys:
        await redis_client.delete(*keys)
    return {"status": "success", "message": "Analytics data reset"}
```

Replace `<upstash-rest-url>` and `<upstash-token>` with your Upstash Redis details.

### Step 2.3: Update `review_ui` for Upstash Redis
The `review_ui` uses Dapr state management, which we’ve already configured to use Upstash Redis in `components/statestore.yaml`. No changes are needed to `review_ui/app.py`.

---

## Step 3: Create Dockerfiles for Hugging Face Docker Spaces
Hugging Face Docker Spaces uses a `Dockerfile` to build and deploy the application. We’ll create a multi-container setup with Dapr sidecars.

### Step 3.1: Create a `Dockerfile` for the Space
In the project root, create a `Dockerfile` for the multi-container setup:
```dockerfile
# Base image for all services
FROM python:3.11-slim AS base

# Install uv for dependency management
RUN pip install uv

# Chat Service
FROM base AS chat-service
WORKDIR /app/chat_service
COPY chat_service/pyproject.toml chat_service/uv.lock ./
COPY chat_service/main.py chat_service/models.py ./
COPY chat_service/cc-ca.crt ./
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Chat Service Dapr Sidecar
FROM daprio/dapr:1.12 AS chat-service-dapr
COPY components /components
COPY chat_service/cc-ca.crt /components/cc-ca.crt
CMD ["./daprd", "--app-id", "chat-service", "--app-port", "8000", "--dapr-http-port", "3500", "--dapr-grpc-port", "50001", "--metrics-port", "9090", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]

# Analytics Service
FROM base AS analytics-service
WORKDIR /app/analytics_service
COPY analytics_service/pyproject.toml analytics_service/uv.lock ./
COPY analytics_service/main.py ./
RUN uv sync --frozen
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

# Analytics Service Dapr Sidecar
FROM daprio/dapr:1.12 AS analytics-service-dapr
COPY components /components
CMD ["./daprd", "--app-id", "analytics-service", "--app-port", "8001", "--dapr-http-port", "3501", "--metrics-port", "9091", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]

# Review UI
FROM base AS review-ui
WORKDIR /app/review_ui
COPY review_ui/pyproject.toml review_ui/uv.lock ./
COPY review_ui/app.py ./
RUN uv sync --frozen
EXPOSE 8501
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# Review UI Dapr Sidecar
FROM daprio/dapr:1.12 AS review-ui-dapr
COPY components /components
COPY chat_service/cc-ca.crt /components/cc-ca.crt
CMD ["./daprd", "--app-id", "review-ui", "--app-port", "8501", "--dapr-http-port", "3502", "--metrics-port", "9092", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]
```

### Step 3.2: Create a `docker-compose.yml` for Hugging Face
Hugging Face Docker Spaces supports multi-container deployments via `docker-compose.yml`. Create `docker-compose.yml` in the project root:
```yaml
version: "3.9"
services:
  chat-service-app:
    build:
      context: .
      target: chat-service
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - DB_CONNECTION=postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full
      - GEMINI_API_KEY=<gemini-api-key>
    volumes:
      - ./chat_service/cc-ca.crt:/app/cc-ca.crt

  chat-service-dapr:
    build:
      context: .
      target: chat-service-dapr
    depends_on:
      - chat-service-app

  analytics-service-app:
    build:
      context: .
      target: analytics-service
    ports:
      - "8001:8001"
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=<upstash-rest-url>
      - REDIS_TOKEN=<upstash-token>

  analytics-service-dapr:
    build:
      context: .
      target: analytics-service-dapr
    depends_on:
      - analytics-service-app

  review-ui-app:
    build:
      context: .
      target: review-ui
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1

  review-ui-dapr:
    build:
      context: .
      target: review-ui-dapr
    depends_on:
      - review-ui-app
```

Replace `<password>`, `<cluster-host>`, `<gemini-api-key>`, `<upstash-rest-url>`, and `<upstash-token>` with your actual values.

---

## Step 4: Deploy to Hugging Face Docker Spaces
Now, let’s deploy the application to Hugging Face Docker Spaces.

### Step 4.1: Push the Code to Hugging Face
1. **Clone the Space Repository**:
   - Go to your `daca-prototype` Space on Hugging Face.
   - Copy the repository URL (e.g., `https://huggingface.co/spaces/<username>/daca-prototype`).
   - Clone the repository locally:
     ```bash
     git clone https://huggingface.co/spaces/<username>/daca-prototype
     cd daca-prototype
     ```

2. **Copy the DACA Project Files**:
   - Copy the `chat_service`, `analytics_service`, `review_ui`, `components`, `Dockerfile`, and `docker-compose.yml` into the cloned repository.
   - Ensure the directory structure matches the project root.

3. **Commit and Push**:
   - Add, commit, and push the changes:
     ```bash
     git add .
     git commit -m "Deploy DACA to Hugging Face Docker Spaces"
     git push https://<username>:<HF_TOKEN>@huggingface.co/spaces/<username>/daca-prototype
     ```
   - Replace `<username>` and `<HF_TOKEN>` with your Hugging Face username and token.

4. **Monitor the Build**:
   - Hugging Face will automatically build and deploy the containers.
   - Go to the Space dashboard and check the **Logs** tab for build status.
   - Once deployed, note the Space URL (e.g., `https://<username>-daca-prototype.hf.space`).

### Step 4.2: Update the cron-job.org URL
Update the cron job on cron-job.org with the deployed URL:
- URL: `https://<username>-daca-prototype.hf.space/analytics/reset`.
- Save the cron job.

---

## Step 5: Test the Prototyping Deployment
Let’s test the deployed application to ensure everything works within the free-tier limits.

### Step 5.1: Initialize Analytics Data
Initialize message counts for `alice` and `bob`:
- For `alice`:
  ```bash
  curl -X POST https://<username>-daca-prototype.hf.space/analytics/alice/initialize -H "Content-Type: application/json" -d '{"message_count": 5}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "alice", "message_count": 5}
  ```
- For `bob`:
  ```bash
  curl -X POST https://<username>-daca-prototype.hf.space/analytics/bob/initialize -H "Content-Type: application/json" -d '{"message_count": 3}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "bob", "message_count": 3}
  ```

### Step 5.2: Send a Message Requiring Human Review
Send a message with a sensitive keyword:
```bash
curl -X POST https://<username>-daca-prototype.hf.space/chat/ -H "Content-Type: application/json" -d '{"user_id": "bob", "text": "This is an urgent request!", "metadata": {"timestamp": "2025-04-06T12:00:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174001"}, "tags": ["greeting"]}'
```

The request will hang, waiting for human review.

### Step 5.3: Approve the Message in the Streamlit UI
Open the Streamlit UI at `https://<username>-daca-prototype.hf.space` (port 8501) and approve the message. The `curl` request should complete with a response like:
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

### Step 5.4: Verify Data in CockroachDB and Upstash Redis
- **CockroachDB**: Query the `conversation` table to verify the conversation was stored:
  ```sql
  SELECT * FROM conversation;
  ```
  Output:
  ```
   id | user_id |        message         |                          reply                          |       timestamp       
  ----+---------+------------------------+---------------------------------------------------------+------------------------
    1 | bob     | This is an urgent request! | Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you? | 2025-04-06 12:36:00
  ```
- **Upstash Redis**: Use the Upstash dashboard to verify message counts:
  - Key: `message_count:bob`, Value: `4` (incremented after the message).

### Step 5.5: Monitor Free-Tier Limits
- **Upstash Redis**: Ensure you’re under 10,000 commands/day (roughly 7 req/min). Use the Upstash dashboard to monitor usage.
- **CloudAMQP**: Check the dashboard to ensure you’re under 1M messages/month and 20 connections.
- **CockroachDB**: Verify you’re under 10 GiB storage and 50M RUs/month in the CockroachDB Cloud Console.

---

## Step 6: Why This Prototyping Stack?
- **Hugging Face Docker Spaces**: Free container hosting with CI/CD, perfect for public testing with a small user base.
- **Google Gemini (Free Tier)**: A cost-free LLM alternative to OpenAI, suitable for prototyping with limited usage.
- **CloudAMQP RabbitMQ**: Free messaging with enough capacity (1M messages/month) for prototyping event-driven workflows.
- **cron-job.org**: Free scheduling for simple tasks like resetting analytics data.
- **CockroachDB Serverless**: Free-tier database (10 GiB, 50M RUs) for persistent storage, with PostgreSQL compatibility.
- **Upstash Redis**: Free-tier in-memory store (10,000 commands/day) for caching and state management, optimized for serverless.
- **Dapr Sidecars**: Enable distributed system capabilities (e.g., pub/sub, state management) without code changes.

**Scalability Limits**: This stack supports 10s-100s of users and 5-20 req/s, constrained by free-tier limits (e.g., Upstash’s 7 req/min cap). For higher loads, we’ll need to scale to a production environment in the next tutorial.

**Cost**: Fully free, but requires careful monitoring of free-tier limits to avoid unexpected throttling or costs.

---

## Step 7: Next Steps
You’ve successfully deployed the DACA application to a prototyping stack using Hugging Face Docker Spaces, Google Gemini, CloudAMQP, cron-job.org, CockroachDB Serverless, Upstash Redis, and Dapr sidecars! The application is now publicly accessible for testing with a small user base, staying within free-tier limits. In the next tutorial, we’ll move to the **Staging** stage of DACA’s ascent, deploying to a more scalable environment (e.g., Azure Container Apps) to handle thousands of users while introducing paid tiers for some services.

### Exercises for Students
1. Add rate-limiting to the `chat_service` to stay within Upstash’s 7 req/min cap.
2. Implement a `/conversations/{user_id}` endpoint in `chat_service` to retrieve a user’s conversation history from CockroachDB.
3. Set up monitoring for CloudAMQP message usage to get alerts if you approach the 1M messages/month limit.

---

## Conclusion
In this tutorial, we deployed the DACA application to a prototyping stack, leveraging free-tier services to test and validate the application with minimal cost. We used Hugging Face Docker Spaces for container hosting, Google Gemini for LLM capabilities, CloudAMQP for messaging, cron-job.org for scheduling, CockroachDB Serverless for the database, Upstash Redis for in-memory storage, and Dapr sidecars for distributed system features. The application now supports 10s-100s of users and 5-20 req/s, ready for public testing. We’re now prepared to ascend to the staging stage in the next tutorial!

---

### Final `chat_service/main.py`
```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
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

def get_gemini_client():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return gemini_api_key

def generate_reply(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    message = input["message"]
    message_count = input["message_count"]
    history = input["history"]
    
    prompt = f"User {user_id} has sent {message_count} messages. History: {history}\nMessage: {message}\nReply as a helpful assistant:"
    api_key = get_gemini_client()
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        params={"key": api_key}
    )
    response.raise_for_status()
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"].strip()

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

### Final `analytics_service/main.py`
```python
import logging
from fastapi import FastAPI
import redis.asyncio as redis
from dapr.clients import DaprClient
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalyticsService")

app = FastAPI()

redis_url = os.getenv("REDIS_URL", "<upstash-rest-url>")
redis_token = os.getenv("REDIS_TOKEN", "<upstash-token>")
redis_client = redis.Redis.from_url(redis_url, password=redis_token, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    with DaprClient() as d:
        d.subscribe_pubsub(
            pubsub_name="pubsub",
            topic_name="messages",
            route="/messages"
        )

@app.post("/messages")
async def handle_message_event(event: dict):
    logger.info(f"Received message event: {event}")
    data = event.get("data", {})
    user_id = data.get("user_id")
    if user_id:
        await redis_client.incr(f"message_count:{user_id}")
        logger.info(f"Incremented message count for user {user_id}")
    return {"status": "success"}

@app.get("/analytics/{user_id}")
async def get_analytics(user_id: str):
    count = await redis_client.get(f"message_count:{user_id}")
    count = int(count) if count else 0
    return {"user_id": user_id, "message_count": count}

@app.post("/analytics/{user_id}/initialize")
async def initialize_analytics(user_id: str, data: dict):
    count = data.get("message_count", 0)
    await redis_client.set(f"message_count:{user_id}", count)
    return {"status": "success", "user_id": user_id, "message_count": count}

@app.post("/analytics/reset")
async def reset_analytics():
    keys = await redis_client.keys("message_count:*")
    if keys:
        await redis_client.delete(*keys)
    return {"status": "success", "message": "Analytics data reset"}
```

### Final `Dockerfile`
```dockerfile
FROM python:3.11-slim AS base
RUN pip install uv

FROM base AS chat-service
WORKDIR /app/chat_service
COPY chat_service/pyproject.toml chat_service/uv.lock ./
COPY chat_service/main.py chat_service/models.py ./
COPY chat_service/cc-ca.crt ./
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM daprio/dapr:1.12 AS chat-service-dapr
COPY components /components
COPY chat_service/cc-ca.crt /components/cc-ca.crt
CMD ["./daprd", "--app-id", "chat-service", "--app-port", "8000", "--dapr-http-port", "3500", "--dapr-grpc-port", "50001", "--metrics-port", "9090", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]

FROM base AS analytics-service
WORKDIR /app/analytics_service
COPY analytics_service/pyproject.toml analytics_service/uv.lock ./
COPY analytics_service/main.py ./
RUN uv sync --frozen
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

FROM daprio/dapr:1.12 AS analytics-service-dapr
COPY components /components
CMD ["./daprd", "--app-id", "analytics-service", "--app-port", "8001", "--dapr-http-port", "3501", "--metrics-port", "9091", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]

FROM base AS review-ui
WORKDIR /app/review_ui
COPY review_ui/pyproject.toml review_ui/uv.lock ./
COPY review_ui/app.py ./
RUN uv sync --frozen
EXPOSE 8501
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

FROM daprio/dapr:1.12 AS review-ui-dapr
COPY components /components
COPY chat_service/cc-ca.crt /components/cc-ca.crt
CMD ["./daprd", "--app-id", "review-ui", "--app-port", "8501", "--dapr-http-port", "3502", "--metrics-port", "9092", "--log-level", "debug", "--config", "/components/tracing.yaml", "--components-path", "/components"]
```

### Final `docker-compose.yml`
```yaml
version: "3.9"
services:
  chat-service-app:
    build:
      context: .
      target: chat-service
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - DB_CONNECTION=postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full
      - GEMINI_API_KEY=<gemini-api-key>
    volumes:
      - ./chat_service/cc-ca.crt:/app/cc-ca.crt

  chat-service-dapr:
    build:
      context: .
      target: chat-service-dapr
    depends_on:
      - chat-service-app

  analytics-service-app:
    build:
      context: .
      target: analytics-service
    ports:
      - "8001:8001"
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=<upstash-rest-url>
      - REDIS_TOKEN=<upstash-token>

  analytics-service-dapr:
    build:
      context: .
      target: analytics-service-dapr
    depends_on:
      - analytics-service-app

  review-ui-app:
    build:
      context: .
      target: review-ui
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1

  review-ui-dapr:
    build:
      context: .
      target: review-ui-dapr
    depends_on:
      - review-ui-app
```

---

This tutorial successfully deploys the DACA application to a prototyping stack, ready for testing with a small user base. 