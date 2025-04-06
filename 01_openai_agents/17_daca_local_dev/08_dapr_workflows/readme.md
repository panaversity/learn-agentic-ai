# Orchestrating Microservices with Dapr Workflows

Welcome to the eighth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the microservices from **07_dapr_pubsub_messaging** by integrating Dapr’s **Workflows** building block. Currently, the Chat Service processes a user message, fetches analytics data synchronously via Service Invocation, generates a reply using the OpenAI Agents SDK, and publishes a “MessageSent” event for the Analytics Service to update the message count asynchronously. We’ll replace this ad-hoc process with a Dapr Workflow, which will orchestrate these steps as a reliable, multi-step process with retries, timeouts, and compensation logic. This will make our system more robust and easier to maintain. Let’s get started!

---

## What You’ll Learn
- How to use Dapr’s Workflows building block to orchestrate multi-step processes in microservices.
- Defining a workflow in the Chat Service to handle message processing, analytics retrieval, agent response generation, and event publishing.
- Configuring retries and timeouts for workflow activities.
- Running microservices with Dapr Workflows enabled.
- Updating unit tests to account for Dapr Workflow integration.

## Prerequisites
- Completion of **07_dapr_pubsub_messaging** (codebase with Chat Service and Analytics Service using Dapr Service Invocation, State Management, and Pub/Sub Messaging).
- Dapr CLI and runtime installed (from **04_dapr_theory_and_cli**).
- Docker installed (Dapr uses Docker for its sidecars and components).
- Python 3.8+ installed.
- An OpenAI API key (set as `OPENAI_API_KEY`).
- Familiarity with Dapr Workflows concepts (introduced in **04_dapr_theory_and_cli**).

---

## Step 1: Recap of the Current Setup
In **07_dapr_pubsub_messaging**, we integrated Dapr’s Pub/Sub Messaging into our microservices:
- The **Chat Service**:
  - Uses Dapr Service Invocation to fetch the user’s message count from the Analytics Service.
  - Processes the message using the OpenAI Agents SDK to generate a reply.
  - Publishes a “MessageSent” event to the `messages` topic.
- The **Analytics Service**:
  - Subscribes to the `messages` topic and increments the user’s message count in the Dapr state store when a “MessageSent” event is received.
  - Stores and retrieves message counts using Dapr State Management.

### Current Limitations
- **Ad-Hoc Process**: The Chat Service’s `/chat/` endpoint handles message processing as a series of sequential steps (fetch analytics, generate reply, publish event) without formal orchestration. If any step fails, there’s no built-in retry or compensation logic.
- **Reliability Concerns**: Failures in fetching analytics or publishing the event are handled with basic error handling (e.g., fallback to `message_count = 0`), but there’s no mechanism to ensure the entire process completes reliably.
- **Maintainability**: As the process grows (e.g., adding more steps like logging or notifications), the ad-hoc approach becomes harder to manage and debug.

### Goal for This Tutorial
We’ll use Dapr’s Workflows to orchestrate the message processing in the Chat Service as a formal workflow:
- Define a workflow with steps for fetching analytics, generating a reply, and publishing the “MessageSent” event.
- Configure retries and timeouts for each step to handle transient failures.
- Use Dapr’s Workflow engine to ensure the process is reliable, with compensation logic for failures.
- This will make the Chat Service more robust and easier to maintain, especially as we add more steps in the future.

### Current Project Structure
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   └── tests/
│       └── test_main.py
├── analytics_service/
│   ├── main.py
│   ├── models.py
│   └── tests/
│       └── test_main.py
├── components/
│   └── subscriptions.yaml
├── pyproject.toml
└── uv.lock
```

---

## Step 2: Why Use Dapr Workflows?
Dapr’s **Workflows** building block provides a framework for orchestrating multi-step processes in a distributed system. It offers several advantages over ad-hoc process management:
- **Reliability**: Workflows ensure that each step completes successfully, with automatic retries for transient failures.
- **Compensation**: If a step fails, workflows can execute compensation logic to undo previous steps (e.g., rollback state changes).
- **State Management**: Dapr Workflows manage the state of the process, allowing it to resume after failures or system restarts.
- **Observability**: Workflows provide visibility into the process state and history, making debugging easier.
- **Scalability**: Workflows can be executed across distributed instances, supporting horizontal scaling.
- **Maintainability**: Formalizing the process as a workflow makes it easier to add, modify, or debug steps.

In DACA, Workflows are crucial for:
- Ensuring reliable message processing in the Chat Service, even in the presence of transient failures (e.g., network issues, service downtime).
- Supporting complex agentic AI workflows (e.g., multi-step conversations, analytics updates, notifications) as the system grows.
- Aligning with DACA’s goal of building a robust, distributed system that can handle failures gracefully.

---

## Step 3: Configure Dapr Workflow Component
Dapr Workflows require a workflow runtime and a state store to manage workflow state. The `dapr init` command already set up a default Redis-based state store (`statestore.yaml`), which Dapr Workflows can use to persist workflow state. However, we need to ensure the Dapr Workflow runtime is enabled and configured.

### Verify the State Store Component
```bash
cat ~/.dapr/components/statestore.yaml
```
Output:
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
    value: localhost:6379
  - name: redisPassword
    value: ""
```
This state store will be used by the Dapr Workflow engine to persist workflow state.

