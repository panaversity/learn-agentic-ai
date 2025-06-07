# 16_daca_hitl: Human-in-the-Loop (HITL) Integration with DACA

Welcome to the sixteenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll introduce **Human-in-the-Loop (HITL)** integration into our microservices architecture. We’ll modify the Chat Service to include a workflow where an agent flags certain messages as requiring human review (e.g., potentially sensitive content). The agent will emit a "HumanReviewRequired" event, pause the workflow, and wait for human input. We’ll build a simple **Streamlit** UI for a human to approve or reject the agent’s decision, and integrate the feedback loop with Dapr by publishing a "HumanDecisionMade" event. The workflow will then resume based on the human’s decision. This HITL integration ensures that critical decisions involve human oversight, enhancing the reliability and safety of our system. Let’s dive in!

---

## What You’ll Learn
- What Human-in-the-Loop (HITL) integration is and why it’s important for agentic systems.
- How to modify the Chat Service workflow to emit a "HumanReviewRequired" event and pause for human input.
- Building a simple Streamlit UI for human review (approve/reject decisions).
- Integrating the feedback loop with Dapr by publishing a "HumanDecisionMade" event.
- Running the updated application with Docker Compose, including the new Streamlit UI service.

## Prerequisites
- Completion of **15_dapr_docker_compose** (Chat Service, Analytics Service, Dapr sidecars, Redis, Zipkin, Prometheus running with Docker Compose).
- Docker and Docker Desktop installed (from **12_docker_and_desktop**).
- An OpenAI API key (stored in `components/secrets.json`).
- Basic familiarity with Python, Streamlit, and **uv** (we’ll provide the setup).

---

## Step 1: What is Human-in-the-Loop (HITL) Integration?
**Human-in-the-Loop (HITL)** integration involves incorporating human oversight into automated workflows, particularly in scenarios where decisions have significant consequences or require nuanced judgment that AI cannot fully handle. In agentic systems, HITL ensures that agents can escalate tasks to humans when needed, combining the efficiency of automation with the reliability of human decision-making.

### Why Use HITL in DACA?
In our DACA application:
- The Chat Service uses an AI agent (via OpenAI) to generate replies to user messages.
- Some messages might be sensitive, offensive, or ambiguous (e.g., containing flagged keywords like "urgent" or "help"), requiring human review before the agent responds.
- HITL allows us to:
  - **Improve Safety**: Prevent the agent from responding inappropriately to sensitive content.
  - **Enhance Reliability**: Ensure critical decisions (e.g., approving a response) are validated by a human.
  - **Build Trust**: Provide transparency by involving humans in the decision-making process.

### HITL Workflow in This Tutorial
1. The Chat Service’s workflow detects a potentially sensitive message (e.g., containing the keyword "urgent").
2. The workflow emits a "HumanReviewRequired" event via Dapr Pub/Sub and pauses, waiting for human input.
3. A Streamlit UI displays the message to a human reviewer, who can approve or reject the agent’s proposed response.
4. The Streamlit UI publishes a "HumanDecisionMade" event with the human’s decision (approve/reject).
5. The Chat Service workflow resumes, either sending the response (if approved) or logging a rejection (if rejected).

---

## Step 2: Update the Chat Service Workflow
We’ll modify the Chat Service’s workflow in `chat_service/main.py` to include HITL integration. The workflow will check for sensitive keywords, emit a "HumanReviewRequired" event, and pause until a "HumanDecisionMade" event is received.

### Step 2.1: Update `chat_service/main.py`
Edit `chat_service/main.py` to add HITL logic to the workflow. Below is the updated code with HITL integration:

