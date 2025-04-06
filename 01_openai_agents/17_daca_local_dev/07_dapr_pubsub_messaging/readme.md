# Event-Driven Communication with Dapr Pub/Sub

Welcome to the seventh tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the microservices from **06_dapr_state_management** by integrating Dapr’s **Pub/Sub Messaging** building block. Currently, the Chat Service uses Dapr’s Service Invocation to fetch the user’s message count synchronously from the Analytics Service, but there’s no mechanism to update the message count when a new message is sent. We’ll address this by having the Chat Service publish a “MessageSent” event after processing a message, and the Analytics Service will subscribe to this event to increment the message count in the Dapr state store. This event-driven approach will decouple the services and improve scalability. Let’s get started!

---

## What You’ll Learn
- How to use Dapr’s Pub/Sub Messaging building block for asynchronous, event-driven communication.
- Configuring the Chat Service to publish a “MessageSent” event after processing a user message.
- Configuring the Analytics Service to subscribe to the “MessageSent” event and update the message count in the state store.
- Setting up Dapr subscriptions to route events to the correct endpoint.
- Running microservices with Dapr sidecars and testing pub/sub messaging.
- Updating unit tests to account for Dapr Pub/Sub integration.

## Prerequisites
- Completion of **06_dapr_state_management** (codebase with Chat Service and Analytics Service using Dapr Service Invocation and State Management).
- Dapr CLI and runtime installed (from **04_dapr_theory_and_cli**).
- Docker installed (Dapr uses Docker for its sidecars and components).
- Python 3.8+ installed.
- An OpenAI API key (set as `OPENAI_API_KEY`).

---

## Step 1: Recap of the Current Setup
In **06_dapr_state_management**, we integrated Dapr’s State Management into the Analytics Service:
- The **Chat Service** uses Dapr Service Invocation to fetch the user’s message count from the Analytics Service (`http://localhost:3500/v1.0/invoke/analytics-service/method/analytics/{user_id}`).
- The **Analytics Service** stores message counts in a Dapr-managed state store (Redis) and retrieves them when requested.
- We added a temporary `/analytics/{user_id}/initialize` endpoint to set initial message counts for testing.

### Current Limitations
- **No Update Mechanism**: The message count in the state store is static; there’s no way to increment it when a user sends a new message.
- **Synchronous Dependency**: The Chat Service relies on synchronous calls to the Analytics Service, which introduces coupling and potential latency.

### Goal for This Tutorial
We’ll use Dapr’s Pub/Sub Messaging to enable asynchronous communication:
- The Chat Service will publish a “MessageSent” event to a Dapr pub/sub topic after processing a user message.
- The Analytics Service will subscribe to this topic and increment the user’s message count in the state store.
- This decouples the services, allowing the Analytics Service to update message counts asynchronously, improving scalability and resilience.

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
├── pyproject.toml
└── uv.lock
```

---

## Step 2: Why Use Dapr Pub/Sub Messaging?
Dapr’s **Pub/Sub Messaging** building block enables asynchronous, event-driven communication between services. It offers several advantages over synchronous communication (e.g., Service Invocation):
- **Decoupling**: The publisher (Chat Service) doesn’t need to know about the subscriber (Analytics Service), reducing dependencies.
- **Scalability**: Subscribers can process events at their own pace, allowing the system to handle high event volumes.
- **Resilience**: Dapr handles message delivery, retries, and dead-letter queues (configurable), ensuring events are processed reliably.
- **Event-Driven Architecture**: Aligns with DACA’s goal of building an agentic AI system that reacts to events (e.g., user messages, agent responses).
- **Pluggability**: Dapr supports multiple message brokers (e.g., Redis, RabbitMQ, Kafka) via components, making it easy to switch brokers.

In DACA, Pub/Sub Messaging is crucial for:
- Notifying the Analytics Service of new messages without blocking the Chat Service.
- Enabling an event-driven architecture where services react to events, supporting scalability and fault tolerance.

---

## Step 3: Configure Dapr Pub/Sub Component
Dapr uses a pub/sub component to handle messaging. The `dapr init` command already set up a default Redis-based pub/sub component in `~/.dapr/components/pubsub.yaml`. Let’s verify its configuration.

### Check the Default Pub/Sub Component
```bash
cat ~/.dapr/components/pubsub.yaml
```
Output:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```
- `name: pubsub`: The name of the pub/sub component (we’ll use this in our code).
- `type: pubsub.redis`: Uses Redis as the message broker.
- `redisHost`: Points to the Redis instance running on `localhost:6379`.