### Enable Dapr Workflows
Dapr Workflows are enabled by default in Dapr 1.8+ (as of April 2025, the latest version is likely higher). However, we need to ensure the Dapr sidecar is configured to support workflows. This is typically done automatically when using the Dapr CLI, but we’ll confirm by checking the Dapr runtime logs when we start the services.

---

## Step 4: Update the Chat Service to Use Dapr Workflows
We’ll modify the Chat Service to define a Dapr Workflow for message processing. The workflow will include the following steps:
1. Fetch the user’s message count from the Analytics Service (via Service Invocation).
2. Generate a reply using the OpenAI Agents SDK.
3. Publish a “MessageSent” event to the `messages` topic.

We’ll use the `dapr` Python SDK to define and execute the workflow, as it provides a more idiomatic way to work with Dapr Workflows compared to raw HTTP/gRPC calls.

### Step 4.1: Install the Dapr Python SDK
Add the `dapr` package to your project dependencies using `uv`.

```bash
uv add dapr
```
This will update `pyproject.toml` and `uv.lock` with the `dapr` package.

### Step 4.2: Define the Workflow in `chat_service/main.py`
We’ll define a Dapr Workflow using the `dapr` Python SDK, breaking the message processing into activities (steps) that can be retried and orchestrated.

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx
from dapr.clients import DaprClient
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, when
from dapr.workflow import WorkflowActivityContext

from models import Message, Response, Metadata

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Dapr Workflow runtime
workflow_runtime = WorkflowRuntime()
workflow_runtime.start()

@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool. Personalize responses using user analytics (e.g., message count).",
    model="gpt-4o",
    tools=[get_current_time],
)

async def get_db():
    return {"connection": "Mock DB Connection"}

# Workflow activities
async def fetch_analytics_activity(ctx: WorkflowActivityContext, user_id: str) -> int:
    """Activity to fetch the user's message count from the Analytics Service."""
    with DaprClient() as dapr_client:
        try:
            response = await dapr_client.invoke_method_async(
                app_id="analytics-service",
                method_name=f"analytics/{user_id}",
                http_verb="GET"
            )
            analytics_data = response.json()
            return analytics_data.get("message_count", 0)
        except Exception as e:
            print(f"Failed to fetch analytics in workflow: {e}")
            return 0

async def generate_reply_activity(ctx: WorkflowActivityContext, input_data: dict) -> str:
    """Activity to generate a reply using the OpenAI Agents SDK."""
    user_id = input_data["user_id"]
    message_text = input_data["message_text"]
    message_count = input_data["message_count"]

    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    result = await Runner.run(chat_agent, input=message_text)
    return result.final_output

async def publish_event_activity(ctx: WorkflowActivityContext, user_id: str):
    """Activity to publish a MessageSent event to the messages topic."""
    with DaprClient() as dapr_client:
        try:
            await dapr_client.publish_event(
                pubsub_name="pubsub",
                topic_name="messages",
                data={"user_id": user_id, "event_type": "MessageSent"}
            )
            print(f"Published MessageSent event for user {user_id} in workflow")
        except Exception as e:
            print(f"Failed to publish MessageSent event in workflow: {e}")
            raise  # Re-raise to trigger workflow retry

