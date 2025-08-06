# [Managing State with Dapr in Microservices](https://docs.dapr.io/reference/api/state_api/)

Welcome to the sixth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the microservices from **05_inter_microservices_communication_using_dapr**, where we used Dapr’s Service Invocation for communication between the Chat Service and Agent Memory Service. Now, we’ll integrate Dapr’s **State Management** building block to replace the mock data (`MOCK_MEMORIES`) in the Agent Memory Service with a persistent state store (Redis, initialized by `dapr init`). We’ll store static user metadata and dynamic conversation history, making our system scalable, realistic, and production-ready. Let’s get started!

---

## What You’ll Learn
- How to use Dapr’s State Management building block to store and retrieve data persistently.
- Replacing mock data in the Agent Memory Service with a Dapr-managed state store for user metadata and conversation history.
- Updating the Chat Service to store and leverage conversation context using a `session_id`.
- Running microservices with Dapr sidecars and testing state management.
- Updating unit tests to account for Dapr State Management integration.

## Prerequisites
- Completion of **05_inter_microservices_communication_using_dapr** (Chat Service and Agent Memory Service with Dapr Service Invocation).
- Dapr CLI and runtime installed (v1.15 recommended, per **04_dapr_theory_and_cli**).
- Docker installed (for Dapr sidecars and Redis state store).
- Python 3.12+ installed (noting your use of Python 3.13 from the error log).
- A Gemini API key (set as `GEMINI_API_KEY` in `chat_service/.env`).

---

## Step 1: Recap of the Current Setup
In **05_inter_microservices_communication_using_dapr**, we implemented:
- The **Chat Service**, invoking the **Agent Memory Service** via Dapr sidecars (`http://localhost:3500/v1.0/invoke/agent-memory-service/method/memories/{user_id}`) to fetch static `past_actions`.
- The **Agent Memory Service**, using a hardcoded `MOCK_MEMORIES` dictionary.

### Current Limitations
- **Mock Data**: `MOCK_MEMORIES` is ephemeral and not shared across instances.
- **No Conversation Context**: Lacks storage for dynamic chat history, limiting personalization.

### Goal for This Tutorial
We’ll replace `MOCK_MEMORIES` with a Dapr-managed state store, storing:
- **User Metadata** per `user_id`: Static data like `name`, `preferred_style`, and `goal`.
- **Conversation History** per `session_id`: Dynamic records of user messages and assistant replies.
The Chat Service will use an existing `session_id` from the `metadata` field if provided, or generate a new one, and store each conversation part by calling the Agent Memory Service.

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

## Step 2: Why Use Dapr State Management?
Dapr’s **State Management** provides:
- **Persistence**: Data persists in external stores (e.g., Redis).
- **Scalability**: Shared state supports multiple instances.
- **Consistency**: Offers concurrency control (e.g., ETags).
- **Abstraction**: Unified API across backends.
- **Pluggability**: Easy backend switching.

For DACA, it enables:
- Persistent user metadata and conversation history.
- Scalable, stateless microservices for Kubernetes.
- Practical state management learning.

---

## Step 3: Configure Dapr State Management Component
Verify the default Redis state store:
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
This is sufficient for local testing.

---

## Step 4: Update the Agent Memory Service to Use Dapr State Management
We’ll manage two types of state: user metadata and conversation history.

### Update `agent_memory_service/models.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime, UTC

class UserMetadata(BaseModel):
    name: str
    preferred_style: str
    goal: str

class ConversationEntry(BaseModel):
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

class ConversationHistory(BaseModel):
    history: list[ConversationEntry] = []
```

### Modify `agent_memory_service/main.py`
```python
import logging
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserMetadata, ConversationHistory, ConversationEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DACA Agent Memory Service",
    description="A FastAPI-based service for user metadata and conversation history",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8010"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_user_metadata(user_id: str, dapr_port: int = 3501) -> dict:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/user:{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return {}

async def set_user_metadata(user_id: str, metadata: dict, dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
    state_data = [{"key": f"user:{user_id}", "value": metadata}]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=state_data)
            response.raise_for_status()
            logger.info(f"Stored metadata for {user_id}: {metadata}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to store metadata: {e}")
            raise HTTPException(status_code=500, detail="Failed to store metadata")

