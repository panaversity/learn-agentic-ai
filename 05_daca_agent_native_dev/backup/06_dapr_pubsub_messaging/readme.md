# Event-Driven Communication with Dapr Pub/Sub

Welcome to the seventh tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the microservices from **06_dapr_state_management**, where the Chat Service synchronously updates conversation history in the Agent Memory Service using Dapr’s Service Invocation. Now, we’ll integrate Dapr’s **Pub/Sub Messaging** building block to:
- Publish a “ConversationUpdated” event from the Chat Service to update conversation history asynchronously.
- Dynamically update user metadata (`user_summary`) in the Agent Memory Service using an LLM, triggered by conversation events.
This event-driven approach decouples the services, improves scalability, and makes metadata adaptive. Let’s dive in!

---

## What You’ll Learn
- How to use Dapr’s Pub/Sub Messaging for asynchronous, event-driven communication.
- Configuring the Chat Service to publish “ConversationUpdated” events after processing messages.
- Configuring the Agent Memory Service to subscribe to these events, update conversation history, and generate a dynamic `user_summary` with an LLM.
- Setting up Dapr subscriptions to route events.
- Running microservices with Dapr sidecars and testing pub/sub messaging.
- Updating unit tests for Pub/Sub integration.

## Prerequisites
- Completion of **06_dapr_state_management** (Chat Service and Agent Memory Service with Dapr State Management).
- Dapr CLI and runtime installed (v1.15 recommended, per **04_dapr_theory_and_cli**).
- Docker installed (for Dapr sidecars and Redis).
- Python 3.12+ installed (compatible with Python 3.13 as used in prior examples).
- A Gemini API key (set as `GEMINI_API_KEY` in `chat_service/.env`).

---

## Step 1: Recap of the Current Setup
In **06_dapr_state_management**, we implemented:
- The **Chat Service**, which invokes the Agent Memory Service via Dapr (`http://localhost:3500/v1.0/invoke/agent-memory-service/method/memories/{user_id}`) to fetch static user metadata and updates conversation history synchronously.
- The **Agent Memory Service**, storing static metadata (`name`, `preferred_style`, `goal`) and conversation history in a Dapr state store (Redis).

### Current Limitations
- **Synchronous Updates**: The Chat Service directly updates conversation history, coupling it to the Agent Memory Service and introducing latency.
- **Static Metadata**: User metadata is static and doesn’t evolve with conversations, limiting personalization.

### Goal for This Tutorial
We’ll use Dapr Pub/Sub to:
- **Decouple History Updates**: The Chat Service will publish “ConversationUpdated” events to a `conversations` topic, and the Agent Memory Service will subscribe to update the history.
- **Dynamic Metadata**: The Agent Memory Service will use an LLM to generate a `user_summary` string (e.g., “Junaid enjoys coding and scheduling tasks”) based on conversation history, updated via Pub/Sub.

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
│   ├── components/
└── README.md
```

---

## Step 2: Why Use Dapr Pub/Sub Messaging?
Dapr’s **Pub/Sub Messaging** enables:
- **Decoupling**: Publishers don’t need to know subscribers, reducing dependencies.
- **Scalability**: Asynchronous processing handles high event volumes.
- **Resilience**: Dapr manages delivery, retries, and dead-letter queues.
- **Event-Driven Design**: Aligns with DACA’s agentic goals.

For DACA, Pub/Sub:
- Decouples conversation history updates.
- Enables dynamic metadata generation based on events.

---

## Step 3: Configure Dapr Pub/Sub Component
Verify the default Redis pub/sub component:
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
This component is ready to use. In a production environment, you might configure a cloud-hosted message broker (e.g., CloudAMQP for RabbitMQ) and secure it with credentials. This is ready for local use.

---

## Step 4: Update the Chat Service to Publish Events
The last tutorial is our starter code here.

The Chat Service will publish a “ConversationUpdated” event instead of directly updating history.

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

async def publish_conversation_event(user_id: str, session_id: str, user_text: str, reply_text: str, dapr_port: int = 3500):
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/conversations"
    event_data = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": "ConversationUpdated",
        "user_message": user_text,
        "assistant_reply": reply_text
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            print(f"Published ConversationUpdated event for {user_id}, session {session_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to publish event: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")

    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{message.user_id}"
    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(metadata_url)
            memory_response.raise_for_status()
            memory_data = memory_response.json()
        except httpx.HTTPStatusError as e:
            memory_data = {"name": message.user_id, "preferred_style": "casual", "user_summary": f"{message.user_id} is a new user."}
            print(f"Failed to fetch metadata: {e}")

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
    summary = memory_data.get("user_summary", f"{name} is a new user.")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    personalized_instructions = (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user’s name is {name}. User summary: {summary}. {context}"
    )

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],
        model=model
    )
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output

    await publish_conversation_event(message.user_id, session_id, message.text, reply_text, dapr_port)

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata(session_id=session_id)
    )
```