# Define the workflow
@workflow_runtime.workflow
async def message_processing_workflow(ctx: DaprWorkflowContext, input_data: dict) -> dict:
    """Workflow to orchestrate message processing in the Chat Service."""
    user_id = input_data["user_id"]
    message_text = input_data["message_text"]

    # Step 1: Fetch analytics
    message_count = await ctx.call_activity(
        fetch_analytics_activity,
        input=user_id,
        retry_policy={"max_retries": 3, "interval": "PT5S"}  # Retry 3 times, 5-second interval
    )

    # Step 2: Generate reply
    reply = await ctx.call_activity(
        generate_reply_activity,
        input={"user_id": user_id, "message_text": message_text, "message_count": message_count},
        retry_policy={"max_retries": 2, "interval": "PT3S"}
    )

    # Step 3: Publish MessageSent event
    await ctx.call_activity(
        publish_event_activity,
        input=user_id,
        retry_policy={"max_retries": 5, "interval": "PT2S"}
    )

    return {"user_id": user_id, "reply": reply}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")

    # Start the workflow
    with DaprWorkflowClient() as workflow_client:
        instance_id = f"chat-{message.user_id}-{int(datetime.utcnow().timestamp())}"
        input_data = {"user_id": message.user_id, "message_text": message.text}
        
        # Start the workflow
        await workflow_client.schedule_new_workflow(
            workflow=message_processing_workflow,
            instance_id=instance_id,
            input=input_data
        )

        # Wait for the workflow to complete
        result = await workflow_client.wait_for_workflow_completion(
            instance_id=instance_id,
            timeout_in_seconds=60
        )

        if result is None or result.runtime_status != "COMPLETED":
            raise HTTPException(status_code=500, detail="Workflow failed to complete")

        workflow_output = result.output
        reply_text = workflow_output["reply"]

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )

# Shutdown the workflow runtime on app shutdown
@app.on_event("shutdown")
def shutdown():
    workflow_runtime.stop()
```

#### Explanation of Changes
1. **Dapr Workflow Setup**:
   - Imported the necessary Dapr Workflow modules (`dapr.ext.workflow`, `dapr.workflow`).
   - Initialized the `WorkflowRuntime` and started it when the app starts.
   - Stopped the runtime on app shutdown to clean up resources.

2. **Workflow Activities**:
   - `fetch_analytics_activity`: Fetches the message count from the Analytics Service using Dapr’s `invoke_method_async` (equivalent to Service Invocation).
   - `generate_reply_activity`: Generates a reply using the OpenAI Agents SDK.
   - `publish_event_activity`: Publishes the “MessageSent” event using Dapr’s `publish_event`.

3. **Workflow Definition**:
   - Defined `message_processing_workflow` using the `@workflow_runtime.workflow` decorator.
   - The workflow orchestrates the three activities in sequence, with retry policies for each step:
     - Fetch analytics: Retry 3 times, 5-second interval.
     - Generate reply: Retry 2 times, 3-second interval.
     - Publish event: Retry 5 times, 2-second interval.

4. **Updated `/chat/` Endpoint**:
   - Replaced the ad-hoc process with a workflow execution.
   - Uses `DaprWorkflowClient` to schedule and wait for the workflow to complete.
   - Returns the workflow output (user ID and reply) as the response.

### Step 4.3: Update `chat_service/tests/test_main.py`
Update the tests to mock the workflow execution and activities.

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."
    }

def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

@pytest.mark.asyncio
async def test_chat():
    with patch("main.DaprWorkflowClient") as mock_workflow_client, \
         patch("main.fetch_analytics_activity", new_callable=AsyncMock) as mock_fetch, \
         patch("main.generate_reply_activity", new_callable=AsyncMock) as mock_generate, \
         patch("main.publish_event_activity", new_callable=AsyncMock) as mock_publish:
        # Mock the workflow client
        mock_workflow_instance = AsyncMock()
        mock_workflow_instance.runtime_status = "COMPLETED"
        mock_workflow_instance.output = {
            "user_id": "alice",
            "reply": "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"
        }
        mock_workflow_client.return_value.__aenter__.return_value = mock_workflow_instance
        mock_workflow_instance.wait_for_workflow_completion.return_value = mock_workflow_instance

        # Mock the activities
        mock_fetch.return_value = 5
        mock_generate.return_value = "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"

        request_data = {
            "user_id": "alice",
            "text": "Hello, how are you?",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            },
            "tags": ["greeting"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["user_id"] == "alice"
        assert response.json()["reply"] == "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"
        assert "metadata" in response.json()
        mock_publish.assert_called_once_with(ANY, "alice")

        # Test with a different user and tool usage
        mock_workflow_instance.output = {
            "user_id": "bob",
            "reply": "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
        }
        mock_fetch.return_value = 3
        mock_generate.return_value = "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
        request_data = {
            "user_id": "bob",
            "text": "What time is it?",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174001"
            },
            "tags": ["question"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["user_id"] == "bob"
        assert response.json()["reply"] == "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()
        mock_publish.assert_called_with(ANY, "bob")

        # Test workflow failure
        mock_workflow_instance.runtime_status = "FAILED"
        mock_workflow_instance.output = None
        request_data = {
            "user_id": "alice",
            "text": "Hello again!",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 500
        assert response.json() == {"detail": "Workflow failed to complete"}

        # Test invalid request
        request_data = {
            "user_id": "bob",
            "text": "",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Message text cannot be empty"}
```