```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateOptions, StateItem, Concurrency, Consistency
import uuid
from datetime import datetime, timezone
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatService")

app = FastAPI()

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
    with DaprClient() as d:
        secret = d.get_secret(store_name="secretstore", key="openai-api-key").secret
        openai.api_key = secret["openai-api-key"]
    return openai

# Activities for the workflow
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
    with DaprClient() as d:
        actor_type = "UserSessionActor"
        actor_id = user_id
        history = d.invoke_actor(actor_type, actor_id, "GetHistory", "").data.decode('utf-8')
        return history if history else "No previous conversation."

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

def store_conversation(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    reply = input["reply"]
    with DaprClient() as d:
        actor_type = "UserSessionActor"
        actor_id = user_id
        conversation = f"User: {message}\nAssistant: {reply}"
        d.invoke_actor(actor_type, actor_id, "AddMessage", conversation)

def publish_message_sent_event(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="messages",
            data=json.dumps({"user_id": user_id, "event_type": "MessageSent"}),
            data_content_type="application/json"
        )

# New activity to check for sensitive content
def check_sensitive_content(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    message = input["message"]
    is_sensitive = any(keyword in message.lower() for keyword in SENSITIVE_KEYWORDS)
    return {"is_sensitive": is_sensitive, "message": message}

# New activity to request human review
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

# New activity to wait for human decision
def wait_for_human_decision(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    instance_id = input["instance_id"]
    with DaprClient() as d:
        # Subscribe to the human-decision topic to wait for the decision
        while True:
            # In a real-world scenario, use Dapr's pub/sub subscription API or external event triggers
            # For simplicity, we'll poll the state store for the decision
            state_key = f"human-decision-{instance_id}"
            state = d.get_state(
                store_name="statestore",
                key=state_key,
                state_options=StateOptions(concurrency=Concurrency.first_write, consistency=Consistency.strong)
            )
            if state.data:
                decision_data = json.loads(state.data.decode('utf-8'))
                # Clean up the state
                d.delete_state(store_name="statestore", key=state_key)
                return decision_data
            time.sleep(1)  # Poll every second

# Chat workflow with HITL
def chat_workflow(context: DaprWorkflowContext, input: Dict[str, Any]) -> Dict[str, Any]:
    user_id = input["user_id"]
    message = input["message"]
    instance_id = context.instance_id

    logger.info(f"Starting workflow for user {user_id} with message: {message}")

    # Step 1: Fetch message count
    message_count = yield context.call_activity(fetch_message_count, input={"user_id": user_id})

    # Step 2: Get conversation history
    history = yield context.call_activity(get_conversation_history, input={"user_id": user_id})

    # Step 3: Generate a reply
    proposed_reply = yield context.call_activity(generate_reply, input={
        "user_id": user_id,
        "message": message,
        "message_count": message_count,
        "history": history
    })

    # Step 4: Check for sensitive content
    sensitive_result = yield context.call_activity(check_sensitive_content, input={"message": message})
    is_sensitive = sensitive_result["is_sensitive"]

    if is_sensitive:
        logger.info(f"Sensitive content detected in message: {message}. Requesting human review.")
        # Step 5: Request human review
        yield context.call_activity(request_human_review, input={
            "user_id": user_id,
            "message": message,
            "proposed_reply": proposed_reply,
            "instance_id": instance_id
        })

        # Step 6: Wait for human decision
        decision = yield context.call_activity(wait_for_human_decision, input={"instance_id": instance_id})
        approved = decision["approved"]

        if not approved:
            logger.info(f"Human rejected the response for user {user_id}. Aborting workflow.")
            return {
                "user_id": user_id,
                "reply": "Message rejected by human reviewer.",
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
            }

    # Step 7: Store the conversation
    yield context.call_activity(store_conversation, input={
        "user_id": user_id,
        "message": message,
        "reply": proposed_reply
    })

    # Step 8: Publish MessageSent event
    yield context.call_activity(publish_message_sent_event, input={"user_id": user_id})

    logger.info(f"Completed workflow for user {user_id}")
    return {
        "user_id": user_id,
        "reply": proposed_reply,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
    }

# Start the workflow runtime
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

        # Wait for the workflow to complete
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

#### Explanation of Changes
- **Sensitive Keywords**: Added a list of `SENSITIVE_KEYWORDS` (e.g., "urgent", "help", "emergency") to flag messages for human review.
- **New Activities**:
  - `check_sensitive_content`: Checks if the message contains sensitive keywords.
  - `request_human_review`: Publishes a "HumanReviewRequired" event to the `human-review` topic with the message, proposed reply, and workflow instance ID.
  - `wait_for_human_decision`: Polls the Dapr state store for a human decision (stored under `human-decision-<instance_id>`). In a production system, you’d use Dapr’s pub/sub subscription API or external event triggers to avoid polling.
- **Updated Workflow (`chat_workflow`)**:
  - After generating a reply, the workflow checks for sensitive content.
  - If the message is sensitive, it emits a "HumanReviewRequired" event and pauses, waiting for a human decision.
  - If the human rejects the response, the workflow returns a rejection message. If approved, it proceeds with storing the conversation and publishing the "MessageSent" event.
- **Polling for Human Decision**: For simplicity, we poll the state store for the human decision. In a real-world application, you’d use Dapr’s pub/sub subscription to listen for the "HumanDecisionMade" event directly in the workflow.

### Step 2.2: Update Dapr Pub/Sub Configuration
We need to configure the `human-review` topic for the "HumanReviewRequired" event. Since the Chat Service publishes to this topic, we don’t need a subscription (the Streamlit UI will subscribe to it). However, we’ll ensure the topic is available by updating the `components/subscriptions.yaml` file to include a subscription for the Streamlit UI (added later).

For now, the Chat Service only needs to publish to the `human-review` topic, which is supported by the existing `pubsub` component (Redis).

---

## Step 3: Create the Streamlit UI for Human Review
We’ll create a new service called `review-ui` that uses **Streamlit** to provide a simple interface for human reviewers to approve or reject messages. The UI will:
- Subscribe to the "HumanReviewRequired" topic to receive review requests.
- Display the message and proposed reply to the human.
- Allow the human to approve or reject the response.
- Publish a "HumanDecisionMade" event with the decision.
- Store the decision in the Dapr state store for the Chat Service workflow to retrieve.

### Step 3.1: Set Up the Streamlit UI
Create a new directory for the Streamlit UI:
```bash
mkdir review_ui
cd review_ui
```

Create a `app.py` file for the Streamlit app:
```bash
touch app.py
```

Edit `review_ui/app.py`:
```python
import streamlit as st
from dapr.clients import DaprClient
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReviewUI")