#### Changes
1. **Publish Function**: Publishes a “ConversationUpdated” event with `user_id`, `session_id`, `user_message`, and `assistant_reply`.
2. **Removed Direct Update**: No longer calls `/conversations/{session_id}` directly.

### Update `chat_service/test_main.py`
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
         patch("main.publish_conversation_event", new_callable=AsyncMock) as mock_publish:
        mock_get.side_effect = [
            AsyncMock(status_code=200, json=lambda: {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}),
            AsyncMock(status_code=200, json=lambda: {"history": []})
        ]
        mock_run.return_value.final_output = "Greetings, Junaid! How may I assist you today?"
        request_data = {"user_id": "junaid", "text": "Hello", "tags": ["greeting"]}
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Greetings, Junaid! How may I assist you today?"
        mock_publish.assert_called_once()
```

---

## Step 5: Update the Agent Memory Service to Subscribe to Events
The Agent Memory Service will subscribe to the `conversations` topic, update history, and generate a dynamic `user_summary`.

### Update `agent_memory_service/models.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime, UTC

class UserMetadata(BaseModel):
    name: str
    preferred_style: str
    user_summary: str

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
import httpx
import os
from dotenv import load_dotenv
from typing import cast

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

from models import UserMetadata, ConversationHistory, ConversationEntry

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=cast(ModelProvider, external_client), tracing_disabled=True)

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
            if response.status_code == 204:  # No content means no history
                return []
            state_data = response.json()
            return state_data.get("history", [])
        except httpx.HTTPStatusError:
            return []  # Return empty list if key doesn't exist or other errors

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

async def generate_user_summary(user_id: str, history: list[dict]) -> str:
    summary_agent = Agent(
        name="SummaryAgent",
        instructions="Generate a concise summary of the user based on their conversation history (e.g., 'Junaid enjoys coding and scheduling tasks'). Use only the provided history.",
        model=model
    )
    history_text = "\n".join([f"{entry['role']}: {entry['content']}" for entry in history[-5:]])  # Last 5 entries
    result = await Runner.run(summary_agent, input=history_text, run_config=config)
    return result.final_output

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

# NEW
@app.post("/conversations")
async def handle_conversation_updated(event: dict):
    print(f"Received event: {event}")
    # Extract the actual event data from the "data" field
    event_data = event.get("data", {})
    event_type = event_data.get("event_type")
    user_id = event_data.get("user_id")
    session_id = event_data.get("session_id")
    user_message = event_data.get("user_message")
    assistant_reply = event_data.get("assistant_reply")

    logger.info(f"Event validation: type={event_type}, user_id={user_id}, session_id={session_id}, user_message={user_message}, assistant_reply={assistant_reply}")

    if event_type != "ConversationUpdated" or not all([user_id, session_id, user_message, assistant_reply]):
        logger.warning("Event ignored due to invalid structure")
        return {"status": "ignored"}

    history = await get_conversation_history(session_id)
    history.extend([
        ConversationEntry(role="user", content=user_message).dict(),
        ConversationEntry(role="assistant", content=assistant_reply).dict()
    ])
    await set_conversation_history(session_id, history)

    metadata = await get_user_metadata(user_id)
    if not metadata:
        metadata = {"name": user_id, "preferred_style": "casual", "user_summary": f"{user_id} is a new user."}
    metadata["user_summary"] = await generate_user_summary(user_id, history)
    await set_user_metadata(user_id, metadata)

    return {"status": "SUCCESS"}  # Uppercase to match Dapr’s expectation
