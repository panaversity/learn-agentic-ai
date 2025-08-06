# [Managing Stateful Interactions with Dapr Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)

Welcome to the tenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we enhance the microservices from **09_dapr_secrets_management** by integrating Dapr’s **Actors** building block using the `dapr-ext-fastapi` extension. 

In Tutorial 09, the Chat Service used a Dapr Workflow to orchestrate message processing, fetching metadata and history from the Agent Memory Service, which introduced latency and statelessness per request. Here, we’ll introduce a `UserSessionActor` to encapsulate per-user conversation state and behavior, replacing the workflow’s external history dependency with a local, stateful actor. This leverages the actor pattern’s focus on independent, single-threaded units of computation, improving scalability and personalization. Let’s dive in!

---

## What You’ll Learn
- How Dapr’s Actors implement the Virtual Actor pattern for stateful, distributed entities.
- Defining a `UserSessionActor` to manage conversation history.
- Using `dapr-ext-fastapi` to integrate actors with FastAPI.
- Updating the Chat Service to invoke actor methods directly, retaining Pub/Sub for Agent Memory Service updates.
- Running and testing microservices with Dapr Actors.

## Reading Resources
- [Getting Started](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [Actors Overview](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/)
- [Actor Lifetime](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-features-concepts/#actor-lifetime)
- [Actors API Reference](https://docs.dapr.io/reference/api/actors_api/)
- [Dapr Python SDK FastAPI Integration](https://docs.dapr.io/developing-applications/sdks/python/python-fastapi/)

---

## Prerequisites
- Completion of **09_dapr_secrets_management** (Chat Service with Workflows and Secrets Management, Agent Memory Service with Pub/Sub).
- Dapr CLI and runtime installed (v1.15+, per **04_dapr_theory_and_cli**).
- Docker installed (for Dapr sidecars and Redis).
- Python 3.12+ with `uv` for dependency management.
- A Gemini API key (managed via Dapr Secrets Management).
- Install `dapr-ext-fastapi`: `uv add dapr-ext-fastapi`.

---

## Step 1: Recap of Tutorial 09
In **09_dapr_secrets_management**, we built:
- **Chat Service**: Uses a Dapr Workflow to fetch metadata and history from the Agent Memory Service, generate replies with Gemini (`AsyncOpenAI`), and publish “ConversationUpdated” events via Pub/Sub. The Gemini API key is retrieved from a secrets store.
- **Agent Memory Service**: Subscribes to the `conversations` topic, updates history, and regenerates `user_summary`.

### Current Limitations
- **Stateless Workflow**: Each message triggers a workflow that fetches state externally, lacking local persistence.
- **Latency and Coupling**: Service Invocation to Agent Memory Service adds overhead and dependency.
- **Scalability**: Workflow orchestration scales less efficiently than distributed, stateful entities for per-user sessions.

### Actors in Dapr
Dapr’s Actors follow the Virtual Actor pattern:
- **Unit of Computation**: Self-contained, single-threaded units processing messages sequentially.
- **State and Behavior**: Each actor instance (e.g., per user) encapsulates state (e.g., conversation history) and logic, persisted by Dapr.
- **Scalability**: Distributed across a cluster, managed by Dapr for activation and failover.
- **Virtual Nature**: Activated on demand, garbage-collected when idle, with state outliving in-memory lifetime.

### Actors vs. Workflows
- **Actors**: Ideal for isolated, stateful entities (e.g., user sessions) with low-latency, single-threaded access.
- **Workflows**: Suited for orchestrating multi-step processes across services (e.g., onboarding flows).
- In DACA, actors better fit per-user session management than workflows.

### Goal
Replace the workflow with a `UserSessionActor` for local conversation history, using `dapr-ext-fastapi` for seamless FastAPI integration.

### Project Structure
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── user_session_actor.py  # New
│   ├── pyproject.toml
│   └── uv.lock
├── agent_memory_service/
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   └── uv.lock
├── components/
│   ├── pubsub.yaml
│   ├── statestore.yaml
│   ├── subscriptions.yaml
│   └── secretstore.yaml
├── secrets.json
└── README.md
```

---

## Step 2: Why Use Dapr Actors?
Actors suit DACA’s chat scenario because:
- **Many Independent Units**: Each user session is an isolated unit of state and logic.
- **Single-Threaded Access**: Ensures safe, sequential processing per user.
- **Scalability**: Dapr distributes actors efficiently across nodes.
- **State Persistence**: Survives restarts via Dapr’s state store.

---

## Step 3: Configure Dapr Actor Runtime
Actors require a state store with actor support. Update `statestore.yaml`:
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
    value: "true"  # Enable actor state
```

---

## Step 4: Implement the UserSessionActor with FastAPI
### Step 4.1: Create `chat_service/user_session_actor.py`
```bash
touch chat_service/user_session_actor.py
```
Edit `chat_service/user_session_actor.py`:
```python
import logging
from dapr.actor import Actor
from dapr.actor.actor_interface import ActorInterface, actormethod

class UserSessionActorInterface(ActorInterface):
    @actormethod(name="AddMessage")
    async def add_message(self, message_data: dict) -> None:
        ...

    @actormethod(name="GetConversationHistory")
    async def get_conversation_history(self) -> list[dict] | None:
        ...

class UserSessionActor(Actor, UserSessionActorInterface):
    def __init__(self, ctx, actor_id):
        super(UserSessionActor, self).__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            history = await self._state_manager.get_state(self._history_key)
            if history is None:  # State doesn’t exist yet
                logging.info(f"State not found for {self._history_key}, initializing")
                await self._state_manager.set_state(self._history_key, [])
            else:
                logging.info(f"State found for {self._history_key}: {history}")
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate for {self._history_key}: {e}")
            # Ensure state is initialized even if get_state fails
            await self._state_manager.set_state(self._history_key, [])

    async def add_message(self, message_data: dict) -> None:
        """Add a message and reply to history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            current_history.append(message_data)
            if len(current_history) > 5:  # Limit to last 5 messages
                current_history = current_history[-5:]
            await self._state_manager.set_state(self._history_key, current_history)
        except Exception as e:
            logging.error(f"Error adding message for {self._history_key}: {e}")
            raise

    async def get_conversation_history(self) -> list[dict]:
        """Retrieve conversation history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history for {self._history_key}: {e}")
            return []
```

### Step 4.2: Create `chat_service/utils.py`
```python
import os
import httpx
from typing import ClassVar
from dataclasses import dataclass
from fastapi import HTTPException


# Configuration
@dataclass
class Settings:
    DAPR_GRPC_PORT: ClassVar[str] = os.getenv("DAPR_GRPC_PORT", "50001")  # Default gRPC port
    DAPR_HTTP_PORT: ClassVar[str] = os.getenv("DAPR_HTTP_PORT", "3500")
    APP_PORT: ClassVar[str] = os.getenv("APP_PORT", "8010")
    CORS_ORIGINS: ClassVar[list[str]] = ["http://localhost:3000"]
    MODEL_NAME: ClassVar[str] = "gemini-1.5-flash"
    MODEL_BASE_URL: ClassVar[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()


# Fetch Gemini API key from Dapr secrets store (using HTTP API)
async def get_gemini_api_key() -> str:
    dapr_url = f"http://localhost:{settings.DAPR_HTTP_PORT}/v1.0/secrets/secretstore/gemini-api-key"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            secret_data = response.json()
            return secret_data["gemini-api-key"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve Gemini API key: {e}")

```

### Step 4.3: Update `chat_service/main.py`
Use `dapr-ext-fastapi` for actor integration: i.e: 
```bash uv add dapr-ext-fastapi```

```python
import httpx
from typing import cast, List, Dict, Any
from uuid import uuid4
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dapr.ext.fastapi import DaprActor
from dapr.actor.runtime.runtime import ActorRuntime
from dapr.actor.runtime.config import ActorRuntimeConfig, ActorTypeConfig, ActorReentrancyConfig

from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata
from user_session_actor import UserSessionActor
from utils import get_gemini_api_key, settings

external_client = None
model = None

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0"
)

config = ActorRuntimeConfig()
config.update_actor_type_configs(
    [ActorTypeConfig(actor_type=UserSessionActor.__name__, reentrancy=ActorReentrancyConfig(enabled=True))]
)
ActorRuntime.set_actor_config(config)

actor = DaprActor(app)

@app.on_event("startup")
async def startup():
    global external_client, model
    print("Starting up...")
    await actor.register_actor(UserSessionActor)
    print(f"Registered actor: {UserSessionActor.__name__}")
    try:
        api_key = await get_gemini_api_key()
        external_client = AsyncOpenAI(api_key=api_key, base_url=settings.MODEL_BASE_URL)
        model = OpenAIChatCompletionsModel(model=settings.MODEL_NAME, openai_client=external_client)
        print("Initialized AI client")
    except Exception as e:
        print(f"Error initializing AI client: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_run_config():
    if model and external_client:
        return RunConfig(
            model=model,
            model_provider=cast(ModelProvider, external_client),
            tracing_disabled=True
        )
    return None

@function_tool
def get_current_time() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

async def publish_conversation_event(
    user_id: str,
    session_id: str,
    user_text: str,
    reply_text: str,
    dapr_port: int = 3500
) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/conversations"
    event_data = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": "ConversationUpdated",
        "user_message": user_text,
        "assistant_reply": reply_text
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            print(f"Published ConversationUpdated event for {user_id}, session {session_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to publish event: {e}")

async def get_memory_data(user_id: str, dapr_port: int = 3500) -> Dict[str, str]:
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            memory_response = await client.get(metadata_url)
            memory_response.raise_for_status()
            return memory_response.json()
        except Exception as e:
            print(f"Failed to fetch metadata: {e}")
            return {
                "name": user_id,
                "preferred_style": "casual",
                "user_summary": f"{user_id} is a new user."
            }

async def generate_reply(user_id: str, message_text: str, history: List[Dict[str, str]]) -> str:
    try:
        memory_data = await get_memory_data(user_id)
        name = memory_data.get("name", user_id)
        style = memory_data.get("preferred_style", "casual")
        summary = memory_data.get("user_summary", f"{name} is a new user.")
        
        history_summary = "No prior conversation." if not history else "\n".join(
            f"User: {entry.get('user_text', '')}\nAssistant: {entry.get('reply_text', '')}" for entry in history[-3:]
        )
        
        instructions = (
            f"You are a helpful chatbot. Respond in a {style} way. "
            f"If the user asks for the time, use the get_current_time tool. "
            f"The user's name is {name}. User summary: {summary}. "
            f"Conversation history:\n{history_summary}"
        )
        
        config = get_run_config()
        if not config:
            return "I'm sorry, but I'm not fully initialized yet. Please try again in a moment."
            
        chat_agent = Agent(name="ChatAgent", instructions=instructions, tools=[get_current_time], model=model)
        result = await Runner.run(chat_agent, input=message_text, run_config=config)
        return result.final_output
    except Exception as e:
        print(f"Error generating reply: {e}")
        return "I'm sorry, I encountered an error while processing your message. Please try again later."

async def get_conversation_history(user_id: str, dapr_port: int = 3500) -> List[Dict[str, Any]]:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/GetConversationHistory"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Calling Dapr endpoint for history: {url}")
            response = await client.post(url, json={})
            response.raise_for_status()
            history = response.json()
            print(f"Received history for {user_id}: {history}")
            return history if history is not None else []
        except httpx.HTTPStatusError as e:
            print(f"Error getting conversation history: {e}")
            print(f"Status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            if e.response.status_code == 404 or "ERR_ACTOR_INSTANCE_MISSING" in e.response.text:
                print(f"Actor instance missing for {user_id}, returning empty list")
                return []
            raise
        except ValueError as e:
            print(f"Error decoding history JSON: {e}")
            return []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            raise

async def add_message(user_id: str, message_data: Dict[str, Any], dapr_port: int = 3500) -> None:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/AddMessage"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"Calling Dapr endpoint to add message: {url}")
            headers = {"Content-Type": "application/json"}
            response = await client.post(url, json=message_data, headers=headers)
            response.raise_for_status()
            print(f"Message added for {user_id}: {message_data}")
        except httpx.HTTPStatusError as e:
            print(f"Error adding message: {e}")
            print(f"Status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")
        except Exception as e:
            print(f"Error adding message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Dict[str, Any])
async def chat(message: Message) -> Dict[str, Any]:
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    
    try:
        history = await get_conversation_history(message.user_id)
        reply_text = await generate_reply(message.user_id, message.text, history)
        await add_message(message.user_id, {"user_text": message.text, "reply_text": reply_text})
        await publish_conversation_event(message.user_id, session_id, message.text, reply_text, int(settings.DAPR_HTTP_PORT))
        
        return {
            "user_id": message.user_id,
            "reply": reply_text,
            "metadata": Metadata(session_id=session_id)
        }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {e}")
```

---

## Step 5: Verify Agent Memory Service
No changes needed—it updates via Pub/Sub events.

---

## Step 6: Run the Microservices
### Install Dependencies
```bash
deactivate
cd chat_service
uv venv
source .venv/bin/activate
uv sync
uv add dapr-ext-fastapi
```

### Start Agent Memory Service
```bash
cd ../agent_memory_service
uv venv
source .venv/bin/activate
uv sync
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start Chat Service
```bash
cd ../chat_service
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 --resources-path ../components --log-level debug -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Verify
```bash
dapr list
```

---

## Step 7: Test the Microservices
### Initialize Metadata
```bash
curl -X POST http://localhost:8001/memories/junaid/initialize -H "Content-Type: application/json" -d '{"name": "Junaid", "preferred_style": "casual", "user_summary": "Junaid like books."}'
```

### Test Chat
#### First Message
```bash
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "Hi there"}'
```
Expected:
```json
{
  "user_id": "junaid",
  "reply": "Greetings, Junaid! No prior conversation.",
  "metadata": {"timestamp": "...", "session_id": "..."}
}
```

#### Second Message
```bash
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "What did I say before?"}'
```
Expected reply references “Hi there.”

{"user_id":"junaid","reply":"Hey Junaid! Your last message was \"Hi there\".\n","metadata":{"timestamp":"2025-04-09T21:29:36.796866+00:00","session_id":"6b285dc2-4e9c-4615-a899-95ce18bf9080"}}%                                                             

---

## Step 8: Why Dapr Actors for DACA?
- **Stateful Local History**: Reduces latency and external dependencies.
- **Scalability**: Distributes session state across actors.
- **Personalization**: Enhances replies with real-time history.
- **FastAPI Integration**: `dapr-ext-fastapi` simplifies actor setup.

---

## Step 9: Next Steps
Next: **11_dapr_observability** for monitoring.

### Exercises
1. Add a `clear_history` method to the actor.
2. Use actor timers to periodically summarize history.
3. Explore `dapr dashboard` to inspect actor state.

---

## Conclusion
We’ve integrated Dapr Actors with FastAPI using `dapr-ext-fastapi`, introducing a `UserSessionActor` for stateful conversation history. This enhances DACA’s scalability and personalization, aligning with the actor pattern’s strengths. Onward to observability!