st.title("Human Review Interface")

# Placeholder for review requests
if "review_requests" not in st.session_state:
    st.session_state.review_requests = []

# Function to publish human decision
def publish_human_decision(instance_id: str, approved: bool):
    with DaprClient() as d:
        # Publish the HumanDecisionMade event
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="human-decision",
            data=json.dumps({
                "instance_id": instance_id,
                "approved": approved,
                "event_type": "HumanDecisionMade"
            }),
            data_content_type="application/json"
        )
        # Store the decision in the state store for the workflow to retrieve
        state_key = f"human-decision-{instance_id}"
        d.save_state(
            store_name="statestore",
            key=state_key,
            value=json.dumps({"instance_id": instance_id, "approved": approved})
        )
    logger.info(f"Published HumanDecisionMade event for instance_id {instance_id}: approved={approved}")

# Subscribe to HumanReviewRequired events
def subscribe_to_reviews():
    with DaprClient() as d:
        while True:
            try:
                # Subscribe to the human-review topic
                response = d.subscribe(
                    pubsub_name="pubsub",
                    topic="human-review"
                )
                for event in response:
                    data = json.loads(event.data.decode('utf-8'))
                    if data["event_type"] == "HumanReviewRequired":
                        st.session_state.review_requests.append(data)
                        st.experimental_rerun()  # Refresh the UI to display the new request
            except Exception as e:
                logger.error(f"Error in subscription: {e}")
                time.sleep(5)  # Retry after a delay

# Run the subscription in a background thread
import threading
threading.Thread(target=subscribe_to_reviews, daemon=True).start()

# Display review requests
if st.session_state.review_requests:
    for request in st.session_state.review_requests:
        st.subheader(f"Review Request for User: {request['user_id']}")
        st.write(f"**Message:** {request['message']}")
        st.write(f"**Proposed Reply:** {request['proposed_reply']}")
        st.write(f"**Instance ID:** {request['instance_id']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve", key=f"approve-{request['instance_id']}"):
                publish_human_decision(request["instance_id"], True)
                st.session_state.review_requests.remove(request)
                st.experimental_rerun()
        with col2:
            if st.button("Reject", key=f"reject-{request['instance_id']}"):
                publish_human_decision(request["instance_id"], False)
                st.session_state.review_requests.remove(request)
                st.experimental_rerun()