```

#### Changes
1. **Subscription Endpoint**: Handles “ConversationUpdated” events, updates history, and regenerates `user_summary`.
2. **Dynamic Metadata**: Uses an LLM to update `user_summary` based on history.

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
        mock_get.return_value = {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid enjoys coding."}
        response = client.get("/memories/junaid")
        assert response.status_code == 200
        assert response.json() == {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid enjoys coding."}

@pytest.mark.asyncio
async def test_initialize_memories():
    with patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set:
        metadata = {"name": "Junaid", "preferred_style": "casual", "user_summary": "Junaid is a new user."}
        response = client.post("/memories/junaid/initialize", json=metadata)
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "junaid", "metadata": metadata}

@pytest.mark.asyncio
async def test_conversation():
    with patch("main.get_conversation_history", new_callable=AsyncMock) as mock_get_history, \
         patch("main.set_conversation_history", new_callable=AsyncMock) as mock_set_history, \
         patch("main.get_user_metadata", new_callable=AsyncMock) as mock_get_meta, \
         patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set_meta, \
         patch("main.generate_user_summary", new_callable=AsyncMock) as mock_summary:
        mock_get_history.return_value = [{"role": "user", "content": "Hi", "timestamp": "2025-04-07T15:00:00Z"}]
        mock_get_meta.return_value = {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}
        mock_summary.return_value = "Junaid enjoys coding."
        response = client.get("/conversations/session123")
        assert response.status_code == 200
        assert len(response.json()["history"]) == 1

        event = {
            "event_type": "ConversationUpdated",
            "user_id": "junaid",
            "session_id": "session123",
            "user_message": "Hello",
            "assistant_reply": "Hi Junaid!"
        }
        response = client.post("/conversations", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "ignored"
```

---

## Step 6: Configure Dapr Subscription
We manage all Dapr components (state store, pub/sub, and subscriptions) in `fastapi-daca-tutorial/components/`, overriding defaults with `--components-path` when running services. First, ensure a Redis instance is available for these components to use.

Since the components/ directory doesn’t yet exist in the project structure, create it in the project root and add the subscription file.

```bash
cd fastapi-daca-tutorial
mkdir components
touch components/subscriptions.yaml
```

Edit components/subscriptions.yaml with:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: conversation-subscription
spec:
  pubsubname: pubsub
  topic: conversations
  route: /conversations
```
This file links the conversations topic to the /conversations endpoint in the Agent Memory Service, using the "pubsub" component defined in ~/.dapr/components/pubsub.yaml.

### Get Other Components here as well
Now statestore.yaml and pubsub.yaml are missing from this directory, so Dapr has no state store or pub/sub component configured, causing the failures.

#### statestore.yaml
Create statestore.yaml in components directory with following config
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
  - name: actorStateStore
    value: "true"
```

#### pubsub.yaml
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

---

## Step 7: Run the Microservices with Dapr

## Setup Dapr
```bash
dapr init
```
- It ensures a Redis container is running at localhost:6379 (which our statestore.yaml and pubsub.yaml in fastapi-daca-tutorial/components/ depend on).
- It creates default components in ~/.dapr/components/, but we ignore those because we override them with --components-path in dapr run.

