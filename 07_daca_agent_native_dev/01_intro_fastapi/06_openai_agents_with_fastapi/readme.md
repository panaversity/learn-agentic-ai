# Integrating [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) with FastAPI

Welcome to the sixth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance our FastAPI-based chatbot by integrating the **[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)**, a powerful toolkit released by OpenAI on 12 March 2025. This SDK allows us to build autonomous AI agents that can make decisions, use tools, and coordinate workflows. We’ll transform our simple chatbot into an agentic system capable of processing user messages intelligently and responding with context-aware replies. Let’s dive in!

---

## Challenge Project

Create the following Agentic System using Agents SDK and FastAPI Interface. Chainlit for UI is recommended but optional

![FastAPI Agents SDK Challenge](./agent-fastapi.png)

---

## What You’ll Learn
- How to set up the OpenAI Agents SDK in a FastAPI project.
- Creating an AI agent using the OpenAI Agents SDK to handle user messages.
- Integrating the agent with FastAPI endpoints to process requests and return responses.
- Adding a simple tool to the agent (e.g., fetching the current time) to demonstrate tool usage.
- Updating unit tests to cover the agentic functionality.
---

In this tutorial, we’ll create a simple agent that processes user messages and responds intelligently, using a tool to fetch the current time as an example of tool usage. This sets the stage for more complex agentic workflows in future DACA tutorials.

---

## Step 2 Setting Up the OpenAI Agents SDK
Let’s add the OpenAI Agents SDK to our existing FastAPI project.

### Navigate to the Project Directory or Create New

Quick Setup for Project

If you’re continuing from the previous tutorial, navigate to your project directory:
```bash
uv init fastapi-daca-tutorial
cd fastapi-daca-tutorial
uv venv
source .venv/bin/activate

uv add "fastapi[standard]" pytest pytest-asyncio
```

### Add the OpenAI Agents SDK Dependency
We’re using `uv` as our dependency manager. Add the `openai-agents` package:
```bash
uv add openai-agents
```
This updates `pyproject.toml` with the new dependency:
```toml
[project]
name = "fastapi-daca-tutorial"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi[standard]>=0.115.12",
    "openai-agents>=0.0.8",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]
```

### Set Up the Gemini API Key
The OpenAI Agents SDK requires an API key to interact with AI models with chat completions api. Create a `.env` file and add environment variable:
```bash
GEMINI_API_KEY="your-api-key-here"
```

---

## Step 3: Creating an AI Agent with the OpenAI Agents SDK
Let’s create an agent that processes user messages and responds in a helpful way. We’ll also add a simple tool to fetch the current time, demonstrating how agents can use tools to perform actions.

### Update `main.py`
Modify `main.py` to integrate the OpenAI Agents SDK. We’ll create an agent, add a tool, and update the `/chat/` endpoint to use the agent for processing messages.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from uuid import uuid4

# Import OpenAI Agents SDK
from agents import Agent, Runner, function_tool

# Initialize the FastAPI app
app = FastAPI(
    title="DACA Chatbot API",
    description="A FastAPI-based API for a chatbot in the DACA tutorial series",
    version="0.1.0",
)

# Pydantic models
class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

# Create a tool to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

# Create an AI agent using OpenAI Agents SDK
chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool.",
    model="gemini-1.5-flash",  # Use Gemini 1.5 Flash model
    tools=[get_current_time],  # Add the time tool
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# GET endpoint with query parameters
@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

# POST endpoint for chatting
@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

### Explanation of the Code
1. **Imports**:
   - `Agent`, `Runner`, `function_tool` from `agents`: Core components of the OpenAI Agents SDK.
   - `Agent` creates an AI agent, `Runner` executes the agent, and `function_tool` defines tools the agent can use.

2. **Tool Definition**:
   - `get_current_time`: A simple tool that returns the current UTC time as a string.
   - Decorated with `@function_tool` to make it usable by the agent. The SDK automatically generates a schema for the tool using Pydantic.

3. **Agent Creation**:
   - `chat_agent`: An instance of `Agent` with:
     - `name`: A unique identifier for the agent.
     - `instructions`: A system prompt guiding the agent’s behavior.
     - `model`: Specifies the LLM (e.g., `gpt-4o`).
     - `tools`: A list of tools the agent can use (here, `get_current_time`).

4. **Updated `/chat/` Endpoint**:
   - Uses `Runner.run` to execute the agent asynchronously with the user’s message (`message.text`).
   - `result.final_output` contains the agent’s response, which may involve tool usage (e.g., fetching the time if the user asks for it).
   - Returns a `Response` object with the agent’s reply.

---

## Step 4: Running and Testing the API
### Start the Server
```bash
fastapi dev main.py
```
 OR
 
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the API
#### Test `/chat/` with a Simple Message
Use Swagger UI (`http://localhost:8000/docs`) to send a request:
```json
{
  "user_id": "junaid",
  "text": "Hello, how are you?",
  "tags": ["greeting"]
}
```
Expected response (actual reply may vary based on the model):
```json
{
  "user_id": "junaid",
  "reply": "I am doing well, thank you for asking! How can I help you today?\n",
  "metadata": {
    "timestamp": "2025-04-07T00:26:17.731540Z",
    "session_id": "4475b689-6cfb-495d-9149-3d01f8e71003"
  }
}
```

