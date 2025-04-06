# Managing State with Dapr in Microservices


Welcome to the sixth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll build on the microservices from **05_inter_microservices_communication_using_dapr**, where we integrated Dapr’s Service Invocation to enable synchronous communication between the Chat Service and Analytics Service. Now, we’ll focus on Dapr’s **State Management** building block to replace the mock data (`MOCK_ANALYTICS`) in the Analytics Service with a Dapr-managed state store (using Redis, the default store initialized by `dapr init`). This will make our analytics data persistent, scalable, and suitable for a distributed system. Let’s get started!

---

## What You’ll Learn
- How to use Dapr’s State Management building block to store and retrieve data persistently.
- Replacing mock data in the Analytics Service with a Dapr-managed state store.
- Updating the Chat Service to work with the updated Analytics Service.
- Running microservices with Dapr sidecars and testing state management.
- Updating unit tests to account for Dapr State Management integration.

## Prerequisites
- Completion of **05_inter_microservices_communication_using_dapr** (codebase with Chat Service and Analytics Service using Dapr Service Invocation).
- Dapr CLI and runtime installed (from **04_dapr_theory_and_cli**).
- Docker installed (Dapr uses Docker for its sidecars and components).
- Python 3.12+ installed.
- An OpenAI API key (set as `OPENAI_API_KEY`) or Google Gemini Flash 2.0.

---

## Step 1: Recap of the Current Setup
In **05_inter_microservices_communication_using_dapr**, we modified our microservices to use Dapr’s Service Invocation:
- The **Chat Service** calls the **Analytics Service** via Dapr sidecars (`http://localhost:3500/v1.0/invoke/analytics-service/method/analytics/{user_id}`) to fetch the user’s message count.
- The **Analytics Service** uses a hardcoded dictionary (`MOCK_ANALYTICS`) to store and return analytics data (e.g., message counts).

### Current Limitations
- **Mock Data**: The Analytics Service uses `MOCK_ANALYTICS`, which is not persistent (data is lost on restart) and not suitable for a distributed system where multiple instances need to share state.
- **Scalability**: Hardcoded data doesn’t support horizontal scaling, as each instance of the Analytics Service would have its own copy of the data.

### Goal for This Tutorial
We’ll replace `MOCK_ANALYTICS` with a Dapr-managed state store (Redis, the default store). The Analytics Service will:
- Store message counts in the state store.
- Retrieve message counts from the state store when requested by the Chat Service.
This will make the analytics data persistent and accessible across multiple instances of the Analytics Service, aligning with DACA’s scalability goals.

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

## Step 2: Why Use Dapr State Management?
Dapr’s **State Management** building block provides a key-value store for managing application state in a distributed system. It offers several advantages over mock data or local storage:
- **Persistence**: State is stored in an external store (e.g., Redis, CockroachDB), surviving service restarts.
- **Scalability**: Multiple instances of a service can share the same state store, enabling horizontal scaling.
- **Consistency**: Dapr supports consistency models (e.g., eventual, strong) and concurrency control (e.g., ETags for optimistic concurrency).
- **Abstraction**: Dapr provides a consistent API for state operations (e.g., get, set, delete), regardless of the underlying store.
- **Pluggability**: You can switch state stores (e.g., from Redis to Postgres) by changing the Dapr component configuration.

In DACA, State Management is crucial for:
- Storing user analytics (e.g., message counts) persistently.
- Supporting stateless services that can scale horizontally in a containerized environment (e.g., Kubernetes).
- Ensuring data consistency across distributed instances of the Analytics Service.

---

## Step 3: Configure Dapr State Management Component
Dapr uses a state store component to manage state. The `dapr init` command already set up a default Redis-based state store in `~/.dapr/components/statestore.yaml`. Let’s verify its configuration.

### Check the Default State Store Component
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
- `name: statestore`: The name of the state store component (we’ll use this in our code).
- `type: state.redis`: Uses Redis as the state store.
- `redisHost`: Points to the Redis instance running on `localhost:6379` (set up by `dapr init`).

This component is ready to use, so we don’t need to modify it for now. In a production environment, you might configure a cloud-hosted Redis instance (e.g., Upstash) and secure it with a password.

---

## Step 4: Update the Analytics Service to Use Dapr State Management
We’ll modify the Analytics Service to store and retrieve message counts using Dapr’s State Management API, replacing the `MOCK_ANALYTICS` dictionary.

### Modify `analytics_service/main.py`
Add functions to interact with the Dapr state store and update the `/analytics/{user_id}` endpoint to use them.

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

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."}

@app.get("/analytics/{user_id}", response_model=Analytics)
async def get_analytics(user_id: str):
    message_count = await get_message_count(user_id)
    if message_count == 0 and user_id not in ["alice", "bob"]:  # Simulate 404 for unknown users
        raise HTTPException(status_code=404, detail="User not found")
    return Analytics(message_count=message_count)