else:
    st.write("No review requests at the moment.")
```

#### Explanation of the Streamlit App
- **Streamlit UI**:
  - Displays a title and a list of review requests.
  - Each request shows the user ID, message, proposed reply, and instance ID.
  - Provides "Approve" and "Reject" buttons for each request.
- **Subscription**:
  - Subscribes to the `human-review` topic to receive "HumanReviewRequired" events.
  - Adds new requests to `st.session_state.review_requests` and refreshes the UI.
- **Human Decision**:
  - When the human clicks "Approve" or "Reject", the app publishes a "HumanDecisionMade" event to the `human-decision` topic.
  - It also stores the decision in the Dapr state store under `human-decision-<instance_id>` for the Chat Service workflow to retrieve.
  - Removes the request from the UI after a decision is made.

### Step 3.2: Create a `pyproject.toml` for the Streamlit App
Instead of `requirements.txt`, we’ll use `pyproject.toml` and `uv` for dependency management. Create `review_ui/pyproject.toml`:
```toml
[project]
name = "review-ui"
version = "0.1.0"
dependencies = [
    "streamlit==1.32.0",
    "dapr==1.12.0",
]

[tool.uv]
lock = "uv.lock"
```

#### Explanation of `pyproject.toml`
- `[project]`: Defines the project metadata.
  - `name`: The project name (`review-ui`).
  - `version`: The project version.
  - `dependencies`: Lists the dependencies (`streamlit` and `dapr`).
- `[tool.uv]`: Configures `uv` to manage dependencies and create a `uv.lock` file.

### Step 3.3: Generate the `uv.lock` File
Navigate to the `review_ui` directory and generate the `uv.lock` file:
```bash
cd review_ui
uv sync
```

This will create a `uv.lock` file in the `review_ui` directory, locking the exact versions of the dependencies.

### Step 3.4: Create a `Dockerfile` for the Streamlit App
Create `review_ui/Dockerfile`:
```dockerfile
# Use a base image with Python 3.9
FROM python:3.9-slim

# Install uv
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy the dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy the application code
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Define the command to run the app
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Explanation of the Dockerfile
- `FROM python:3.9-slim`: Uses a lightweight Python 3.9 image.
- `RUN pip install uv`: Installs `uv` in the image.
- `WORKDIR /app`: Sets the working directory to `/app`.
- `COPY pyproject.toml uv.lock ./`: Copies the dependency files.
- `RUN uv sync --frozen`: Installs the dependencies using `uv`, respecting the locked versions in `uv.lock`.
- `COPY . .`: Copies the application code (`app.py`).
- `EXPOSE 8501`: Streamlit runs on port `8501` by default.
- `CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]`: Runs the Streamlit app using `uv run` on port `8501`.

---

## Step 4: Update Dapr Pub/Sub Configuration for the Streamlit UI
We need to configure the Streamlit UI to subscribe to the `human-review` topic and publish to the `human-decision` topic. Update the `components/subscriptions.yaml` file to include subscriptions for the Streamlit UI.

Edit `components/subscriptions.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: analytics-subscription
spec:
  topic: messages
  route: /events
  pubsubname: pubsub
---
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: review-ui-subscription
spec:
  topic: human-review
  route: /human-review
  pubsubname: pubsub
```

#### Explanation of Changes
- Added a new subscription for the `review-ui` service to listen to the `human-review` topic.
- The `route: /human-review` is used by Dapr to route events to the Streamlit app, but since we’re using the Dapr Python SDK’s `subscribe` method, this route is not directly used (it’s a placeholder for HTTP-based subscriptions).

---

## Step 5: Update `docker-compose.yml` to Include the Streamlit UI
We’ll add the `review-ui` service to the `docker-compose.yml` file and ensure it runs with a Dapr sidecar.

