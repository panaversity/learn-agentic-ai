# Inter-Microservices Communication Using Dapr

Welcome to the fifth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the stateless microservices we built in **03_microservices_with_fastapi** by integrating **Dapr** for inter-service communication. Previously, the Chat Service called the Analytics Service synchronously using `httpx`. Now, we’ll use Dapr’s **Service Invocation** building block to handle this communication, leveraging Dapr’s sidecar architecture for service discovery, retries, and observability. This tutorial will demonstrate how Dapr simplifies microservices communication while preparing our system for scalability and resilience. Let’s get started!

---

## What You’ll Learn
- How to integrate Dapr with existing FastAPI microservices.
- Using Dapr’s Service Invocation building block for synchronous inter-service communication.
- Replacing direct `httpx` calls with Dapr-managed communication.
- Running microservices with Dapr sidecars using the Dapr CLI.
- Updating unit tests to account for Dapr integration.

## Prerequisites
- Completion of **03_microservices_with_fastapi** (codebase with Chat Service and Analytics Service).
- Completion of **04_dapr_theory_and_cli** (familiarity with Dapr and the Dapr CLI).
- Python 3.12+ installed.
- Dapr CLI and runtime installed (from **04_dapr_theory_and_cli**).
- Docker installed (Dapr uses Docker for its sidecars and components).
- An OpenAI API key (set as `OPENAI_API_KEY`) or Google Gemini Flash 2.0.

---

## Step 1: Recap of the Current Setup
In **03_microservices_with_fastapi**, we built two stateless microservices:
- **Chat Service** (`chat_service/`): Handles user messages, uses the OpenAI Agents SDK to generate responses, and calls the Analytics Service to fetch user analytics (e.g., message count) to personalize responses.
- **Analytics Service** (`analytics_service/`): Provides user analytics (e.g., message count) using mock data.

The Chat Service communicates with the Analytics Service synchronously using `httpx`:
- The Chat Service makes an HTTP GET request to `http://localhost:8001/analytics/{user_id}` to fetch analytics data.
- This approach hardcodes the Analytics Service’s URL and lacks features like service discovery, retries, and observability.

In this tutorial, we’ll replace the `httpx` call with Dapr’s Service Invocation, allowing the Chat Service to call the Analytics Service via Dapr sidecars. Dapr will handle service discovery, retries, and tracing, making our system more robust and scalable.

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

## Step 2: Why Use Dapr for Inter-Service Communication?
Dapr’s **Service Invocation** building block offers several advantages over direct HTTP calls (e.g., using `httpx`):
- **Service Discovery**: Dapr automatically resolves service addresses using app IDs, eliminating hardcoded URLs.
- **Retries and Resilience**: Dapr handles retries, timeouts, and circuit breakers transparently.
- **Observability**: Dapr provides tracing (e.g., via Zipkin) to monitor inter-service calls.
- **Security**: Dapr supports mTLS (mutual TLS) for secure communication between services.
- **Portability**: Dapr works in both self-hosted and Kubernetes environments, aligning with DACA’s deployment goals.

In this tutorial, we’ll configure the Chat Service to invoke the Analytics Service through Dapr sidecars, replacing the direct `httpx` call.

---

## Step 3: Update the Chat Service to Use Dapr Service Invocation
We’ll modify the Chat Service to call the Analytics Service using Dapr’s Service Invocation API instead of `httpx`. Dapr’s Service Invocation API allows a service to call another service by its app ID, with the Dapr sidecar handling the communication.

### Update `chat_service/main.py`
Replace the `httpx` call with a Dapr Service Invocation call. We’ll use `httpx` to call the Dapr sidecar’s API, which will then forward the request to the Analytics Service.

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

    # Use Dapr Service Invocation to call the Analytics Service
    dapr_port = 3500  # Default Dapr HTTP port (will be set when running with Dapr)
    dapr_url = f"http://localhost:{dapr_port}/v1.0/invoke/analytics-service/method/analytics/{message.user_id}"
    async with httpx.AsyncClient() as client:
        try:
            analytics_response = await client.get(dapr_url)
            analytics_response.raise_for_status()
            analytics_data = analytics_response.json()
            message_count = analytics_data.get("message_count", 0)
        except httpx.HTTPStatusError as e:
            message_count = 0  # Fallback if Analytics Service fails
            print(f"Failed to fetch analytics via Dapr: {e}")

    # Update the agent's instructions with user analytics
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

