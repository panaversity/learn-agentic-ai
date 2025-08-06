# [Containerizing DACA Microservices with Docker and Dapr](https://docs.dapr.io/operations/hosting/self-hosted/self-hosted-with-docker/#run-app-as-a-process-and-sidecar-as-a-docker-container)

Welcome to the thirteenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll containerize the **Chat Service** and **Agent Memory Service** from **07_dapr_pubsub_messaging** using **Docker**. We’ll create optimized Dockerfiles, build container images, and run them with **Dapr sidecars** in a custom Docker network to maintain pub/sub messaging functionality. This prepares us for **Docker Compose** in Tutorial 14 while ensuring consistency and scalability.

---

## What You’ll Learn

- How to create optimized Dockerfiles for the Chat Service and Agent Memory Service.
- Building lightweight container images with the latest Python and Dapr versions.
- Setting up a custom Docker network for service communication.
- Running containerized services with Dapr sidecars for pub/sub and state management.
- Verifying the setup with tests from **07_dapr_pubsub_messaging**.

---

## Prerequisites

- **Completion of Tutorial 7**: Chat Service and Agent Memory Service working with Dapr pub/sub and state management from **07_dapr_pubsub_messaging**.
- **Docker**: Install [Docker](https://docs.docker.com/get-docker/) and ensure Docker Desktop (or the Docker daemon) is running.
- **Dapr CLI**: Install the latest Dapr CLI (v1.15 as of April 2025, or newer) via [Dapr’s guide](https://docs.dapr.io/getting-started/install-dapr-cli/). (Optional for this tutorial since we’re running Dapr in containers.)
- **Python 3.12+**: Required for local development (though containers handle runtime).
- **Gemini API Key**: Set in `chat_service/.env` and `agent_memory_service/.env` as `GEMINI_API_KEY=<your-key>`.

---

## Step 1: Recap of the Current Setup

In **07_dapr_pubsub_messaging**, we built an event-driven system:

- **Chat Service**:
  - Handles user messages, fetches metadata/history via Dapr service invocation.
  - Uses a Gemini-powered LLM to generate replies.
  - Publishes “ConversationUpdated” events to a `conversations` topic via Dapr pub/sub.
  - Runs on port `8080`.
- **Agent Memory Service**:
  - Stores user metadata (`name`, `preferred_style`, `user_summary`) and conversation history in a Dapr state store (Redis).
  - Subscribes to the `conversations` topic to update history and generate `user_summary` using an LLM.
  - Runs on port `8001`.

### Current Limitations

- **Non-Containerized**: Services run on the host with `uv run uvicorn`, risking inconsistencies.
- **Dependency Management**: Local installs may conflict.
- **Production Readiness**: Without containers, scaling or deployment is challenging.

### Goal for This Tutorial

- Containerize both services with separate app and Dapr sidecar containers.
- Use a custom Docker network for communication.
- Verify pub/sub and state management functionality.

### Project Structure

```
fastapi-daca-tutorial/
├── chat_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env
├── agent_memory_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env
├── components/
│   ├── subscriptions.yaml
│   ├── statestore.yaml
│   ├── pubsub.yaml
└── README.md
```

---

### Why Containerize with Docker and Dapr?

- **Consistency**: Ensures identical environments across development and production.
- **Isolation**: Encapsulates dependencies, avoiding conflicts.
- **Scalability**: Simplifies orchestration (e.g., Kubernetes).
- **Dapr Integration**: Sidecars provide seamless pub/sub and state management.

This approach aligns with Dapr’s recommended sidecar pattern, preparing us for real-world deployments.

---

## Step 2: Update Code and Components

To ensure containers communicate correctly in a custom Docker network:

- Update `chat_service/main.py` and `agent_memory_service/main.py` to use sidecar container names (e.g., `chat-service-dapr`, `agent-memory-service-dapr`).
- Update `components/statestore.yaml` and `pubsub.yaml` to use `redis:6379`.

### Step 2.1: Update Chat Service Code

Edit `chat_service/main.py` to replace `localhost` with container names.

**Before** (snippet):

```python
async def publish_conversation_event(user_id: str, session_id: str, user_text: str, reply_text: str, dapr_port: int = 3500):
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/conversations"
    # ...
metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{message.user_id}"
history_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/conversations/{session_id}"
```

**After** (full file as provided earlier):

- Change `publish_conversation_event` to use `http://chat-service-dapr:{dapr_port}`.
- Change `metadata_url` to `http://agent-memory-service-dapr:3501`.
- Change `history_url` to `http://agent-memory-service-dapr:3501`.

**Instructions**:

1. Open `chat_service/main.py`.
2. Full Code:

```python
import os
import httpx
import logging
from typing import cast
from dotenv import load_dotenv
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

from models import Message, Response, Metadata, ConversationEntry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set in .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=cast(
    ModelProvider, external_client), tracing_disabled=True)

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


async def publish_conversation_event(user_id: str, session_id: str, user_text: str, reply_text: str):
    # Get Dapr hostname from environment variable or use default
    dapr_url = f"http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations"

    logger.info(f"Publishing to Dapr URL: {dapr_url}")

    event_data = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": "ConversationUpdated",
        "user_message": user_text,
        "assistant_reply": reply_text
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            logger.info(
                f"Published ConversationUpdated event for {user_id}, session {session_id}")
        except httpx.ConnectError as e:
            logger.error(
                f"Connection error with Dapr sidecar: {e}. Check if Dapr sidecar is running and accessible at {dapr_url}")
            # Continue execution instead of failing completely
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event: {e}")
            # Continue execution instead of failing completely


@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}


@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    # Use existing session_id from metadata if provided, otherwise generate a new one
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(
        uuid4())
    dapr_port = int(os.getenv("DAPR_HTTP_PORT", "3501"))

    # Get Dapr hostname from environment variable or use default
    memory_service_host = os.getenv(
        "MEMORY_SERVICE_HOST", "agent-memory-service-dapr")
    logger.info(f"Using memory service at: {memory_service_host}:{dapr_port}")

    # Fetch user metadata
    metadata_url = f"http://{memory_service_host}:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{message.user_id}"
    logger.info(f"Fetching metadata from {metadata_url}")

    memory_data = {"name": message.user_id, "preferred_style": "casual",
                   "user_summary": f"{message.user_id} is a new user."}
    history = []

    # Try to get metadata, but use defaults if service is unavailable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                memory_response = await client.get(metadata_url)
                memory_response.raise_for_status()
                memory_data = memory_response.json()
                logger.info(
                    f"Successfully fetched metadata for {message.user_id}")
            except httpx.ConnectError as e:
                logger.error(
                    f"Connection error to memory service: {e}. Using default metadata.")
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Failed to fetch metadata: {e}. Using default metadata.")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching metadata: {e}. Using default metadata.")

    # Fetch conversation history
    history_url = f"http://{memory_service_host}:{dapr_port}/v1.0/invoke/agent-memory-service/method/conversations/{session_id}"
    logger.info(f"Fetching history from {history_url}")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                history_response = await client.get(history_url)
                history_response.raise_for_status()
                history = history_response.json()["history"]
                logger.info(
                    f"Successfully fetched history for session {session_id}")
            except httpx.ConnectError as e:
                logger.error(
                    f"Connection error fetching history: {e}. Using empty history.")
            except httpx.HTTPStatusError:
                logger.info(f"No prior history for session {session_id}")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching history: {e}. Using empty history.")

    name = memory_data.get("name", message.user_id)
    style = memory_data.get("preferred_style", "casual")
    summary = memory_data.get("user_summary", f"{name} is a new user.")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    personalized_instructions = (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user's name is {name}. User summary: {summary}. {context}"
    )
    # clean history of timestamps after a copy
    current_user_message = ConversationEntry(role="user", content=message.text)
    history.append(current_user_message.model_dump())
    # Remove timestamps from each entry, instead of filtering out entries that have them
    history_without_timestamps = [
        {k: v for k, v in entry.items() if k != "timestamp"} for entry in history
    ]

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],
        model=model
    )

    result = await Runner.run(chat_agent, input=history_without_timestamps, run_config=config)
    reply_text = result.final_output

    # Try to publish, but don't fail if Dapr is unavailable
    try:
        await publish_conversation_event(message.user_id, session_id, message.text, reply_text)
    except Exception as e:
        logger.error(f"Failed to publish conversation event: {e}")

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata(session_id=session_id)
    )
```

### Step 2.2: Update Agent Memory Service Code

Edit `agent_memory_service/main.py` to use `agent-memory-service-dapr`.

**Before** (snippet):

```python
async def get_user_metadata(user_id: str, dapr_port: int = 3501) -> dict:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/user:{user_id}"
async def set_user_metadata(user_id: str, metadata: dict, dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
async def get_conversation_history(session_id: str, dapr_port: int = 3501) -> list[dict]:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/session:{session_id}"
async def set_conversation_history(session_id: str, history: list[dict], dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
```

**After** (full file as provided earlier):

- Update all Dapr URLs to `http://agent-memory-service-dapr:{dapr_port}`.

**Instructions**:

1. Open `agent_memory_service/main.py`.
2. Full Code:

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
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_user_metadata(user_id: str, dapr_port: int = 3501) -> dict:
    dapr_url = f"http://agent-memory-service-dapr:{dapr_port}/v1.0/state/statestore/user:{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            # Handle 204 No Content response
            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.HTTPStatusError:
            return {}

async def set_user_metadata(user_id: str, metadata: dict, dapr_port: int = 3501) -> None:
    dapr_url = f"http://agent-memory-service-dapr:{dapr_port}/v1.0/state/statestore"
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
    dapr_url = f"http://agent-memory-service-dapr:{dapr_port}/v1.0/state/statestore/session:{session_id}"
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
    dapr_url = f"http://agent-memory-service-dapr:{dapr_port}/v1.0/state/statestore"
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
        return UserMetadata(name=user_id, preferred_style="casual", user_summary=f"{user_id} is a new user.")
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

### Step 2.3: Update Component Files

Update Redis host in `components/` to use the `redis` container.

**`components/statestore.yaml`**:

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
      value: redis:6379
    - name: redisPassword
      value: ""
    - name: actorStateStore
      value: "true"
```

**`components/pubsub.yaml`**:

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
      value: redis:6379
    - name: redisPassword
      value: ""
```

**`components/subscriptions.yaml`**:

- No changes needed (it defines topic and route, no host references).

**Instructions**:

1. Open `components/statestore.yaml` and replace `redisHost` value with `redis:6379`.
2. Open `components/pubsub.yaml` and replace `redisHost` value with `redis:6379`.

## Step 3: Create Optimized Dockerfiles

We’ll use `python:3.12-slim` for lightweight app containers. Dapr sidecars use the official `[daprio/dapr:1.15](https://blog.dapr.io/posts/2025/02/27/dapr-v1.15-is-now-available/)` image.

### Step 3.1: Dockerfile for Chat Service

In `chat_service/`:

```bash
touch chat_service/Dockerfile
```

Edit `chat_service/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock .env /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Create `.dockerignore`:

```
.venv
.mypy_cache
__pycache__
.pytest_cache
```

### Step 3.2: Dockerfile for Agent Memory Service

In `agent_memory_service/`:

```bash
touch agent_memory_service/Dockerfile
```

Edit `agent_memory_service/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock .env /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Create `.dockerignore`:

```
.venv
.mypy_cache
__pycache__
.pytest_cache
```

## Step 4: Build the Container Images

Since we updated `main.py` files, rebuild the images.

### Step 4.1: Build Chat Service Image

```bash
cd chat_service
nerdctl build -t chat-service:latest .
cd ..
```

### Step 4.2: Build Agent Memory Service Image

```bash
cd agent_memory_service
nerdctl build -t agent-memory-service:latest .
cd ..
```

### Step 4.3: Verify Images

```bash
nerdctl images
```

**Expected Output**:

```
REPOSITORY             TAG                       IMAGE ID       CREATED              SIZE
agent-memory-service   latest                    10f5f9e79347   41 seconds ago       431MB
chat-service           latest                    d0924e0b62e5   About a minute ago   430MB
python                 3.12-slim                 85824326bc4a   3 days ago           211MB
```

---

## Step 5: Run Containerized Services with Dapr

Use `dapr-network` and manually start Redis.

### Step 5.1: Create Docker Network

```bash
docker network create dapr-network
```

### Step 5.2: Start Redis

```bash
nerdctl run -d --name redis --network dapr-network -p 6379:6379 redis:latest
```

### Step 5.3: Run Agent Memory Service

From `fastapi-daca-tutorial/`:

1. **App Container**:

   ```bash
   nerdctl run -d --name agent-memory-service-app \
     --network dapr-network \
     -p 8001:8001 \
     agent-memory-service:latest
   ```

2. **Dapr Sidecar**:
   ```bash
   nerdctl run -d \
   --name agent-memory-service-dapr \
   --network dapr-network \
   -p 3501:3501 \
   -v $(pwd)/components:/components \
   daprio/dapr:1.15.1 \
   ./daprd \
   --app-id agent-memory-service \
   --app-port 8001 \
   --dapr-http-port 3501 \
   --log-level debug \
   --components-path /components \
   --app-protocol http \
   --app-channel-address agent-memory-service-app
   ```

### Step 5.4: Run Chat Service

From `fastapi-daca-tutorial/`:

1. **App Container**:

   ```bash
   nerdctl run -d --name chat-service-app \
     --network dapr-network \
     -p 8080:8080 \
     chat-service:latest
   ```

2. **Dapr Sidecar**:
   ```bash
   nerdctl run -d \
   --name chat-service-dapr \
   --network dapr-network \
   -p 3500:3500 \
   -v $(pwd)/components:/components \
   daprio/dapr:1.15.1 \
   ./daprd \
   --app-id chat-service \
   --app-port 8080 \
   --dapr-http-port 3500 \
   --log-level debug \
   --components-path /components \
   --app-protocol http \
   --app-channel-address chat-service-app
   ```

### Step 5.5: Verify Containers

```bash
nerdctl ps
```

**Expected Output**:

```
mjs@Muhammads-MacBook-Pro-3 agent_memory_service % nerdctl ps

CONTAINER ID   IMAGE                         COMMAND                  CREATED          STATUS          PORTS                                            NAMES
949b71c9604c   daprio/dapr:1.15.1            "./daprd --app-id ch…"   4 seconds ago    Up 4 seconds    0.0.0.0:3500->3500/tcp                           chat-service-dapr
cb9532670d84   chat-service:latest           "uv run uvicorn main…"   8 seconds ago    Up 8 seconds    0.0.0.0:8080->8080/tcp                           chat-service-app
a7752bb571c5   daprio/dapr:1.15.1            "./daprd --app-id ag…"   13 seconds ago   Up 13 seconds   0.0.0.0:3501->3501/tcp                           agent-memory-service-dapr
0b96d39e2ccf   agent-memory-service:latest   "uv run uvicorn main…"   18 seconds ago   Up 18 seconds   0.0.0.0:8001->8001/tcp                           agent-memory-service-app
5db9ef8136ee   redis:latest                  "docker-entrypoint.s…"   44 seconds ago   Up 44 seconds   0.0.0.0:6379->6379/tcp                           redis
```

---

## Step 6: Test the Containerized Setup

### Step 6.1: Initialize State

```bash
curl -X POST http://localhost:8001/memories/junaid/initialize \
  -H "Content-Type: application/json" \
  -d '{"name": "Junaid", "preferred_style": "casual", "user_summary": "Junaid is building Agents WorkForce."}'
```

**Expected Output**:

```json
{"status":"success","user_id":"junaid","metadata":{"name":"Junaid","preferred_style":"casual","user_summary":"Junaid is building Agents WorkForce."}}%
```

### Step 6.2: Test Chat Service

First request:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "I need to schedule a coding session."}'
```

**Expected Response**:

```json
{"user_id":"junaid","reply":"Hey Junaid!  Sounds good. What time works best for you?  I can help you figure that out.\n","metadata":{"timestamp":"2025-04-12T04:01:04.035603+00:00","session_id":"98289651-62fb-45eb-804a-21c7ee59384c"}}%
```

Second request (same session):

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "What was my last msg?", "metadata": {"session_id": "98289651-62fb-45eb-804a-21c7ee59384c"}}'
```

**Expected Response**:

```json
{
  "user_id": "junaid",
  "reply": "Your last message was: \"I need to schedule a coding session.\"\n",
  "metadata": {
    "timestamp": "2025-04-12T04:02:03.001332+00:00",
    "session_id": "98289651-62fb-45eb-804a-21c7ee59384c"
  }
}
```

### Step 6.3: Verify Metadata Update

```bash
curl http://localhost:8001/memories/junaid
```

**Expected Output**:

```json
{"name":"Junaid","preferred_style":"casual","user_summary":"Junaid needs to schedule a coding session.\n"}%
```

### Step 6.4: Test Background Memories

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Tomorrow we will pack for SF?", "metadata": {"session_id": "98289651-62fb-45eb-804a-21c7ee59384c"}}'
```

New session:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Where was I planning to go tomorrow?"}'
```

**Expected Response**:

```json
{
  "user_id": "junaid",
  "reply": "Based on our previous conversation, you, Junaid, are planning a trip to San Francisco tomorrow.",
  "metadata": {
    "timestamp": "2025-04-11T12:02:00Z",
    "session_id": "new-uuid"
  }
}
```

### Step 6.5: Check Logs

- Chat Service:

  ```bash
  nerdctl logs chat-service-app
  ```

  **Expected**:

  ```bash
  200 OK"
  INFO:main:Successfully fetched metadata for junaid
  INFO:main:Fetching history from http://agent-memory-service-dapr:3501/v1.0/invoke/agent-memory-service/method/conversations/5cdf5f65-3853-43ff-a1db-e4cb7d901b11
  INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/invoke/agent-memory-service/method/conversations/5cdf5f65-3853-43ff-a1db-e4cb7d901b11 "HTTP/1.1 200 OK"
  INFO:main:Successfully fetched history for session 5cdf5f65-3853-43ff-a1db-e4cb7d901b11
  INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
  INFO:main:Publishing to Dapr URL: http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations
  INFO:httpx:HTTP Request: POST http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations "HTTP/1.1 204 No Content"
  INFO:main:Published ConversationUpdated event for junaid, session 5cdf5f65-3853-43ff-a1db-e4cb7d901b11
  INFO:     192.168.65.1:26287 - "POST /chat/ HTTP/1.1" 200 OK
  mjs@Muhammads-MacBook-Pro-3 fastapi-daca-tutorial %
  ```

- Agent Memory Service:
  ```bash
  nerdctl logs agent-memory-service-app
  ```
  **Expected**:

```
INFO:     172.19.0.6:39566 - "POST /conversations HTTP/1.1" 200 OK
INFO:     192.168.65.1:42786 - "GET /docs HTTP/1.1" 200 OK
INFO:     192.168.65.1:42786 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:98289651-62fb-45eb-804a-21c7ee59384c "HTTP/1.1 200 OK"
INFO:     192.168.65.1:43679 - "GET /conversations/98289651-62fb-45eb-804a-21c7ee59384c HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:     172.19.0.6:58152 - "GET /memories/junaid HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:98289651-62fb-45eb-804a-21c7ee59384c "HTTP/1.1 200 OK"
INFO:     172.19.0.6:58152 - "GET /conversations/98289651-62fb-45eb-804a-21c7ee59384c HTTP/1.1" 200 OK
INFO:main:Event validation: type=ConversationUpdated, user_id=junaid, session_id=98289651-62fb-45eb-804a-21c7ee59384c, user_message=What was my last msg?, assistant_reply=Your last message was: "I need to schedule a coding session."

INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:98289651-62fb-45eb-804a-21c7ee59384c "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored conversation history for session 98289651-62fb-45eb-804a-21c7ee59384c
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored metadata for junaid: {'name': 'Junaid', 'preferred_style': 'casual', 'user_summary': 'Junaid needs to schedule a coding session.\n'}
Received event: {'data': {'assistant_reply': 'Your last message was: "I need to schedule a coding session."\n', 'event_type': 'ConversationUpdated', 'session_id': '98289651-62fb-45eb-804a-21c7ee59384c', 'user_id': 'junaid', 'user_message': 'What was my last msg?'}, 'datacontenttype': 'application/json', 'id': 'f81f3caf-bc07-4866-8258-82fff5e15f47', 'pubsubname': 'pubsub', 'source': 'chat-service', 'specversion': '1.0', 'time': '2025-04-12T04:02:02Z', 'topic': 'conversations', 'traceid': '00-00000000000000000000000000000000-0000000000000000-00', 'traceparent': '00-00000000000000000000000000000000-0000000000000000-00', 'tracestate': '', 'type': 'com.dapr.event.sent'}
INFO:     172.19.0.6:58152 - "POST /conversations HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:     192.168.65.1:55010 - "GET /memories/junaid HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:     172.19.0.6:41924 - "GET /memories/junaid HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:98289651-62fb-45eb-804a-21c7ee59384c "HTTP/1.1 200 OK"
INFO:     172.19.0.6:41924 - "GET /conversations/98289651-62fb-45eb-804a-21c7ee59384c HTTP/1.1" 200 OK
INFO:main:Event validation: type=ConversationUpdated, user_id=junaid, session_id=98289651-62fb-45eb-804a-21c7ee59384c, user_message=Tomorrow we will pack for SF?, assistant_reply=Okay, cool!  Packing for San Francisco tomorrow.  Anything specific you need to remember to pack?

INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:98289651-62fb-45eb-804a-21c7ee59384c "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored conversation history for session 98289651-62fb-45eb-804a-21c7ee59384c
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored metadata for junaid: {'name': 'Junaid', 'preferred_style': 'casual', 'user_summary': 'Junaid needs to schedule a coding session and is packing for a trip to San Francisco.\n'}
Received event: {'data': {'assistant_reply': 'Okay, cool!  Packing for San Francisco tomorrow.  Anything specific you need to remember to pack?\n', 'event_type': 'ConversationUpdated', 'session_id': '98289651-62fb-45eb-804a-21c7ee59384c', 'user_id': 'junaid', 'user_message': 'Tomorrow we will pack for SF?'}, 'datacontenttype': 'application/json', 'id': 'b5269213-676e-4d1c-999e-be7b61a0efb8', 'pubsubname': 'pubsub', 'source': 'chat-service', 'specversion': '1.0', 'time': '2025-04-12T04:02:40Z', 'topic': 'conversations', 'traceid': '00-00000000000000000000000000000000-0000000000000000-00', 'traceparent': '00-00000000000000000000000000000000-0000000000000000-00', 'tracestate': '', 'type': 'com.dapr.event.sent'}
INFO:     172.19.0.6:41924 - "POST /conversations HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:     172.19.0.6:41924 - "GET /memories/junaid HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:5cdf5f65-3853-43ff-a1db-e4cb7d901b11 "HTTP/1.1 204 No Content"
INFO:     172.19.0.6:41924 - "GET /conversations/5cdf5f65-3853-43ff-a1db-e4cb7d901b11 HTTP/1.1" 200 OK
INFO:main:Event validation: type=ConversationUpdated, user_id=junaid, session_id=5cdf5f65-3853-43ff-a1db-e4cb7d901b11, user_message=Where was I planning to go tomorrow?, assistant_reply=Hey Junaid!  Looks like you're heading to San Francisco tomorrow!  Safe travels!

INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/session:5cdf5f65-3853-43ff-a1db-e4cb7d901b11 "HTTP/1.1 204 No Content"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored conversation history for session 5cdf5f65-3853-43ff-a1db-e4cb7d901b11
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
INFO:main:Stored metadata for junaid: {'name': 'Junaid', 'preferred_style': 'casual', 'user_summary': 'Junaid is planning a trip to San Francisco tomorrow.\n'}
Received event: {'data': {'assistant_reply': "Hey Junaid!  Looks like you're heading to San Francisco tomorrow!  Safe travels!\n", 'event_type': 'ConversationUpdated', 'session_id': '5cdf5f65-3853-43ff-a1db-e4cb7d901b11', 'user_id': 'junaid', 'user_message': 'Where was I planning to go tomorrow?'}, 'datacontenttype': 'application/json', 'id': '13e97c18-611e-4e9b-a470-6bad9c528f77', 'pubsubname': 'pubsub', 'source': 'chat-service', 'specversion': '1.0', 'time': '2025-04-12T04:02:47Z', 'topic': 'conversations', 'traceid': '00-00000000000000000000000000000000-0000000000000000-00', 'traceparent': '00-00000000000000000000000000000000-0000000000000000-00', 'tracestate': '', 'type': 'com.dapr.event.sent'}
INFO:     172.19.0.6:41924 - "POST /conversations HTTP/1.1" 200 OK
INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
INFO:     192.168.65.1:59600 - "GET /memories/junaid HTTP/1.1" 200 OK
mjs@Muhammads-MacBook-Pro-3 fastapi-daca-tutorial %
```

---

## Step 7: Benefits of Containerization for DACA

- **Consistency**: Uniform environments across setups.
- **Isolation**: Dependency conflicts eliminated.
- **Scalability**: Ready for orchestration.
- **Event-Driven Integrity**: Dapr sidecars ensure pub/sub works seamlessly.

---

## Step 8: Next Steps

In **Tutorial 14**, we’ll use **Docker Compose** to streamline this multi-container setup.

### Optional Exercises

1. **Push to Docker Hub**: `docker tag chat-service:latest yourusername/chat-service:latest && docker push yourusername/chat-service:latest`
2. **Health Checks**: Add `HEALTHCHECK CMD curl -f http://localhost:8080/ || exit 1` to Dockerfiles.

---

## Step 9: Conclusion

We’ve containerized the Chat Service and Agent Memory Service using separate app and Dapr sidecar containers, fixed previous errors by using `./daprd`, and set up a custom Docker network. The setup mirrors production best practices while remaining beginner-friendly, verified by Tutorial 7’s tests. Next, we’ll simplify this with Docker Compose!