#### Test `/chat/` with a Tool-Using Message
Send a request asking for the time:
```json
{
  "user_id": "junaid",
  "text": "What time is it?",
  "tags": ["greeting"]
}
```
Expected response:
```json
{
  "user_id": "junaid",
  "reply": "It is 2025-04-07 00:28:11 UTC.\n",
  "metadata": {
    "timestamp": "2025-04-07T00:28:12.183175Z",
    "session_id": "656462d5-4126-497e-b14a-660a13620269"
  }
}
```

### Streaming Endpoint

Now let's add another streaming endpoint:

```python
# POST endpoint for chatting
async def stream_response(message: Message):
    result = Runner.run_streamed(chat_agent, input=message.text, run_config=config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            # Serialize dictionary to JSON string
            chunk = json.dumps({"chunk": event.data.delta})
            yield f"data: {chunk}\n\n"
            
@app.post("/chat/stream", response_model=Response)
async def chat_stream(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    return StreamingResponse(
        stream_response(message),
        media_type="text/event-stream"
    )

```

Call it in PostMan to see the streaming response.

---

## Step 5: Updating Unit Tests
Let’s update our unit tests to cover the agentic functionality. Since the agent’s responses depend on an external API (OpenAI), we’ll mock the agent’s behavior for consistent testing.

### Update `test_main.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

# Create a test client
client = TestClient(app)

# Test the root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
    }

# Test the /users/{user_id} endpoint
def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

# Mock the OpenAI Agents SDK Runner
@pytest.mark.asyncio
async def test_chat():
    # Mock the Runner.run method
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run:
        # Mock a simple chat response
        mock_run.return_value.final_output = "Hi Alice! I'm doing great, thanks for asking. How about you?"
        
        # Valid request
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
        assert response.json()["reply"] == "Hi Alice! I'm doing great, thanks for asking. How about you?"
        assert "metadata" in response.json()

        # Mock a tool-using response (asking for the time)
        mock_run.return_value.final_output = "The current time is 2025-04-06 04:01:23 UTC."
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
        assert response.json()["reply"] == "The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()

        # Invalid request (empty text)
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

### Run the Tests
```bash
uv run pytest test_main.py -v
```
Output:
```
collected 3 items

tests/test_main.py::test_root PASSED
tests/test_main.py::test_get_user PASSED
tests/test_main.py::test_chat PASSED

================= 3 passed in 0.15s =================
```

### Explanation of the Tests
- **Mocking the Runner**:
  - We use `unittest.mock.patch` to mock `Runner.run`, allowing us to control the agent’s response without making real API calls to OpenAI.
  - `mock_run.return_value.final_output` sets the mocked response for different test cases.
- **Test Cases**:
  - Tests a simple chat message (“Hello, how are you?”).
  - Tests a tool-using message (“What time is it?”).
  - Tests an invalid request (empty text).

---

## Step 6: Why OpenAI Agents SDK for DACA?
The OpenAI Agents SDK is a great fit for DACA because:
- **Autonomy**: Agents can make decisions and perform tasks (e.g., fetching the time) without manual intervention.
- **Tool Integration**: Easily add tools to extend agent capabilities, a key requirement for DACA’s agentic workflows.
- **Scalability**: The SDK’s lightweight design aligns with DACA’s stateless, containerized architecture.
- **Observability**: Built-in tracing (not covered in this tutorial) will help debug complex workflows in later stages.

---


### Exercises for Students
1. Add a new tool to the agent (e.g., a tool to fetch weather data for a given city).
2. Experiment with the agent’s `instructions` to change its tone or behavior (e.g., make it more formal or humorous).
3. Add a unit test for a new endpoint that lists all tools available to the agent.

---

## Conclusion
In this tutorial, we integrated the OpenAI Agents SDK with our FastAPI app, transforming our chatbot into an agentic system capable of autonomous decision-making and tool usage. We created an agent, added a simple tool to fetch the current time, and updated our API and tests to handle agentic responses. This sets a strong foundation for building more complex agentic workflows in the DACA series.

---

### Final Code for `main.py`
```python
import os
from dotenv import load_dotenv
from typing import cast
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from uuid import uuid4

# Import OpenAI Agents SDK
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

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
    title="DACA Chatbot API",
    description="A FastAPI-based API for a chatbot in the DACA tutorial series",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models


class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None


class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

# Create a tool to fetch the current time


@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


# Create an AI agent using OpenAI Agents SDK
chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool.",
    tools=[get_current_time],  # Add the time tool
    model=model
)

# Root endpoint


@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# GET endpoint with query parameters


@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

# POST endpoint for chatting


@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```
---

### Final Code for `tests/test_main.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

# Create a test client
client = TestClient(app)

# Test the root endpoint


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
    }

# Test the /users/{user_id} endpoint


def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

# Mock the OpenAI Agents SDK Runner


@pytest.mark.asyncio
async def test_chat():
    # Mock the Runner.run method
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run:
        # Mock a simple chat response
        mock_run.return_value.final_output = "Hi Alice! I'm doing great, thanks for asking. How about you?"

        # Valid request
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
        assert response.json()[
            "reply"] == "Hi Alice! I'm doing great, thanks for asking. How about you?"
        assert "metadata" in response.json()

        # Mock a tool-using response (asking for the time)
        mock_run.return_value.final_output = "The current time is 2025-04-06 04:01:23 UTC."
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
        assert response.json()[
            "reply"] == "The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()

        # Invalid request (empty text)
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
---

This tutorial successfully integrates the OpenAI Agents SDK with FastAPI, laying the groundwork for more advanced agentic features in the DACA series. 