#### Explanation of Changes
1. **Dapr Service Invocation**:
   - We replaced the direct `httpx` call to `http://localhost:8001/analytics/{user_id}` with a call to the Dapr sidecar’s Service Invocation API: `http://localhost:3500/v1.0/invoke/analytics-service/method/analytics/{user_id}`.
   - `analytics-service` is the app ID of the Analytics Service (we’ll set this when running the service with Dapr).
   - `method/analytics/{user_id}` specifies the endpoint on the Analytics Service to invoke (`GET /analytics/{user_id}`).
   - The Dapr sidecar for the Chat Service forwards the request to the Dapr sidecar for the Analytics Service, which then calls the actual endpoint.

2. **Dapr Port**:
   - We hardcoded the Dapr HTTP port as `3500` for simplicity. In a production setup, you’d use an environment variable or Dapr’s configuration to dynamically set this.

3. **Error Handling**:
   - The error handling remains the same: if the Analytics Service call fails, we fall back to a message count of 0.

### Update `chat_service/tests/test_main.py`
Update the tests to mock the Dapr Service Invocation call instead of the direct `httpx` call to the Analytics Service.

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
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
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
```

#### Explanation of Test Changes
- We updated the `patch` for `httpx.AsyncClient.get` to mock the Dapr Service Invocation call (`http://localhost:3500/v1.0/invoke/...`) instead of the direct Analytics Service URL.
- The test logic remains the same: we mock successful responses, tool usage, and failure scenarios.

---

## Step 4: Update the Analytics Service for Dapr
The Analytics Service doesn’t need significant changes since it’s the target of the Service Invocation call. However, we’ll ensure it’s configured to run with a Dapr sidecar and can be invoked by its app ID (`analytics-service`).

### Verify `analytics_service/main.py`
The Analytics Service code remains unchanged, as it already exposes the `/analytics/{user_id}` endpoint that Dapr will invoke. Here’s the current code for reference:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

MOCK_ANALYTICS = {
    "alice": {"message_count": 5},
    "bob": {"message_count": 3},
}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."}

@app.get("/analytics/{user_id}", response_model=Analytics)
async def get_analytics(user_id: str):
    if user_id not in MOCK_ANALYTICS:
        raise HTTPException(status_code=404, detail="User not found")
    return Analytics(**MOCK_ANALYTICS[user_id])
```

### Verify `analytics_service/tests/test_main.py`
The tests for the Analytics Service remain unchanged, as they don’t depend on how the service is invoked (direct HTTP or Dapr). Here’s the current test file for reference:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."
    }

def test_get_analytics():
    response = client.get("/analytics/alice")
    assert response.status_code == 200
    assert response.json() == {"message_count": 5}

    response = client.get("/analytics/bob")
    assert response.status_code == 200
    assert response.json() == {"message_count": 3}

    response = client.get("/analytics/charlie")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
```

---

## Step 5: Run the Microservices with Dapr
We’ll use the Dapr CLI to run both services with Dapr sidecars, specifying their app IDs and ports. Dapr will handle service discovery, allowing the Chat Service to invoke the Analytics Service by its app ID (`analytics-service`).

### Start the Analytics Service with Dapr
In a terminal, navigate to the Analytics Service directory and run it with Dapr:
```bash
cd analytics_service
dapr run --app-id analytics-service --app-port 8001 --dapr-http-port 3501 -- uv run uvicorn main:app --host 0.0.0.0 --port 8001
```
- `--app-id analytics-service`: Sets the app ID for the Analytics Service (used by Dapr for service discovery).
- `--app-port 8001`: The port the Analytics Service listens on.
- `--dapr-http-port 3501`: The port for the Analytics Service’s Dapr sidecar.
- The `uv run uvicorn ...` command starts the FastAPI app.

