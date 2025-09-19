# [Inter-Microservices Communication Using Dapr](https://docs.dapr.io/reference/api/service_invocation_api/)

Welcome to the fifth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the stateless microservices we built in **03_microservices_with_fastapi** by integrating **Dapr** for inter-service communication. Previously, the Chat Service called the Agent Memory Service synchronously using `httpx`. Now, we’ll use Dapr’s **Service Invocation** building block to handle this communication, leveraging Dapr’s sidecar architecture for service discovery, retries, and observability. This tutorial will demonstrate how Dapr simplifies microservices communication while preparing our system for scalability and resilience. Let’s get started!

---

## What You’ll Learn
- How to integrate Dapr with existing FastAPI microservices.
- Using Dapr’s Service Invocation building block for synchronous inter-service communication.
- Replacing direct `httpx` calls with Dapr-managed communication.
- Running microservices with Dapr sidecars using the Dapr CLI.
- Updating unit tests to account for Dapr integration.


## Prerequisites
- Completion of **03_microservices_with_fastapi** (codebase with Chat Service and Agent Memory Service).
- Completion of **04_dapr_theory_and_cli** (familiarity with Dapr and the Dapr CLI).
- Python 3.12+ installed.
- Dapr CLI and runtime installed (from **04_dapr_theory_and_cli**).
- Docker installed (Dapr uses Docker for its sidecars and components).
- A Gemini API key (set as `GEMINI_API_KEY` in a `.env` file).

---

## Step 1: Recap of the Current Setup
In **03_microservices_with_fastapi**, we built two stateless microservices:
- **Chat Service** (`chat_service/`): Handles user messages, uses the OpenAI Agents SDK to generate responses, and calls the Agent Memory Service to fetch procedural memories (e.g., past actions) to personalize responses.
- **Agent Memory Service** (`agent_memory_service/`): Provides procedural memories (e.g., past actions) using mock data.

The Chat Service communicates with the Agent Memory Service synchronously using `httpx`:
- The Chat Service makes an HTTP GET request to `http://localhost:8001/memories/{user_id}` to fetch memory data.
- This approach hardcodes the Agent Memory Service’s URL and lacks features like service discovery, retries, and observability.

In this tutorial, we’ll replace the `httpx` call with Dapr’s Service Invocation, allowing the Chat Service to call the Agent Memory Service via Dapr sidecars. Dapr will handle service discovery, retries, and tracing, making our system more robust and scalable.

### Current Project Structure
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   └── test_main.py
│   ├── pyproject.toml
│   └── uv.lock
├── agent_memory_service/
│   ├── main.py
│   ├── models.py
│   └── test_main.py
│   ├── pyproject.toml
│   └── uv.lock
└── README.md
```

---

## Step 2: Why Use Dapr for Inter-Service Communication?
Dapr’s **Service Invocation** building block offers several advantages over direct HTTP calls (e.g., using `httpx`):
- **Service Discovery**: Dapr automatically resolves service addresses using app IDs, eliminating hardcoded URLs.
- **Retries and Resilience**: Dapr handles retries, timeouts, and circuit breakers transparently.
- **Observability**: Dapr provides tracing (e.g., via Zipkin) to monitor inter-service calls.
- **Security**: Dapr supports mTLS (mutual TLS) for secure communication between services.
- **Portability**: Dapr works in both self-hosted and Kubernetes environments, aligning with DACA’s deployment goals.

In this tutorial, we’ll configure the Chat Service to invoke the Agent Memory Service through Dapr sidecars, replacing the direct `httpx` call.

---

## Step 3: Update the Chat Service to Use Dapr Service Invocation
We’ll modify the Chat Service to call the Agent Memory Service using Dapr’s Service Invocation API instead of `httpx`. Dapr’s Service Invocation API allows a service to call another service by its app ID, with the Dapr sidecar handling the communication.

### Update `chat_service/main.py`
Replace the `httpx` call with a Dapr Service Invocation call. We’ll use `httpx` to call the Dapr sidecar’s API, which will then forward the request to the Agent Memory Service.

```python
import os
import httpx

from typing import cast
from dotenv import load_dotenv
from datetime import datetime, UTC

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import OpenAI Agents SDK
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