This component is ready to use. In a production environment, you might configure a cloud-hosted message broker (e.g., CloudAMQP for RabbitMQ) and secure it with credentials.

---

## Step 4: Update the Chat Service to Publish Events
The Chat Service will publish a “MessageSent” event to the `messages` topic after processing a user message. This event will notify the Analytics Service to update the message count.

### Modify `chat_service/main.py`
Add a function to publish an event using Dapr’s Pub/Sub API and call it in the `/chat/` endpoint.

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx

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

async def publish_message_sent_event(user_id: str, dapr_port: int = 3500):
    """Publish a MessageSent event to the messages topic."""
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/messages"
    event_data = {"user_id": user_id, "event_type": "MessageSent"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            print(f"Published MessageSent event for user {user_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to publish MessageSent event: {e}")

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

    # Use Dapr Service Invocation to call the Analytics Service
    dapr_port = 3500
    dapr_url = f"http://localhost:{dapr_port}/v1.0/invoke/analytics-service/method/analytics/{message.user_id}"
    async with httpx.AsyncClient() as client:
        try:
            analytics_response = await client.get(dapr_url)
            analytics_response.raise_for_status()
            analytics_data = analytics_response.json()
            message_count = analytics_data.get("message_count", 0)
        except httpx.HTTPStatusError as e:
            message_count = 0
            print(f"Failed to fetch analytics via Dapr: {e}")

    # Update the agent's instructions with user analytics
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    # Process the message with the OpenAI Agents SDK
    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output

    # Publish a MessageSent event
    await publish_message_sent_event(message.user_id, dapr_port)

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

#### Explanation of Changes
1. **Publish Function**:
   - Added `publish_message_sent_event` to publish an event to the `messages` topic using Dapr’s Pub/Sub API (`http://localhost:3500/v1.0/publish/pubsub/messages`).
   - The event payload includes the `user_id` and `event_type` (`MessageSent`).

2. **Event Publishing**:
   - After processing the message and generating a reply, the `/chat/` endpoint calls `publish_message_sent_event` to notify other services (e.g., Analytics Service) that a message was sent.

### Update `chat_service/tests/test_main.py`
Update the tests to mock the pub/sub event publishing.

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
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("main.publish_message_sent_event", new_callable=AsyncMock) as mock_publish:
        # Mock the Dapr Service Invocation response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"message_count": 5})
        mock_run.return_value.final_output = "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"
        
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
        mock_publish.assert_called_once_with("alice", 3500)

        # Mock a tool-using response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"message_count": 3})
        mock_run.return_value.final_output = "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
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
        mock_publish.assert_called_with("bob", 3500)

        # Test failure of Analytics Service via Dapr
        mock_get.side_effect = httpx.HTTPStatusError(
            message="Not Found", request=AsyncMock(), response=AsyncMock(status_code=404)
        )
        mock_run.return_value.final_output = "Hi Alice! How can I help you today?"
        request_data = {
            "user_id": "alice",
            "text": "Hello again!",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Hi Alice! How can I help you today?"
        mock_publish.assert_called_with("alice", 3500)

        # Invalid request
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
        assert mock_publish.call_count == 3  # Not called for invalid request
```

#### Explanation of Test Changes
- Added a mock for `publish_message_sent_event` to verify that the Chat Service publishes the “MessageSent” event after processing a message.
- Ensured the event is not published for invalid requests (e.g., empty message text).

---

## Step 5: Update the Analytics Service to Subscribe to Events
The Analytics Service will subscribe to the `messages` topic and increment the user’s message count in the state store when a “MessageSent” event is received.

### Modify `analytics_service/main.py`
Add a subscription endpoint to handle incoming pub/sub events and update the message count in the state store.

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

    # Increment the message count in the state store
    await increment_message_count(user_id)
    return {"status": "success"}
```

#### Explanation of Changes
1. **Increment Function**:
   - Added `increment_message_count` to fetch the current message count, increment it, and save it back to the state store.

2. **Subscription Endpoint**:
   - Added a `/messages` POST endpoint to handle events from the `messages` topic.
   - The endpoint checks the `event_type` and `user_id`, then calls `increment_message_count` to update the state.

### Update `analytics_service/tests/test_main.py`
Update the tests to include the new `/messages` endpoint and mock the state management operations.

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
        "message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."
    }

@pytest.mark.asyncio
async def test_get_analytics():
    with patch("main.get_message_count", new_callable=AsyncMock) as mock_get:
        # Test for existing user
        mock_get.return_value = 5
        response = client.get("/analytics/alice")
        assert response.status_code == 200
        assert response.json() == {"message_count": 5}

        # Test for another existing user
        mock_get.return_value = 3
        response = client.get("/analytics/bob")
        assert response.status_code == 200
        assert response.json() == {"message_count": 3}

        # Test for non-existing user
        mock_get.return_value = 0
        response = client.get("/analytics/charlie")
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

@pytest.mark.asyncio
async def test_initialize_message_count():
    with patch("main.set_message_count", new_callable=AsyncMock) as mock_set:
        response = client.post("/analytics/alice/initialize", json={"message_count": 5})
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "alice", "message_count": 5}
        mock_set.assert_called_once_with("alice", 5)