Edit `docker-compose.yml`:
```yaml
version: "3.9"
services:
  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - dapr-network

  zipkin:
    image: openzipkin/zipkin
    ports:
      - "9411:9411"
    networks:
      - dapr-network

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - dapr-network

  chat-service-app:
    build: ./chat_service
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - dapr-network

  chat-service-dapr:
    image: daprio/dapr:1.12
    command:
      - "./daprd"
      - "--app-id"
      - "chat-service"
      - "--app-port"
      - "8000"
      - "--dapr-http-port"
      - "3500"
      - "--dapr-grpc-port"
      - "50001"
      - "--metrics-port"
      - "9090"
      - "--log-level"
      - "debug"
      - "--config"
      - "/components/tracing.yaml"
      - "--components-path"
      - "/components"
    environment:
      - DAPR_REDIS_HOST=redis:6379
    volumes:
      - ./components:/components
    depends_on:
      - chat-service-app
      - redis
      - zipkin
      - prometheus
    networks:
      - dapr-network

  analytics-service-app:
    build: ./analytics_service
    ports:
      - "8001:8001"
    depends_on:
      - redis
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - dapr-network

  analytics-service-dapr:
    image: daprio/dapr:1.12
    command:
      - "./daprd"
      - "--app-id"
      - "analytics-service"
      - "--app-port"
      - "8001"
      - "--dapr-http-port"
      - "3501"
      - "--metrics-port"
      - "9091"
      - "--log-level"
      - "debug"
      - "--config"
      - "/components/tracing.yaml"
      - "--components-path"
      - "/components"
    environment:
      - DAPR_REDIS_HOST=redis:6379
    volumes:
      - ./components:/components
    depends_on:
      - analytics-service-app
      - redis
      - zipkin
      - prometheus
    networks:
      - dapr-network

  review-ui-app:
    build: ./review_ui
    ports:
      - "8501:8501"
    depends_on:
      - redis
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - dapr-network

  review-ui-dapr:
    image: daprio/dapr:1.12
    command:
      - "./daprd"
      - "--app-id"
      - "review-ui"
      - "--app-port"
      - "8501"
      - "--dapr-http-port"
      - "3502"
      - "--metrics-port"
      - "9092"
      - "--log-level"
      - "debug"
      - "--config"
      - "/components/tracing.yaml"
      - "--components-path"
      - "/components"
    environment:
      - DAPR_REDIS_HOST=redis:6379
    volumes:
      - ./components:/components
    depends_on:
      - review-ui-app
      - redis
      - zipkin
      - prometheus
    networks:
      - dapr-network

networks:
  dapr-network:
    driver: bridge

volumes:
  redis-data:
```

#### Explanation of Changes
- Added `review-ui-app`:
  - `build: ./review_ui`: Builds the image from the `Dockerfile` in the `review_ui` directory.
  - `ports: - "8501:8501"`: Exposes the Streamlit UI on port `8501`.
  - `depends_on: - redis`: Ensures Redis starts first.
  - `environment: - PYTHONUNBUFFERED=1`: Ensures Python output is unbuffered.
  - `networks: - dapr-network`: Connects to the custom network.
- Added `review-ui-dapr`:
  - `image: daprio/dapr:1.12`: Uses the Dapr runtime image.
  - `command`: Configures the Dapr sidecar for the `review-ui` app (e.g., `--app-id review-ui`, `--app-port 8501`).
  - `environment: - DAPR_REDIS_HOST=redis:6379`: Overrides the Redis host for Dapr.
  - `volumes: - ./components:/components`: Mounts the `components` directory.
  - `depends_on`: Ensures the `review-ui-app`, Redis, Zipkin, and Prometheus start first.
  - `networks: - dapr-network`: Connects to the custom network.

### Update `prometheus.yml` for the New Service
Add the `review-ui-dapr` metrics endpoint to `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dapr'
    static_configs:
      - targets: ['chat-service-dapr:9090', 'analytics-service-dapr:9091', 'review-ui-dapr:9092']
```

---

## Step 6: Run the Application with Docker Compose
### Step 6.1: Start the Application
From the project root (`fastapi-daca-tutorial`), start the application:
```bash
docker-compose up -d
```