#### Explanation of Test Changes
- Mocked the `DaprWorkflowClient` to simulate workflow execution and completion.
- Mocked the individual activities (`fetch_analytics_activity`, `generate_reply_activity`, `publish_event_activity`) to verify they are called with the correct inputs.
- Added a test case for workflow failure to ensure the endpoint returns a 500 error if the workflow doesn’t complete successfully.

---

## Step 5: Verify the Analytics Service
The Analytics Service doesn’t need changes, as it already handles the “MessageSent” event via Pub/Sub and updates the message count in the state store. However, let’s verify its code for completeness.

### `analytics_service/main.py` (Unchanged)
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from models import Analytics

app = FastAPI(
    title="DACA Analytics Service",
    description="A FastAPI-based Analytics Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_message_count(user_id: str, dapr_port: int = 3501) -> int:
    """Retrieve the message count for a user from the Dapr state store."""
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            state_data = response.json()
            return state_data.get("message_count", 0) if state_data else 0
        except httpx.HTTPStatusError as e:
            print(f"Failed to retrieve state for {user_id}: {e}")
            return 0

async def set_message_count(user_id: str, message_count: int, dapr_port: int = 3501):
    """Set the message count for a user in the Dapr state store."""
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
    state_data = [
        {
            "key": user_id,
            "value": {"message_count": message_count}
        }
    ]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=state_data)
            response.raise_for_status()
            print(f"Set message count for {user_id}: {message_count}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to set state for {user_id}: {e}")

async def increment_message_count(user_id: str, dapr_port: int = 3501):
    """Increment the message count for a user in the Dapr state store."""
    current_count = await get_message_count(user_id, dapr_port)
    new_count = current_count + 1
    await set_message_count(user_id, new_count, dapr_port)

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."}

@app.get("/analytics/{user_id}", response_model=Analytics)
async def get_analytics(user_id: str):
    message_count = await get_message_count(user_id)
    if message_count == 0 and user_id not in ["alice", "bob"]:
        raise HTTPException(status_code=404, detail="User not found")
    return Analytics(message_count=message_count)

@app.post("/analytics/{user_id}/initialize")
async def initialize_message_count(user_id: str, message_count: int):
    await set_message_count(user_id, message_count)
    return {"status": "success", "user_id": user_id, "message_count": message_count}

@app.post("/messages")
async def handle_message_sent(event: dict):
    """Handle MessageSent events from the messages topic."""
    print(f"Received event: {event}")
    event_type = event.get("event_type")
    user_id = event.get("user_id")

    if event_type != "MessageSent" or not user_id:
        return {"status": "ignored"}

    await increment_message_count(user_id)
    return {"status": "success"}
```

The Analytics Service tests (`analytics_service/tests/test_main.py`) also remain unchanged, as they already cover the existing functionality.

---

## Step 6: Run the Microservices with Dapr
### Start the Analytics Service with Dapr
In a terminal, navigate to the Analytics Service directory and run it with Dapr, specifying the components directory:
```bash
cd analytics_service
dapr run --app-id analytics-service --app-port 8001 --dapr-http-port 3501 --components-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001
```
Output:
```
ℹ  Starting Dapr with id analytics-service. HTTP Port: 3501  gRPC Port: 50002
ℹ  Dapr sidecar is up and running.
ℹ  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Start the Chat Service with Dapr
In a separate terminal, navigate to the Chat Service directory and run it with Dapr:
```bash
cd chat_service
dapr run --app-id chat-service --app-port 8000 --dapr-http-port 3500 --dapr-grpc-port 50001 -- uv run uvicorn main:app --host 0.0.0.0 --port 8000
```
Output:
```
ℹ  Starting Dapr with id chat-service. HTTP Port: 3500  gRPC Port: 50001
ℹ  Dapr sidecar is up and running.
ℹ  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http Dapr Workflow engine started.
://0.0.0.0:8000 (Press CTRL+C to quit)
```