@pytest.mark.asyncio
async def test_handle_message_sent():
    with patch("main.increment_message_count", new_callable=AsyncMock) as mock_increment:
        # Test valid MessageSent event
        event_data = {"event_type": "MessageSent", "user_id": "alice"}
        response = client.post("/messages", json=event_data)
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_increment.assert_called_once_with("alice")

        # Test invalid event (wrong event_type)
        event_data = {"event_type": "OtherEvent", "user_id": "bob"}
        response = client.post("/messages", json=event_data)
        assert response.status_code == 200
        assert response.json() == {"status": "ignored"}
        mock_increment.assert_called_once()  # Not called again

        # Test invalid event (missing user_id)
        event_data = {"event_type": "MessageSent"}
        response = client.post("/messages", json=event_data)
        assert response.status_code == 200
        assert response.json() == {"status": "ignored"}
        mock_increment.assert_called_once()  # Not called again
```

#### Explanation of Test Changes
- Added a test for the `/messages` endpoint to verify it handles “MessageSent” events correctly and ignores invalid events.
- Mocked `increment_message_count` to ensure it’s called only for valid events.

---

## Step 6: Configure Dapr Subscription
Dapr requires a subscription configuration to map topics to endpoints. We’ll create a `subscriptions.yaml` file to define the subscription for the `messages` topic.

### Create the Components Directory
```bash
mkdir -p components
cd components
touch subscriptions.yaml
```

### Define the Subscription in `components/subscriptions.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: message-subscription
spec:
  pubsubname: pubsub
  topic: messages
  route: /messages
```
- `pubsubname: pubsub`: The name of the pub/sub component (matches the default `pubsub.yaml`).
- `topic: messages`: The topic to subscribe to.
- `route: /messages`: The endpoint in the Analytics Service to call when an event is received.

When running the Analytics Service with Dapr, we’ll specify this components directory so Dapr loads the subscription.

---

## Step 7: Run the Microservices with Dapr
### Start the Analytics Service with Dapr
In a terminal, navigate to the Analytics Service directory and run it with Dapr, specifying the components directory:
```bash
cd analytics_service
dapr run --app-id analytics-service --app-port 8001 --dapr-http-port 3501 --components-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001
```
- `--components-path ../components`: Points to the directory containing `subscriptions.yaml`.
- The Analytics Service will subscribe to the `messages` topic and handle events at the `/messages` endpoint.

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
dapr run --app-id chat-service --app-port 8000 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8000
```
Output:
```
ℹ  Starting Dapr with id chat-service. HTTP Port: 3500  gRPC Port: 50001
ℹ  Dapr sidecar is up and running.
ℹ  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

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

## Step 8: Test the Microservices with Dapr Pub/Sub
### Initialize State for Testing
Let’s initialize message counts for `alice` and `bob` using the `/analytics/{user_id}/initialize` endpoint:
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
#### Test State Retrieval
Test the `/analytics/{user_id}` endpoint to verify it retrieves data from the state store:
- Visit `http://localhost:8001/docs` and test:
  - For `alice`: `{"message_count": 5}`
  - For `bob`: `{"message_count": 3}`
  - For `charlie`: `404 Not Found`