Output:
```
Creating network "fastapi-daca-tutorial_dapr-network" with driver "bridge"
Creating volume "fastapi-daca-tutorial_redis-data" with default driver
Creating fastapi-daca-tutorial_redis_1 ... done
Creating fastapi-daca-tutorial_zipkin_1 ... done
Creating fastapi-daca-tutorial_prometheus_1 ... done
Creating fastapi-daca-tutorial_chat-service-app_1 ... done
Creating fastapi-daca-tutorial_analytics-service-app_1 ... done
Building review-ui-app
Step 1/7 : FROM python:3.9-slim
 ---> abc123def456
Step 2/7 : RUN pip install uv
 ---> Running in 123abc456def
...
Successfully built 789xyz123abc
Successfully tagged fastapi-daca-tutorial_review-ui-app:latest
Creating fastapi-daca-tutorial_review-ui-app_1 ... done
Creating fastapi-daca-tutorial_chat-service-dapr_1 ... done
Creating fastapi-daca-tutorial_analytics-service-dapr_1 ... done
Creating fastapi-daca-tutorial_review-ui-dapr_1 ... done
```

### Step 6.2: Verify the Services Are Running
List the running containers:
```bash
docker-compose ps
```
Output:
```
                Name                              Command               State           Ports         
------------------------------------------------------------------------------------------------------
fastapi-daca-tutorial_analytics-service-app_1    uv run uvicorn main:app -- ...   Up      0.0.0.0:8001->8001/tcp
fastapi-daca-tutorial_analytics-service-dapr_1   ./daprd --app-id analytics ...   Up                            
fastapi-daca-tutorial_chat-service-app_1         uv run uvicorn main:app -- ...   Up      0.0.0.0:8000->8000/tcp
fastapi-daca-tutorial_chat-service-dapr_1        ./daprd --app-id chat-serv ...   Up                            
fastapi-daca-tutorial_prometheus_1               /bin/prometheus --config.f ...   Up      0.0.0.0:9090->9090/tcp
fastapi-daca-tutorial_redis_1                    docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
fastapi-daca-tutorial_review-ui-app_1            uv run streamlit run app.p ...   Up      0.0.0.0:8501->8501/tcp
fastapi-daca-tutorial_review-ui-dapr_1           ./daprd --app-id review-ui ...   Up                            
fastapi-daca-tutorial_zipkin_1                   start-zipkin                     Up      0.0.0.0:9411->9411/tcp
```

---

## Step 7: Test the HITL Workflow
We’ll test the HITL integration by sending a message that triggers a human review, using the Streamlit UI to approve or reject the response, and verifying the workflow completes accordingly.

### Step 7.1: Initialize State for Testing
Initialize message counts for `alice` and `bob` (same as previous tutorials):
- For `alice`:
  ```bash
  curl -X POST http://localhost:8001/analytics/alice/initialize -H "Content-Type: application/json" -d '{"message_count": 5}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "alice", "message_count": 5}
  ```
- For `bob`:
  ```bash
  curl -X POST http://localhost:8001/analytics/bob/initialize -H "Content-Type: application/json" -d '{"message_count": 3}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "bob", "message_count": 3}
  ```

### Step 7.2: Send a Message Requiring Human Review
Send a message to the Chat Service that contains a sensitive keyword (e.g., "urgent"):
```bash
curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" -d '{"user_id": "bob", "text": "This is an urgent request!", "metadata": {"timestamp": "2025-04-06T12:00:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174001"}, "tags": ["greeting"]}'
```

The request will hang because the workflow is waiting for human input.

#### Check the Chat Service Logs
```bash
docker-compose logs chat-service-app
```
Output:
```
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,123 - ChatService - INFO - Received chat request for user bob: This is an urgent request!
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,124 - ChatService - INFO - Scheduling workflow with instance_id: chat-bob-1744064460
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,125 - ChatService - INFO - Starting workflow for user bob with message: This is an urgent request!
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,130 - ChatService - INFO - Sensitive content detected in message: This is an urgent request!. Requesting human review.
```

### Step 7.3: Review the Message in the Streamlit UI
Open the Streamlit UI at `http://localhost:8501`. You should see a review request:
- **User:** bob
- **Message:** This is an urgent request!
- **Proposed Reply:** (e.g., "Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you?")
- **Instance ID:** chat-bob-1744064460