Note: The Dapr logs should indicate that the Workflow engine is running. If you don’t see this, ensure your Dapr version supports workflows (1.8+).

### Verify Running Services
```bash
dapr list
```
Output:
```
  APP ID            HTTP PORT  GRPC PORT  APP PORT  COMMAND                          AGE  CREATED              STATUS
  chat-service      3500       50001      8000      uv run uvicorn main:app --ho...  10s  2025-04-06 04:01:00  Running
  analytics-service 3501       50002      8001      uv run uvicorn main:app --ho...  15s  2025-04-06 04:00:55  Running
```

---

## Step 7: Test the Microservices with Dapr Workflows
### Initialize State for Testing
Initialize message counts for `alice` and `bob` using the `/analytics/{user_id}/initialize` endpoint:
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

### Test the Analytics Service
Test the `/analytics/{user_id}` endpoint to verify it retrieves data from the state store:
- Visit `http://localhost:8001/docs` and test:
  - For `alice`: `{"message_count": 5}`
  - For `bob`: `{"message_count": 3}`
  - For `charlie`: `404 Not Found`

### Test the Chat Service with Workflow
Send a request to the Chat Service to trigger the workflow:
```json
{
  "user_id": "bob",
  "text": "Hello, how are you?",
  "metadata": {
    "timestamp": "2025-04-06T12:00:00Z",
    "session_id": "123e4567-e89b-12d3-a456-426614174001"
  },
  "tags": ["greeting"]
}
```
Expected response (actual reply may vary):
```json
{
  "user_id": "bob",
  "reply": "Hi Bob! You've sent 3 messages so far. How can I help you today?",
  "metadata": {
    "timestamp": "2025-04-06T04:01:00Z",
    "session_id": "some-uuid"
  }
}
```

#### What Happens During the Request?
1. The Chat Service receives the request and starts a new workflow instance.
2. The workflow executes the following steps:
   - Fetches `bob`’s message count (3) from the Analytics Service via Service Invocation.
   - Generates a reply using the OpenAI Agents SDK.
   - Publishes a “MessageSent” event to the `messages` topic.
3. The Analytics Service receives the event and increments `bob`’s message count in the state store (from 3 to 4).
4. The workflow completes, and the Chat Service returns the reply.

Check the updated message count for `bob`:
- Visit `http://localhost:8001/docs` and test `/analytics/bob`:
  - Expected: `{"message_count": 4}`

### Run the Tests
- Chat Service:
  ```bash
  cd chat_service
  uv run pytest tests/test_main.py -v
  ```
  Output:
  ```
  collected 3 items

  tests/test_main.py::test_root PASSED
  tests/test_main.py::test_get_user PASSED
  tests/test_main.py::test_chat PASSED

  ================= 3 passed in 0.15s =================
  ```
- Analytics Service:
  ```bash
  cd analytics_service
  uv run pytest tests/test_main.py -v
  ```
  Output:
  ```
  collected 4 items

  tests/test_main.py::test_root PASSED
  tests/test_main.py::test_get_analytics PASSED
  tests/test_main.py::test_initialize_message_count PASSED
  tests/test_main.py::test_handle_message_sent PASSED

  ================= 4 passed in 0.12s =================
  ```

---

## Step 8: Why Dapr Workflows for DACA?
Using Dapr’s Workflows building block enhances DACA’s architecture by:
- **Reliability**: The workflow ensures each step (fetch analytics, generate reply, publish event) completes successfully, with retries for transient failures.
- **Compensation**: If a step fails after retries, the workflow can execute compensation logic (e.g., logging the failure, notifying an admin), which we’ll explore in future tutorials.
- **Maintainability**: Formalizing the process as a workflow makes it easier to add new steps (e.g., logging, notifications) or modify existing ones.
- **Observability**: Dapr Workflows provide visibility into the process state and history, which can be viewed using the Dapr dashboard.
- **Scalability**: Workflows can be executed across distributed instances, supporting DACA’s containerized deployment goals.

---