from models import Message, Response, Metadata

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client), # satisfy type checker
    tracing_disabled=True
)

# Initialize the FastAPI app
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

# Create a tool to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# POST endpoint for chatting
@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    # Use Dapr Service Invocation to call the Agent Memory Service
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")  # Default Dapr HTTP port
    dapr_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{message.user_id}"

    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(dapr_url)
            memory_response.raise_for_status()
            memory_data = memory_response.json()
            past_actions = memory_data.get("past_actions", [])
        except httpx.HTTPStatusError:
            past_actions = []  # Fallback if Memory Service fails

    # Personalize agent instructions with procedural memories
    memory_context = "The user has no past actions." if not past_actions else f"The user’s past actions include: {', '.join(past_actions)}."
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"{memory_context} Use this to personalize your response."
    )

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],  # Add the time tool
        model=model
    )
    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

#### Explanation of Changes
1. **Dapr Service Invocation**:
   - Replaced the direct `httpx` call to `http://localhost:8001/memories/{user_id}` with a call to the Dapr sidecar’s Service Invocation API: `http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}`.
   - `agent-memory-service` is the app ID of the Agent Memory Service (set when running with Dapr).
   - `method/memories/{user_id}` specifies the endpoint on the Agent Memory Service (`GET /memories/{user_id}`).
   - The Dapr sidecar forwards the request to the Agent Memory Service’s sidecar.

2. **Dapr Port**:
   - Used `os.getenv("DAPR_HTTP_PORT", "3500")` to dynamically set the port, aligning with Dapr’s runtime configuration.

3. **Error Handling**:
   - If the Agent Memory Service call fails, it falls back to an empty `past_actions` list, consistent with Tutorial 3.

### Update `chat_service/tests/test_main.py`
Update the tests to mock the Dapr Service Invocation call instead of the direct `httpx` call to the Agent Memory Service.

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
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"past_actions": ["scheduled a meeting", "analyzed data"]})
        mock_run.return_value.final_output = "Hi Alice! I see you’ve scheduled a meeting and analyzed data before. How can I assist you today?"
        
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
        assert response.json()["reply"] == "Hi Alice! I see you’ve scheduled a meeting and analyzed data before. How can I assist you today?"
        assert "metadata" in response.json()

        # Mock a tool-using response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"past_actions": ["wrote a report"]})
        mock_run.return_value.final_output = "Bob, you’ve written a report before. The current time is 2025-04-06 04:01:23 UTC."
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
        assert response.json()["reply"] == "Bob, you’ve written a report before. The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()

        # Test failure of Agent Memory Service via Dapr
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
- Updated `mock_get` to return `past_actions` instead of `message_count`, reflecting the Agent Memory Service’s response.
- Adjusted mock responses to match memory-based personalization.

---

## Step 4: Update the Agent Memory Service for Dapr
The Agent Memory Service doesn’t need significant changes since it’s the target of the Service Invocation call. However, we’ll ensure it’s configured to run with a Dapr sidecar and can be invoked by its app ID (`agent-memory-service`).

### Verify `agent_memory_service/main.py`
The Agent Memory Service code remains unchanged, as it already exposes the `/memories/{user_id}` endpoint that Dapr will invoke. Here’s the current code for reference:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Memories

app = FastAPI(
    title="Agent Memory Service",
    description="Provides procedural memories for AI agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_MEMORIES = {
    "alice": {"past_actions": ["scheduled a meeting", "analyzed data"]},
    "bob": {"past_actions": ["wrote a report"]}
}

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Memory Service! Access /docs for the API documentation."}

@app.get("/memories/{user_id}", response_model=Memories)
async def get_memories(user_id: str):
    if user_id not in MOCK_MEMORIES:
        raise HTTPException(status_code=404, detail="User not found")
    return Memories(**MOCK_MEMORIES[user_id])