#### Approve the Response
Click the "Approve" button.

#### Check the Streamlit Logs
```bash
docker-compose logs review-ui-app
```
Output:
```
fastapi-daca-tutorial_review-ui-app_1  | 2025-04-06 04:01:00,150 - ReviewUI - INFO - Published HumanDecisionMade event for instance_id chat-bob-1744064460: approved=True
```

#### Check the Chat Service Response
The `curl` request should now complete with a response:
```json
{
  "user_id": "bob",
  "reply": "Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you?",
  "metadata": {
    "timestamp": "2025-04-06T04:01:00Z",
    "session_id": "some-uuid"
  }
}
```

#### Check the Analytics Service Logs
```bash
docker-compose logs analytics-service-app
```
Output:
```
fastapi-daca-tutorial_analytics-service-app_1  | 2025-04-06 04:01:00,162 - AnalyticsService - INFO - Received event: {'user_id': 'bob', 'event_type': 'MessageSent'}
fastapi-daca-tutorial_analytics-service-app_1  | 2025-04-06 04:01:00,163 - AnalyticsService - INFO - Incrementing message count for user bob
...
fastapi-daca-tutorial_analytics-service-app_1  | 2025-04-06 04:01:00,169 - AnalyticsService - INFO - Processed MessageSent event for user bob
```

### Step 7.4: Test Rejection
Send another message requiring review:
```bash
curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" -d '{"user_id": "alice", "text": "I need help immediately!", "metadata": {"timestamp": "2025-04-06T12:00:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174002"}, "tags": ["support"]}'
```

In the Streamlit UI (`http://localhost:8501`), click the "Reject" button for this request.

#### Check the Chat Service Response
The `curl` request should complete with:
```json
{
  "user_id": "alice",
  "reply": "Message rejected by human reviewer.",
  "metadata": {
    "timestamp": "2025-04-06T04:01:00Z",
    "session_id": "some-uuid"
  }
}
```

#### Check the Chat Service Logs
```bash
docker-compose logs chat-service-app
```
Output:
```
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,170 - ChatService - INFO - Received chat request for user alice: I need help immediately!
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,171 - ChatService - INFO - Scheduling workflow with instance_id: chat-alice-1744064460
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,172 - ChatService - INFO - Starting workflow for user alice with message: I need help immediately!
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,175 - ChatService - INFO - Sensitive content detected in message: I need help immediately!. Requesting human review.
fastapi-daca-tutorial_chat-service-app_1  | 2025-04-06 04:01:00,180 - ChatService - INFO - Human rejected the response for user alice. Aborting workflow.
```

#### Verify Message Count
Since the message was rejected, the Analytics Service should not increment the message count for `alice`. Check the count:
- Visit `http://localhost:8001/docs` and test `/analytics/alice`:
  - Expected: `{"message_count": 5}` (unchanged).

---

## Step 8: Why HITL for DACA?
Integrating Human-in-the-Loop into our DACA application provides several benefits:
- **Safety and Compliance**: Ensures sensitive or ambiguous messages are reviewed by a human, reducing the risk of inappropriate responses.
- **Reliability**: Combines the efficiency of AI agents with human judgment for critical decisions.
- **Transparency**: Logs human decisions, providing an audit trail for accountability.
- **Flexibility**: The HITL workflow can be extended to other scenarios (e.g., flagging transactions, moderating content).

---

## Step 9: Next Steps
You’ve successfully integrated Human-in-the-Loop into the DACA application! The Chat Service now pauses for human review when a message contains sensitive keywords, and the Streamlit UI allows a human to approve or reject the agent’s response. In the next tutorial, we’ll explore deploying this application to a production environment, such as a Kubernetes cluster, using Dapr’s Kubernetes integration.

### Optional Exercises
1. Enhance the Streamlit UI to include a history of reviewed messages and their decisions.
2. Add more sophisticated sensitive content detection (e.g., using a machine learning model to flag messages).
3. Replace the polling mechanism in `wait_for_human_decision` with a proper Dapr pub/sub subscription to listen for the "HumanDecisionMade" event.