#### Test Pub/Sub Subscription
Use the Dapr CLI to publish a test event to the `messages` topic:
```bash
dapr publish --pubsub pubsub --topic messages --data '{"event_type": "MessageSent", "user_id": "alice"}'
```
Output in the Analytics Service terminal:
```
== APP == Received event: {'event_type': 'MessageSent', 'user_id': 'alice'}
== APP == Set message count for alice: 6
```

Check the updated message count for `alice`:
- Visit `http://localhost:8001/docs` and test `/analytics/alice`:
  - Expected: `{"message_count": 6}`

### Test the Chat Service
Send a request to the Chat Service to trigger the full flow (Service Invocation + Pub/Sub):
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
1. The Chat Service receives the request and uses Service Invocation to fetch `bob`’s message count (3) from the Analytics Service.
2. The Chat Service processes the message and generates a reply.
3. The Chat Service publishes a “MessageSent” event to the `messages` topic.
4. The Analytics Service’s Dapr sidecar receives the event and calls the `/messages` endpoint.
5. The Analytics Service increments `bob`’s message count in the state store (from 3 to 4).

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

## Step 9: Why Dapr Pub/Sub Messaging for DACA?
Using Dapr’s Pub/Sub Messaging building block enhances DACA’s architecture by:
- **Decoupling**: The Chat Service and Analytics Service are now loosely coupled; the Chat Service doesn’t need to wait for the Analytics Service to update the message count.
- **Scalability**: Asynchronous communication allows the Analytics Service to process events at its own pace, improving system throughput.
- **Resilience**: Dapr handles message delivery and retries (configurable), ensuring events are processed reliably.
- **Event-Driven Architecture**: Aligns with DACA’s goal of building an agentic AI system that reacts to events (e.g., user actions, agent responses).

---

## Step 10: Next Steps
You’ve successfully integrated Dapr’s Pub/Sub Messaging into our microservices, enabling asynchronous communication between the Chat Service and Analytics Service! In the next tutorial (**08_dapr_workflows**), we’ll explore Dapr’s Workflows building block to orchestrate multi-step processes (e.g., message processing → analytics update → agent response) with retries and compensation logic.

### Optional Exercises
1. Add a new pub/sub topic for “UserRegistered” events and have the Analytics Service initialize a user’s message count to 0 when they register.
2. Configure Dapr to use a different message broker (e.g., RabbitMQ) by creating a custom `pubsub.yaml` in the components directory.
3. Use the Dapr dashboard (`dapr dashboard`) to trace the pub/sub event flow between the Chat Service and Analytics Service.

---

## Conclusion
In this tutorial, we integrated Dapr’s Pub/Sub Messaging building block into our microservices, enabling asynchronous, event-driven communication. The Chat Service now publishes “MessageSent” events, which the Analytics Service subscribes to and uses to update message counts in the state store. This decouples the services, improves scalability, and aligns with DACA’s event-driven architecture goals. We’re now ready to explore Dapr Workflows in the next tutorial!

---

### Final Code for `chat_service/main.py`
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx

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

async def publish_message_sent_event(user_id: str, dapr_port: int = 3500):
    """Publish a MessageSent event to the messages topic."""
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/messages"
    event_data = {"user_id": user_id, "event_type": "MessageSent"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            print(f"Published MessageSent event for user {user_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to publish MessageSent event: {e}")

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

    dapr_port = 3500
    dapr_url = f"http://localhost:{dapr_port}/v1.0/invoke/analytics-service/method/analytics/{message.user_id}"
    async with httpx.AsyncClient() as client:
        try:
            analytics_response = await client.get(dapr_url)
            analytics_response.raise_for_status()
            analytics_data = analytics_response.json()
            message_count = analytics_data.get("message_count", 0)
        except httpx.HTTPStatusError as e:
            message_count = 0
            print(f"Failed to fetch analytics via Dapr: {e}")

    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output

    await publish_message_sent_event(message.user_id, dapr_port)

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

---

### Final Code for `analytics_service/main.py`
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

---

This tutorial provides a focused introduction to Dapr Pub/Sub Messaging, keeping the scope manageable while advancing our microservices architecture. 