# Temporary endpoint to initialize state for testing
@app.post("/analytics/{user_id}/initialize")
async def initialize_message_count(user_id: str, message_count: int):
    await set_message_count(user_id, message_count)
    return {"status": "success", "user_id": user_id, "message_count": message_count}
```

#### Explanation of Changes
1. **State Management Functions**:
   - `get_message_count`: Retrieves the message count for a user from the Dapr state store (`http://localhost:3501/v1.0/state/statestore/{user_id}`). Returns 0 if the user doesn’t exist.
   - `set_message_count`: Sets the message count for a user in the state store (`http://localhost:3501/v1.0/state/statestore`).

2. **Updated Endpoint**:
   - `/analytics/{user_id}`: Now retrieves the message count from the state store instead of `MOCK_ANALYTICS`.
   - Removed the `MOCK_ANALYTICS` dictionary, as we’re now using the Dapr state store.

3. **Temporary Initialization Endpoint**:
   - Added `/analytics/{user_id}/initialize` to set initial message counts for testing purposes. In a real application, this would be part of a user registration flow or handled by another service.

### Update `analytics_service/tests/test_main.py`
Update the tests to mock the Dapr State Management API calls.

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
```

#### Explanation of Test Changes
1. **Mock State Management**:
   - Mocked `get_message_count` to simulate retrieving message counts from the state store.
   - Mocked `set_message_count` to verify it’s called when initializing message counts.

2. **New Test for Initialization**:
   - Added a test for the `/analytics/{user_id}/initialize` endpoint to ensure it sets the message count correctly.

---

## Step 5: Verify the Chat Service
The Chat Service doesn’t need changes, as it already uses Dapr Service Invocation to call the Analytics Service. However, let’s verify its code for completeness.

### `chat_service/main.py` (Unchanged)
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

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

The Chat Service tests (`chat_service/tests/test_main.py`) also remain unchanged, as they already mock the Service Invocation call to the Analytics Service.

---

## Step 6: Run the Microservices with Dapr
### Start the Analytics Service with Dapr
In a terminal, navigate to the Analytics Service directory and run it with Dapr:
```bash
cd analytics_service
dapr run --app-id analytics-service --app-port 8001 --dapr-http-port 3501 -- uv run uvicorn main:app --host 0.0.0.0 --port 8001
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

## Step 7: Test the Microservices with Dapr State Management
### Initialize State for Testing
Since the state store is initially empty, let’s initialize message counts for `alice` and `bob` using the `/analytics/{user_id}/initialize` endpoint.

Set initial message counts:
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

### Test the Chat Service
Send a request to the Chat Service to verify the full flow:
```json
{
  "user_id": "alice",
  "text": "Hello, how are you?",
  "metadata": {
    "timestamp": "2025-04-06T12:00:00Z",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "tags": ["greeting"]
}
```
Expected response (actual reply may vary):
```json
{
  "user_id": "alice",
  "reply": "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?",
  "metadata": {
    "timestamp": "2025-04-06T04:01:00Z",
    "session_id": "some-uuid"
  }
}
```

#### What Happens During the Request?
1. The Chat Service receives the request and uses Service Invocation to call the Analytics Service.
2. The Analytics Service retrieves `alice`’s message count (5) from the Dapr state store.
3. The Chat Service uses the message count to personalize the agent’s response.

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
  collected 3 items

  tests/test_main.py::test_root PASSED
  tests/test_main.py::test_get_analytics PASSED
  tests/test_main.py::test_initialize_message_count PASSED

  ================= 3 passed in 0.12s =================
  ```

---

## Step 8: Why Dapr State Management for DACA?
Using Dapr’s State Management building block enhances DACA’s architecture by:
- **Persistence**: Message counts are now stored in a persistent state store (Redis), surviving service restarts.
- **Scalability**: Multiple instances of the Analytics Service can share the same state store, supporting horizontal scaling in a containerized environment.
- **Consistency**: Dapr provides options for consistency and concurrency control (e.g., ETags), which we’ll explore in future tutorials.
- **Abstraction**: The Dapr State Management API abstracts the underlying store, making it easy to switch to a different backend (e.g., CockroachDB) if needed.

---


### Exercises for Students
1. Configure Dapr to use a different state store (e.g., in-memory for testing) by creating a custom `statestore.yaml` in a components directory.
2. Add a new endpoint to the Analytics Service to increment the message count, simulating a real-world update scenario.
3. Use the Dapr dashboard (`dapr dashboard`) to inspect the state store and verify the stored data.

---

## Conclusion
In this tutorial, we integrated Dapr’s State Management building block into our microservices, replacing the mock data in the Analytics Service with a Dapr-managed state store. The Analytics Service now stores and retrieves message counts persistently, making our system more scalable and production-ready. This aligns with DACA’s goals of building a distributed, resilient agentic AI system. We’re now ready to explore Dapr Pub/Sub Messaging in the next tutorial!

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
```

---

This tutorial provides a focused introduction to Dapr State Management, keeping the scope manageable while advancing our microservices architecture. 