Output:
```
ℹ  Starting Dapr with id analytics-service. HTTP Port: 3501  gRPC Port: 50002
✅  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Start the Chat Service with Dapr
In a separate terminal, navigate to the Chat Service directory and run it with Dapr:
```bash
cd chat_service
dapr run --app-id chat-service --app-port 8000 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8000
```
- `--app-id chat-service`: Sets the app ID for the Chat Service.
- `--app-port 8000`: The port the Chat Service listens on.
- `--dapr-http-port 3500`: The port for the Chat Service’s Dapr sidecar (matches the hardcoded port in `main.py`).
- The `uv run uvicorn ...` command starts the FastAPI app.

Output:
```
ℹ  Starting Dapr with id chat-service. HTTP Port: 3500  gRPC Port: 50001
✅  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Verify Running Services
Check that both services are running with Dapr:
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

## Step 6: Test the Microservices with Dapr
### Test the Analytics Service
The Analytics Service can still be tested directly (bypassing Dapr) to confirm it’s working:
- Visit `http://localhost:8001/docs` and test the `/analytics/{user_id}` endpoint:
  - For `alice`: `{"message_count": 5}`
  - For `bob`: `{"message_count": 3}`
  - For `charlie`: `404 Not Found`

Alternatively, test it via Dapr Service Invocation:
```bash
dapr invoke --app-id analytics-service --method analytics/alice --data '{}'
```
Output:
```
{"message_count": 5}
```

### Test the Chat Service
Use Swagger UI (`http://localhost:8000/docs`) to send a request to the Chat Service:
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
1. The Chat Service receives the request at `/chat/`.
2. It makes a Service Invocation call to its Dapr sidecar (`http://localhost:3500/v1.0/invoke/analytics-service/method/analytics/alice`).
3. The Chat Service’s Dapr sidecar resolves the `analytics-service` app ID and forwards the request to the Analytics Service’s Dapr sidecar (`http://localhost:3501`).
4. The Analytics Service’s Dapr sidecar calls the actual endpoint (`http://localhost:8001/analytics/alice`).
5. The response flows back through the Dapr sidecars to the Chat Service, which uses the analytics data to personalize the agent’s response.

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
  collected 2 items

  tests/test_main.py::test_root PASSED
  tests/test_main.py::test_get_analytics PASSED

  ================= 2 passed in 0.10s =================
  ```

---

## Step 7: Why Dapr Service Invocation for DACA?
Using Dapr’s Service Invocation building block enhances DACA’s architecture by:
- **Simplified Communication**: No need to hardcode service URLs; Dapr handles service discovery using app IDs.
- **Resilience**: Dapr automatically retries failed requests (configurable via policies), improving fault tolerance.
- **Observability**: Dapr’s tracing (enabled by default with Zipkin) allows us to monitor inter-service calls, which we’ll explore in a future tutorial.
- **Scalability**: Dapr’s sidecar architecture aligns with DACA’s containerized, Kubernetes-based deployment goals.
- **Security**: Dapr supports mTLS for secure communication (configurable in production).

---


### Exercises for Students
1. Configure Dapr to enable mTLS for secure communication between the Chat Service and Analytics Service.
2. Use the Dapr dashboard (`dapr dashboard`) to trace the Service Invocation call between the services.
3. Add a retry policy to the Service Invocation call by creating a Dapr configuration file.

---

## Conclusion
In this tutorial, we integrated Dapr with our Chat Service and Analytics Service, replacing direct `httpx` calls with Dapr’s Service Invocation building block. The Chat Service now communicates with the Analytics Service via Dapr sidecars, leveraging Dapr’s service discovery, retries, and observability features. This makes our microservices more resilient, scalable, and aligned with DACA’s distributed system goals. We’re now ready to explore Dapr’s State Management in the next tutorial!

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