### Start the Agent Memory Service
Note: Now here you will first install openai agents sdk and create a .env file with Gemini Key like in chat-service
```bash
cd fastapi-daca-tutorial/agent_memory_service

uv venv
source .venv/bin/activate
uv sync

uv add openai-agents

dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start the Chat Service
```bash
cd chat_service
uv venv
source .venv/bin/activate
uv sync

cd fastapi-daca-tutorial/chat_service
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload

```

### Verify Running Services
```bash
dapr list
```

---

## Step 8: Test the Microservices with Dapr Pub/Sub
### Initialize State
- For `junaid`:
  ```bash
  curl -X POST http://localhost:8001/memories/junaid/initialize -H "Content-Type: application/json" -d '{"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}'
  ```

Successful Output:
```bash
{"status":"success","user_id":"junaid","metadata":{"name":"Junaid","preferred_style":"formal","user_summary":"Junaid is a new user."}}%
```

### Test the Chat Service
First request:
```json
{
  "user_id": "junaid",
  "text": "I need to schedule a coding session."
}
```
Response:
```json
{
  "user_id": "junaid",
  "reply": "Certainly, Junaid.  To schedule your coding session, I require some additional information. Please specify the topic, date, time, duration, and any preferred coding tools or technologies.\n",
  "metadata": {
    "timestamp": "2025-04-08T23:33:48.142950+00:00",
    "session_id": "90f6242e-7dae-494f-a919-e47b0bd8815e"
  }
}
```
Second request:
```json
{
  "user_id": "junaid",
  "text": "What time is it?",
  "metadata": {
    "session_id": "90f6242e-7dae-494f-a919-e47b0bd8815e"
  }
}
```
Response:
```json
{
  "user_id": "junaid",
  "reply": "The current time is 2025-04-08 23:34:53 UTC.\n",
  "metadata": {
    "timestamp": "2025-04-08T23:34:54.244633+00:00",
    "session_id": "90f6242e-7dae-494f-a919-e47b0bd8815e"
  }
}
```
Check metadata:
Open http://localhost:8001/ and try this endpoint
- `http://localhost:8001/memories/junaid`
- Expected: `{"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid enjoys coding and scheduling tasks."}`

#### What Happens?
1. Chat Service publishes “ConversationUpdated”.
2. Agent Memory Service updates history and regenerates `user_summary`.

#### VIBE: Try Background Memories Feature you have already implemented
Another Req in same session.
```json
{
  "user_id": "junaid",
  "text": "Tomorrow we will pack for SF?",
  "metadata": {
    "session_id": "90f6242e-7dae-494f-a919-e47b0bd8815e"
  }
}
```

Now ask about it in another session

```json
{
  "user_id": "junaid",
  "text": "Where was I planning to go tommorrow?"
}
```

OUTPUT:
```json
{
  "user_id": "junaid",
  "reply": "Based on our previous conversation, you, Junaid, are planning a trip to San Francisco tomorrow.\n",
  "metadata": {
    "timestamp": "2025-04-08T23:38:02.667521+00:00",
    "session_id": "9ee00bf5-1138-45be-81bc-ea5656a0fdd2"
  }
}
```


### Run the Tests
- `cd chat_service && uv run pytest test_main.py -v`
- `cd agent_memory_service && uv run pytest test_main.py -v`

---

## Step 9: Why Dapr Pub/Sub for DACA?
- **Decoupling**: Asynchronous updates reduce latency.
- **Scalability**: Handles conversation volume efficiently.
- **Dynamic Metadata**: Enhances personalization.

---

## Step 10: Next Steps
Next, we’ll explore Dapr Workflows to orchestrate multi-step processes.

### Exercises
1. Add a “UserRegistered” event to initialize metadata.

---

## Conclusion
In this tutorial, we integrated Dapr’s Pub/Sub Messaging building block into our microservices, enabling asynchronous, event-driven communication. This aligns with DACA’s scalable, event-driven goals. Next up: Dapr Workflows!