async def get_conversation_history(session_id: str, dapr_port: int = 3501) -> list[dict]:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/session:{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            state_data = response.json()
            return state_data.get("history", [])
        except httpx.HTTPStatusError:
            return []

async def set_conversation_history(session_id: str, history: list[dict], dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
    state_data = [{"key": f"session:{session_id}", "value": {"history": history}}]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=state_data)
            response.raise_for_status()
            logger.info(f"Stored conversation history for session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to store conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to store conversation")

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Agent Memory Service! Access /docs for the API documentation."}

@app.get("/memories/{user_id}", response_model=UserMetadata)
async def get_memories(user_id: str):
    metadata = await get_user_metadata(user_id)
    if not metadata:
        return UserMetadata(name=user_id, preferred_style="casual", goal="chat")
    return UserMetadata(**metadata)

@app.post("/memories/{user_id}/initialize", response_model=dict)
async def initialize_memories(user_id: str, metadata: UserMetadata):
    await set_user_metadata(user_id, metadata.dict())
    return {"status": "success", "user_id": user_id, "metadata": metadata.dict()}

@app.get("/conversations/{session_id}", response_model=ConversationHistory)
async def get_conversation(session_id: str):
    history = await get_conversation_history(session_id)
    return ConversationHistory(history=[ConversationEntry(**entry) for entry in history])

@app.post("/conversations/{session_id}", response_model=dict)
async def update_conversation(session_id: str, history: ConversationHistory):
    await set_conversation_history(session_id, [entry.dict() for entry in history.history])
    return {"status": "success", "session_id": session_id}
```

#### Explanation of Changes
1. **State Functions**: Manage user metadata and conversation history separately.
2. **Endpoints**:
   - `/memories/{user_id}`: Fetches metadata.
   - `/conversations/{session_id}`: Fetches or updates history.

### Update `agent_memory_service/test_main.py`
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
        "message": "Welcome to the DACA Agent Memory Service! Access /docs for the API documentation."
    }

@pytest.mark.asyncio
async def test_get_memories():
    with patch("main.get_user_metadata", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}
        response = client.get("/memories/alice")
        assert response.status_code == 200
        assert response.json() == {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}

@pytest.mark.asyncio
async def test_initialize_memories():
    with patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set:
        metadata = {"name": "Bob", "preferred_style": "casual", "goal": "learn coding"}
        response = client.post("/memories/bob/initialize", json=metadata)
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "bob", "metadata": metadata}

@pytest.mark.asyncio
async def test_conversation():
    with patch("main.get_conversation_history", new_callable=AsyncMock) as mock_get, \
         patch("main.set_conversation_history", new_callable=AsyncMock) as mock_set:
        mock_get.return_value = [{"role": "user", "content": "Hi", "timestamp": "2025-04-07T15:00:00Z"}]
        response = client.get("/conversations/session123")
        assert response.status_code == 200
        assert len(response.json()["history"]) == 1

        history = {"history": [{"role": "assistant", "content": "Hello!", "timestamp": "2025-04-07T15:01:00Z"}]}
        response = client.post("/conversations/session123", json=history)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
```

---

## Step 5: Update the Chat Service

### Update `chat_service/models.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from uuid import uuid4

class Metadata(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] = []

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

class ConversationEntry(BaseModel):
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### Modify `chat_service/main.py`
```python
import os
import httpx
from typing import cast
from dotenv import load_dotenv
from datetime import datetime, UTC
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Response, Metadata, ConversationEntry

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set in .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=cast(ModelProvider, external_client), tracing_disabled=True)

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
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    # Use existing session_id from metadata if provided, otherwise generate a new one
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")

    # Fetch user metadata
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{message.user_id}"
    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(metadata_url)
            memory_response.raise_for_status()
            memory_data = memory_response.json()
        except httpx.HTTPStatusError as e:
            memory_data = {"name": message.user_id, "preferred_style": "casual", "goal": "chat"}
            print(f"Failed to fetch metadata: {e}")

    # Fetch conversation history
    history_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/conversations/{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            history_response = await client.get(history_url)
            history_response.raise_for_status()
            history = history_response.json()["history"]
        except httpx.HTTPStatusError:
            history = []
            print(f"No prior history for session {session_id}")

    name = memory_data.get("name", message.user_id)
    style = memory_data.get("preferred_style", "casual")
    goal = memory_data.get("goal", "chat")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    personalized_instructions = (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user’s name is {name}, their goal is to {goal}. {context}"
    )

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],
        model=model
    )
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output

    # Update conversation history
    history.append(ConversationEntry(role="user", content=message.text).dict())
    history.append(ConversationEntry(role="assistant", content=reply_text).dict())
    async with httpx.AsyncClient() as client:
        update_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/conversations/{session_id}"
        try:
            await client.post(update_url, json={"history": history})
        except httpx.HTTPStatusError as e:
            print(f"Failed to store conversation: {e}")

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata(session_id=session_id)
    )
```

#### Explanation of Changes
1. **Session ID Fix**: Correctly accesses `message.metadata.session_id`, handling `None` cases.
2. **Conversation Storage**: Appends user and assistant messages to history and updates the state store.
3. **Response**: Passes `session_id` to `Metadata` explicitly.

---

## Step 6: Run the Microservices with Dapr
### Start the Agent Memory Service
```bash
cd agent_memory_service
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start the Chat Service
Ensure `chat_service/.env` has `GEMINI_API_KEY=<your-key>`:
```bash
cd chat_service
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Verify Running Services
```bash
dapr list
```

---

## Step 7: Test the Microservices with Dapr State Management
### Initialize State
- For `junaid`:
  ```bash
  curl -X POST http://localhost:8001/memories/junaid/initialize -H "Content-Type: application/json" -d '{"name": "Junaid", "preferred_style": "formal", "goal": "schedule tasks"}'
  ```

### Test the Chat Service
First request (new session):
```json
{
  "user_id": "junaid",
  "text": "Hello",
  "tags": ["greeting"]
}
```
Response:
```json
{
  "user_id": "junaid",
  "reply": "Hello Junaid, how may I help you today?\n",
  "metadata": {
    "timestamp": "2025-04-08T22:06:28.209479+00:00",
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  }
}
```
Second request (using returned `session_id`):
```json
{
  "user_id": "junaid",
  "text": "What time is it?",
  "metadata": {
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  },
  "tags": ["question"]
}
```
Response:
```json
{
  "user_id": "junaid",
  "reply": "The current time is 2025-04-08 22:06:53 UTC.  How may I further assist you with your task scheduling?\n",
  "metadata": {
    "timestamp": "2025-04-08T22:06:54.669251+00:00",
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  }
}
```

Thied request (using returned `session_id`):
```json
{
  "user_id": "junaid",
  "text": "What have we talked about and what do you know about me?",
  "metadata": {
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  },
  "tags": ["question"]
}
```
Response:
```json
{
  "user_id": "junaid",
  "reply": "We have just begun our conversation.  I know your name is Junaid and that your goal is to schedule tasks.  I have no other information about you.\n",
  "metadata": {
    "timestamp": "2025-04-08T22:07:21.600372+00:00",
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  }
}
```
#### Verify Conversation History
Input:
```json
{
  "user_id": "junaid",
  "text": "What were my last 2 messages?",
  "metadata": {
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  },
  "tags": ["question"]
}
```
Output:
```json
{
  "user_id": "junaid",
  "reply": "Your last two messages were:\n\n1. \"What time is it?\"\n2. \"What have we talked about and what do you know about me?\"\n",
  "metadata": {
    "timestamp": "2025-04-08T22:08:02.874905+00:00",
    "session_id": "623d75cd-528c-4768-9652-cf33e233d049"
  }
}
```
-> Try what happens if you don't share session_id or change it!

#### What Happens During the Request?
1. Chat Service uses provided `session_id` or generates a new one.
2. Fetches metadata and history via Dapr.
3. Personalizes response and stores conversation parts.

### Run the Tests
- Agent Memory Service: `cd agent_memory_service && uv run pytest test_main.py -v`
- Run Chat Service tests
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

@pytest.mark.asyncio
async def test_chat():
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # Mock metadata and history responses
        mock_get.side_effect = [
            AsyncMock(status_code=200, json=lambda: {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}),
            AsyncMock(status_code=200, json=lambda: {"history": []})
        ]
        mock_run.return_value.final_output = "Greetings, Alice!"
        mock_post.return_value = AsyncMock(status_code=200)

        request_data = {
            "user_id": "alice",
            "text": "Hello",
            "tags": ["greeting"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Greetings, Alice!"
        assert "session_id" in response.json()["metadata"]
```

Run: `cd chat_service && uv run pytest test_main.py -v`

---

## Step 8: Why Dapr State Management for DACA?
- **Persistence**: Metadata and conversations persist.
- **Scalability**: Supports distributed instances.
- **Realism**: Tracks chat history for context.

---

### Exercises for Students
1. Enhance the Chat Service to summarize history for longer sessions.
2. Use Zikin, `dapr dashboard` and inspect stored state.
3. Find and implement how to fire a [callback or webhook using FastAPI](https://fastapi.tiangolo.com/advanced/openapi-webhooks/#an-app-with-webhooks) so we don't have to wait while our chat history is saved.
---

## Conclusion
We’ve integrated Dapr’s State Management, replacing mock data with persistent user metadata and conversation history. This enhances scalability and realism, aligning with DACA’s goals. Next, we’ll explore Dapr Pub/Sub Messaging!