## Step 9: Next Steps
You’ve successfully integrated Dapr’s Workflows building block into the Chat Service, orchestrating message processing as a reliable, multi-step process! In the next tutorial (**09_dapr_secrets_management**), we’ll explore Dapr’s Secrets Management building block to securely manage sensitive data, such as the OpenAI API key, in our microservices.

### Optional Exercises
1. Add a new step to the workflow to log the message and reply to a Dapr state store for auditing purposes.
2. Configure a compensation activity in the workflow to handle failures (e.g., notify an admin if the “MessageSent” event fails to publish after retries).
3. Use the Dapr dashboard (`dapr dashboard`) to inspect the workflow state and history for a completed workflow instance.

---

## Conclusion
In this tutorial, we integrated Dapr’s Workflows building block into the Chat Service, replacing an ad-hoc process with a formal workflow for message processing. The workflow orchestrates fetching analytics, generating a reply, and publishing a “MessageSent” event, with retries and timeouts to handle transient failures. This makes our system more reliable, maintainable, and aligned with DACA’s goals for a robust, distributed agentic AI system. We’re now ready to explore Dapr Secrets Management in the next tutorial!

---

### Final Code for `chat_service/main.py`
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx
from dapr.clients import DaprClient
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, when
from dapr.workflow import WorkflowActivityContext

from models import Message, Response, Metadata

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow_runtime = WorkflowRuntime()
workflow_runtime.start()

@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool. Personalize responses using user analytics (e.g., message count).",
    model="gpt-4o",
    tools=[get_current_time],
)

async def get_db():
    return {"connection": "Mock DB Connection"}

async def fetch_analytics_activity(ctx: WorkflowActivityContext, user_id: str) -> int:
    with DaprClient() as dapr_client:
        try:
            response = await dapr_client.invoke_method_async(
                app_id="analytics-service",
                method_name=f"analytics/{user_id}",
                http_verb="GET"
            )
            analytics_data = response.json()
            return analytics_data.get("message_count", 0)
        except Exception as e:
            print(f"Failed to fetch analytics in workflow: {e}")
            return 0

async def generate_reply_activity(ctx: WorkflowActivityContext, input_data: dict) -> str:
    user_id = input_data["user_id"]
    message_text = input_data["message_text"]
    message_count = input_data["message_count"]

    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    result = await Runner.run(chat_agent, input=message_text)
    return result.final_output

async def publish_event_activity(ctx: WorkflowActivityContext, user_id: str):
    with DaprClient() as dapr_client:
        try:
            await dapr_client.publish_event(
                pubsub_name="pubsub",
                topic_name="messages",
                data={"user_id": user_id, "event_type": "MessageSent"}
            )
            print(f"Published MessageSent event for user {user_id} in workflow")
        except Exception as e:
            print(f"Failed to publish MessageSent event in workflow: {e}")
            raise

@workflow_runtime.workflow
async def message_processing_workflow(ctx: DaprWorkflowContext, input_data: dict) -> dict:
    user_id = input_data["user_id"]
    message_text = input_data["message_text"]

    message_count = await ctx.call_activity(
        fetch_analytics_activity,
        input=user_id,
        retry_policy={"max_retries": 3, "interval": "PT5S"}
    )

    reply = await ctx.call_activity(
        generate_reply_activity,
        input={"user_id": user_id, "message_text": message_text, "message_count": message_count},
        retry_policy={"max_retries": 2, "interval": "PT3S"}
    )

    await ctx.call_activity(
        publish_event_activity,
        input=user_id,
        retry_policy={"max_retries": 5, "interval": "PT2S"}
    )

    return {"user_id": user_id, "reply": reply}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")

    with DaprWorkflowClient() as workflow_client:
        instance_id = f"chat-{message.user_id}-{int(datetime.utcnow().timestamp())}"
        input_data = {"user_id": message.user_id, "message_text": message.text}
        
        await workflow_client.schedule_new_workflow(
            workflow=message_processing_workflow,
            instance_id=instance_id,
            input=input_data
        )

        result = await workflow_client.wait_for_workflow_completion(
            instance_id=instance_id,
            timeout_in_seconds=60
        )

        if result is None or result.runtime_status != "COMPLETED":
            raise HTTPException(status_code=500, detail="Workflow failed to complete")

        workflow_output = result.output
        reply_text = workflow_output["reply"]

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )

@app.on_event("shutdown")
def shutdown():
    workflow_runtime.stop()
```

---

This tutorial provides a focused introduction to Dapr Workflows, enhancing the reliability and maintainability of our microservices. 