```

---

## Step 5: Run the Microservices with Dapr
We’ll use the Dapr CLI to run both services with Dapr sidecars, specifying their app IDs and ports. Dapr will handle service discovery, allowing the Chat Service to invoke the Agent Memory Service by its app ID (`agent-memory-service`).

### Start the Agent Memory Service with Dapr
In a terminal:
```bash
cd agent_memory_service
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 -- uv run uvicorn main:app --host 0.0.0.0 --port 8001
```
- `--app-id agent-memory-service`: Sets the app ID.
- `--app-port 8001`: The app’s listening port.
- `--dapr-http-port 3501`: The Dapr sidecar’s port.

Output:
```
ℹ  Starting Dapr with id agent-memory-service. HTTP Port: 3501  gRPC Port: 50002
✅  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Start the Chat Service with Dapr
In a separate terminal, ensure a `.env` file exists in `chat_service/` with `GEMINI_API_KEY=<your-key>`:
```bash
cd chat_service
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8010
```
- `--app-id chat-service`: Sets the app ID.
- `--app-port 8010`: The app’s listening port.
- `--dapr-http-port 3500`: The Dapr sidecar’s port.

Output:
```
ℹ  Starting Dapr with id chat-service. HTTP Port: 3500  gRPC Port: 50001
✅  You're up and running! Both Dapr and your app logs will appear here.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8010 (Press CTRL+C to quit)
```

### Verify Running Services
```bash
dapr list
```
Output:
```
  APP ID              HTTP PORT  GRPC PORT  APP PORT  COMMAND                          AGE  CREATED              STATUS
  chat-service        3500       50001      8000      uv run uvicorn main:app --ho...  10s  2025-04-07 12:01:00  Running
  agent-memory-service 3501       50002      8001      uv run uvicorn main:app --ho...  15s  2025-04-07 12:00:55  Running
```

---

## Step 6: Test the Microservices with Dapr
### Test the Agent Memory Service
Directly:
- Visit `http://localhost:8001/docs` and test `/memories/{user_id}`:
  - For `alice`: `{"past_actions": ["scheduled a meeting", "analyzed data"]}`
  - For `bob`: `{"past_actions": ["wrote a report"]}`
  - For `charlie`: `404 Not Found`

Via Dapr:
```bash
dapr invoke --app-id agent-memory-service --method  / --verb GET memories/alice --data '{}'

```
Output:
```
{"message":"Welcome to the Agent Memory Service!"}
✅  App invoked successfully
```

### Test the Chat Service
Use Swagger UI (`http://localhost:8010/docs`):
```json
{
  "user_id": "bob",
  "text": "Hello, how are you?",
  "tags": ["wiz"]
}
```
Expected response:
```json
{
  "user_id": "bob",
  "reply": "I'm doing well, thank you for asking! I know you were working on a report earlier. I hope it went well. Is there anything I can help you with today?\n",
  "metadata": {
    "timestamp": "2025-04-07T21:43:07.682565Z",
    "session_id": "621f4356-9c75-4ad4-bc3f-27a1662fefdd"
  }
}
```

#### What Happens During the Request?
1. The Chat Service receives the request at `/chat/`.
2. It calls its Dapr sidecar (`http://localhost:3500/v1.0/invoke/agent-memory-service/method/memories/alice`).
3. The Chat Service’s Dapr sidecar resolves `agent-memory-service` and forwards the request to the Agent Memory Service’s sidecar (`http://localhost:3501`).
4. The Agent Memory Service’s sidecar calls `http://localhost:8001/memories/alice`.
5. The response flows back through the Dapr sidecars, and the Chat Service uses the memories to personalize the response.

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
1. Use the Dapr dashboard (`dapr dashboard`) to trace the Service Invocation call between the services. (Hint: Check Zipkin Container Port)
2. Find how to configure Dapr to enable mTLS for secure communication between the Chat Service and Agent Memory Service.
3. Searcg on How to add a retry policy to the Service Invocation call by creating a Dapr configuration file.

---

## Conclusion
In this tutorial, we integrated Dapr with our Chat Service and Agent Memory Service, replacing direct `httpx` calls with Dapr’s Service Invocation building block. The Chat Service now communicates with the Agent Memory Service via Dapr sidecars, leveraging Dapr’s service discovery, retries, and observability features. This makes our microservices more resilient, scalable, and aligned with DACA’s distributed system goals. We’re now ready to explore Dapr’s State Management in the next tutorial!

---