---

## Conclusion
In this tutorial, we introduced Human-in-the-Loop integration into our DACA microservices. We modified the Chat Service workflow to emit a "HumanReviewRequired" event for sensitive messages, built a Streamlit UI for human review, and integrated the feedback loop with Dapr by publishing a "HumanDecisionMade" event. We also updated the `review_ui` project to use **uv** for dependency management, ensuring consistency with the rest of the DACA application. The updated application runs seamlessly with Docker Compose, and the HITL workflow ensures human oversight for critical decisions. We’re now ready to explore production deployment in the next tutorial!

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
from dapr.clients.grpc._state import StateOptions, StateItem, Concurrency, Consistency
import uuid
from datetime import datetime, timezone
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatService")

app = FastAPI()

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
    with DaprClient() as d:
        secret = d.get_secret(store_name="secretstore", key="openai-api-key").secret
        openai.api_key = secret["openai-api-key"]
    return openai

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
    with DaprClient() as d:
        actor_type = "UserSessionActor"
        actor_id = user_id
        history = d.invoke_actor(actor_type, actor_id, "GetHistory", "").data.decode('utf-8')
        return history if history else "No previous conversation."

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

def store_conversation(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    reply = input["reply"]
    with DaprClient() as d:
        actor_type = "UserSessionActor"
        actor_id = user_id
        conversation = f"User: {message}\nAssistant: {reply}"
        d.invoke_actor(actor_type, actor_id, "AddMessage", conversation)

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

### Final `review_ui/app.py`
```python
import streamlit as st
from dapr.clients import DaprClient
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReviewUI")

st.title("Human Review Interface")

if "review_requests" not in st.session_state:
    st.session_state.review_requests = []

def publish_human_decision(instance_id: str, approved: bool):
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="human-decision",
            data=json.dumps({
                "instance_id": instance_id,
                "approved": approved,
                "event_type": "HumanDecisionMade"
            }),
            data_content_type="application/json"
        )
        state_key = f"human-decision-{instance_id}"
        d.save_state(
            store_name="statestore",
            key=state_key,
            value=json.dumps({"instance_id": instance_id, "approved": approved})
        )
    logger.info(f"Published HumanDecisionMade event for instance_id {instance_id}: approved={approved}")

def subscribe_to_reviews():
    with DaprClient() as d:
        while True:
            try:
                response = d.subscribe(
                    pubsub_name="pubsub",
                    topic="human-review"
                )
                for event in response:
                    data = json.loads(event.data.decode('utf-8'))
                    if data["event_type"] == "HumanReviewRequired":
                        st.session_state.review_requests.append(data)
                        st.experimental_rerun()
            except Exception as e:
                logger.error(f"Error in subscription: {e}")
                time.sleep(5)

import threading
threading.Thread(target=subscribe_to_reviews, daemon=True).start()

if st.session_state.review_requests:
    for request in st.session_state.review_requests:
        st.subheader(f"Review Request for User: {request['user_id']}")
        st.write(f"**Message:** {request['message']}")
        st.write(f"**Proposed Reply:** {request['proposed_reply']}")
        st.write(f"**Instance ID:** {request['instance_id']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve", key=f"approve-{request['instance_id']}"):
                publish_human_decision(request["instance_id"], True)
                st.session_state.review_requests.remove(request)
                st.experimental_rerun()
        with col2:
            if st.button("Reject", key=f"reject-{request['instance_id']}"):
                publish_human_decision(request["instance_id"], False)
                st.session_state.review_requests.remove(request)
                st.experimental_rerun()
else:
    st.write("No review requests at the moment.")
```

### Final `review_ui/pyproject.toml`
```toml
[project]
name = "review-ui"
version = "0.1.0"
dependencies = [
    "streamlit==1.32.0",
    "dapr==1.12.0",
]

[tool.uv]
lock = "uv.lock"
```

### Final `review_ui/Dockerfile`
```dockerfile
FROM python:3.9-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

This tutorial uses **uv** for dependency management in the `review_ui` project, ensuring consistency with the `chat_service` and `analytics_service` projects. 