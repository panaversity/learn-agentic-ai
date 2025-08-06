# Integrating [Relational DB with Dapr StateStore](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-cockroachdb/) and [SQLModel](https://sqlmodel.tiangolo.com/) using CockroachDB Serverless

Welcome to the seventeenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! Building on **15_dapr_docker_compose**, we’re diving deep into **databases** by replacing **Redis**’s in-memory state with **CockroachDB Serverless**. We’ll use **Dapr’s state store** to save **LLM-generated memories** (e.g., user summaries) and **SQLModel** to manage **conversation history** in a relational table. **Redis** stays for pub/sub, preserving the simple, event-driven flow of Tutorial 15. With a clean Docker Compose setup and proper container networking, this tutorial focuses on making your chatbot’s memory durable and queryable using **CockroachDB** and **SQLModel**. Ready to level up your DACA app? Let’s climb! 🚀

---

## What You’ll Learn

- Set up **CockroachDB Serverless** for Dapr and SQLModel.
- Configure **Dapr’s state store** to save LLM-generated memories in CockroachDB.
- Use **SQLModel** to store and query conversation history in CockroachDB.
- Update **Chat Service** to fetch memories and history from **Agent Memory Service** using proper Docker networking.
- Run the application with Docker Compose, ensuring robust container communication.
- Test **CockroachDB**’s state store and SQLModel tables to verify persistence.

## Prerequisites

- Completed **15_dapr_docker_compose** (Chat Service, Agent Memory Service, Redis, Dapr sidecars).
- **Docker** and **Docker Desktop** installed ([Docker installation guide](https://docs.docker.com/get-docker/)).
- **Python 3.12+** for local development (containers handle runtime).
- **Gemini API Key** stored in `chat_service/.env` and `agent_memory_service/.env` as `GEMINI_API_KEY=<your-key>`.
- **CockroachDB Serverless** account (we’ll guide you through setup).
- Basic familiarity with Python, Dapr, and Docker networking.

---

## Step 1: Why Two Databases?

We’re upgrading from **Redis**’s in-memory state to a dual-database setup:

- **CockroachDB Serverless**:
  - **Dapr State Store**: Stores **LLM-generated memories** (e.g., `metadata-junaid: {"name": "Junaid", "user_summary": "..."}`) in the `dapr_state` table, offering durable key-value storage.
  - **SQLModel**: Stores **conversation history** (e.g., `user_id`, `session_id`, `message`, `reply`, `timestamp`) in the `conversation` table, enabling relational queries like `SELECT * FROM conversation WHERE user_id = 'junaid'`.
- **Redis**: Handles pub/sub for `ConversationUpdated` events, keeping messaging fast and decoupled, just like Tutorial 15.

**Why two?** Redis excels at events but isn’t ideal for persistent or relational data. **CockroachDB** provides durability (state) and query power (SQLModel), making our chatbot robust while maintaining Tutorial 15’s simplicity.

---

## Step 2: Set Up CockroachDB Serverless

**CockroachDB Serverless** is a managed, PostgreSQL-compatible SQL database with a free tier (5 GiB storage, 50M Request Units as of April 2025), perfect for our cloud-native DACA app.

### Step 2.1: Sign Up

1. Visit [CockroachDB Cloud](https://cockroachlabs.cloud).
2. Sign up for a free account (no credit card needed).
3. Verify your email.

### Step 2.2: Create a Cluster

1. Log in to the CockroachDB Cloud Console.
2. Click **Create Cluster**.
3. Choose **Basic** (free tier).
4. Select a cloud provider (e.g., AWS) and region (e.g., `us-east-1`).
5. Name the cluster (e.g., `daca-cluster`).
6. Click **Create Cluster** (takes ~1 minute).

### Step 2.3: Create Database and User

1. Go to your cluster’s **Overview** page.
2. Click **Connect**.
3. Create a SQL user (e.g., `daca_user`) and set a password.
4. Copy the connection string (e.g., `'postgresql://daca_user:<password>@<cluster-host>:26257/defaultdb?...'`).
   ```
   postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full
   ```
---

## Step 3: Project Structure

Here’s how your project should look:

```
fastapi-daca-tutorial/
├── chat_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env
│   ├── .dockerignore
├── agent_memory_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env
│   ├── .dockerignore
├── components/
│   ├── cockroachdb.yaml
│   ├── pubsub.yaml
│   ├── subscriptions.yaml
├── compose.yml
└── README.md
```

---

## Step 4: Configure Dapr for CockroachDB

We’ll configure **Dapr** to use **CockroachDB** as the state store for memories, keeping **Redis** for pub/sub.

### Step 4.1: Create CockroachDB Component

Create `components/cockroachdb.yaml` and remove `statestore.yaml`:

```bash
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.cockroachdb
  version: v1
  metadata:
  - name: connectionString
    value: postgresql://muhammad:@daca.cockroachlabs.cloud:26/ddb?sslmode=verify-full
  - name: schema
    value: "public"
  - name: tableName
    value: "dapr_state"
  - name: cleanupIntervalInSeconds
    value: "300"
  - name: skipCreateTable
    value: "true"
```

- Replace `<password>`, `<cluster-host>` with your CockroachDB details.
- This sets up `dapr_state` for memories.

Verify:

```bash
ls components/
```

**Expected**:

```
cockroachdb.yaml  pubsub.yaml  subscriptions.yaml
```

---

## Step 5: Set Up the Chat Service

The **Chat Service** receives messages, fetches **memories** (CockroachDB Dapr state) and **conversation history** (CockroachDB SQLModel) from **Agent Memory Service**, generates **Gemini** replies, and publishes events to **Redis**. So there will be no changes here.

Create `chat_service/.env`:

```bash
cat > chat_service/.env <<EOF
GEMINI_API_KEY=<your-gemini-api-key>
EOF
```

- Replace `<your-gemini-api-key>` with your Gemini API key.

---

## Step 6: Set Up the Agent Memory Service

The **Agent Memory Service** stores **memories** in **Dapr’s state store** (CockroachDB), **conversation history** in **SQLModel** (CockroachDB), and updates user summaries with **Gemini** when `ConversationUpdated` events are received.

### Step 6.1: Create `main.py`

Update `agent_memory_service/main.py`:
```python
import os
import logging
import httpx

from typing import cast, List
from dotenv import load_dotenv, find_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from sqlmodel import SQLModel, Session, create_engine, select

from datetime import datetime, timezone
from models import Metadata, ConversationResponse, Conversation

_ = load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentMemoryService")

gemini_api_key = os.getenv("GEMINI_API_KEY")
connection_string = os.getenv("DB_CONNECTION")
if not connection_string or not gemini_api_key:
    raise ValueError(
        "DB_CONNECTION or GEMINI_API_KEY environment variable is not set")

connection_string = connection_string.replace(
    "postgresql://", "cockroachdb+psycopg://")
# Modify the sslmode from verify-full to require for less strict certificate verification
if "sslmode=verify-full" in connection_string:
    connection_string = connection_string.replace(
        "sslmode=verify-full", "sslmode=require")
elif "sslmode=" not in connection_string:
    # If sslmode isn't specified, add it with require
    if "?" in connection_string:
        connection_string += "&sslmode=require"
    else:
        connection_string += "?sslmode=require"

engine = create_engine(connection_string, echo=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating all tables")
    SQLModel.metadata.create_all(engine)
    print("Tables created")
    yield

app = FastAPI(
    title="DACA Agent Memory Service",
    description="A FastAPI-based service for user metadata and conversation history",
    version="0.1.0",
    lifespan=lifespan
)


async def get_user_metadata(user_id: str, dapr_port: int = 3501) -> dict:
    dapr_url = f"http://agent-memory-service-dapr:{dapr_port}/v1.0/state/statestore/user:{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            if response.status_code == 204 or not response.text:
                logger.info(f"No metadata found for {user_id}")
                return {}
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch metadata for {user_id}: {e}")
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
            raise HTTPException(
                status_code=500, detail="Failed to store metadata")


async def generate_user_summary(user_id: str, conversations: List[Conversation]) -> str:
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model="gemini-1.5-flash", openai_client=external_client)
    config = RunConfig(model=model, model_provider=cast(
        ModelProvider, external_client), tracing_disabled=True)

    def get_current_time():
        return datetime.now(timezone.utc).isoformat()

    summary_agent = Agent(
        name="SummaryAgent",
        instructions="Generate a one-sentence summary of the user’s interests or activities based on their conversation history.",
        model=model,
        tools=[function_tool(get_current_time)],
    )

    history = []
    for conv in conversations[-5:]:
        history.append({"role": "user", "content": conv.content})
        history.append({"role": "assistant", "content": conv.content})

    conversation_text = "\n".join(
        [f"{entry['role'].capitalize()}: {entry['content']}" for entry in history]
    ) if history else "No conversation history available."

    prompt = f"History:\n{conversation_text}\nSummary:"

    if not history:
        return f"{user_id} is a new user with no conversation history yet."

    try:
        result = await Runner.run(
            summary_agent,
            input=[{"role": "user", "content": prompt}],
            run_config=config,
        )
        return result.final_output
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"{user_id} is interested in having conversations."


@app.post("/memories/{user_id}/initialize")
async def initialize_metadata(user_id: str, metadata: Metadata):
    await set_user_metadata(user_id, metadata.model_dump())
    return {"status": "success", "user_id": user_id, "metadata": metadata.dict()}


@app.get("/memories/{user_id}", response_model=Metadata)
async def get_metadata(user_id: str):
    metadata = await get_user_metadata(user_id)
    if not metadata:
        return Metadata(name=user_id, preferred_style="casual", user_summary=f"{user_id} is a new user.")
    return Metadata(**metadata)


@app.get("/conversations/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str):
    with Session(engine) as session:
        query = select(Conversation).where(
            Conversation.session_id == session_id
        )
        conversations = session.exec(query).all()
        logger.info(
            f"Conversations retrieved: {len(conversations)} for session {session_id}")
        return ConversationResponse(history=conversations, session_id=session_id, user_id=conversations[0].user_id)


@app.post("/conversations")
async def handle_conversation_updated(event: dict):
    logger.info(f"Received event: {event}")
    event_data = event.get("data", {})
    event_type = event_data.get("event_type")
    user_id = event_data.get("user_id")
    session_id = event_data.get("session_id")
    user_message = event_data.get("user_message")
    assistant_reply = event_data.get("assistant_reply")

    logger.info(
        f"Event validation: type={event_type}, user_id={user_id}, session_id={session_id}, "
        f"user_message={user_message}, assistant_reply={assistant_reply}"
    )

    if event_type != "ConversationUpdated" or not all([user_id, session_id, user_message, assistant_reply]):
        logger.warning(f"Event ignored due to invalid structure: {event_data}")
        return {"status": "ignored"}

    conversation_1 = Conversation(
        user_id=user_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        role="user",
        content=user_message
    )
    conversation_2 = Conversation(
        user_id=user_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        role="assistant",
        content=assistant_reply
    )
    with Session(engine) as session:
        session.add(conversation_1)
        session.add(conversation_2)
        session.commit()
        logger.info(
            f"Stored conversation for session {session_id} in SQLModel")

    with Session(engine) as session:
        conversations = session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()

    metadata = await get_user_metadata(user_id)
    if not metadata:
        metadata = {
            "name": user_id,
            "preferred_style": "casual",
            "user_summary": f"{user_id} is a new user."
        }
    metadata["user_summary"] = await generate_user_summary(user_id, conversations)
    await set_user_metadata(user_id, metadata)

    return {"status": "SUCCESS"}

```

### Step 6.2: Update `models.py`

Create `agent_memory_service/models.py`:

```bash
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Metadata(SQLModel):
    name: str
    preferred_style: str
    user_summary: str

class ConversationEntry(SQLModel):
    role: str
    content: str


class Conversation(ConversationEntry, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationResponse(SQLModel):
    history: list[ConversationEntry] = []
    session_id: str
    user_id: str

```

### Step 6.3: Update Dependencies

```bash
cd agent_memory_service
deactivate
uv venv
source .venv/bin/activate
uv sync
uv add sqlmodel "psycopg[binary]" sqlalchemy-cockroachdb
```


### Step 6.4: Configure `.env`

Create `agent_memory_service/.env`:

```bash
GEMINI_API_KEY=<your-gemini-api-key>
DB_CONNECTION=postgresql://daca_user:<password>@<cluster-host>:26257/daca_db?sslmode=verify-full
```

- Replace `<your-gemini-api-key>`, `<password>`, `<cluster-host>` with your values.

---

## Step 7: Run the Application

### Step 7.1: Start the Application

```bash
docker-compose up
```

### Step 7.2: Verify Services

```bash
docker-compose ps
```

**Expected Output**:

```
NAME                                              COMMAND                  STATE           PORTS
----------------------------------------------------------------------------------------------------------------
fastapi-daca-tutorial_agent-memory-service-app_1   uv run uvicorn main:app -- ...   Up      0.0.0.0:7001->8001/tcp
fastapi-daca-tutorial_agent-memory-service-dapr_1  ./daprd --app-id agent-mem ...   Up      0.0.0.0:3501->3501/tcp
fastapi-daca-tutorial_chat-service-app_1          uv run uvicorn main:app -- ...   Up      0.0.0.0:8080->8080/tcp
fastapi-daca-tutorial_chat-service-dapr_1         ./daprd --app-id chat-serv ...   Up      0.0.0.0:3500->3500/tcp
fastapi-daca-tutorial_redis_1                     docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
```

---

## Step 8: Test the Application

Let’s test the application to verify **CockroachDB** storage, **SQLModel** queries, and **Docker networking**.

### Step 8.1: Initialize Memories

```bash
curl -X POST http://localhost:8001/memories/junaid/initialize \
  -H "Content-Type: application/json" \
  -d '{"name": "Junaid", "preferred_style": "informal", "user_summary": "Junaid is building his Agents WorkForce."}'
```

**Expected Output**:

```json
{
  "status": "success",
  "user_id": "junaid",
  "metadata": {
    "name": "Junaid",
    "preferred_style": "casual",
    "user_summary": "Junaid is building Agents WorkForce."
  }
}
```

Verify in CockroachDB SQL:

```bash
SELECT * FROM dapr_state;
```

**Expected**:

```
key            | value
---------------+--------------------------------
agent-memory-service||user:junaid | {"name":"Junaid","preferred_style":"informal","user_summary":"Junaid is building his Agents WorkForce."}
```

### Step 8.2: Send a Chat Message

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Schedule a brainstorming session.", "metadata": {"tags": ["coding"]}}'
```

**Expected Output**:

```json
{"user_id":"junaid","reply":"Hey Junaid,\n\nLet's schedule that brainstorming session!  To do so effectively, I need a little more info.  When are you free?  And how long should the session be?  Let me know and I'll find a time that works for everyone.\n","metadata":{"session_id":"c8b43b63-1442-44ab-b3b5-c7a4806a8b3a","timestamp":"2025-04-14T04:51:11.542149+00:00","tags":[]}}
```

### Step 8.3: Send Another Message (Same Session)

Use the `session_id` from the previous response:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "What was my last message?", "metadata": {"session_id": "c8b43b63-1442-44ab-b3b5-c7a4906a8b3a", "tags": ["query"]}}'
```

**Expected Output**:

```json
{"user_id":"junaid","reply":"Your last message was:  \"Schedule a brainstorming session.\"\n","metadata":{"session_id":"c8b43b63-1442-44ab-b3b5-c7a4906a8b3a","timestamp":"2025-04-14T04:59:59.768457+00:00","tags":[]}}
```

### Step 8.4: Verify Conversation History

```bash
SELECT * FROM conversation;
```

**Expected Output**:

```
id | user_id | session_id | message                    | reply                                              | timestamp
---+---------+------------+----------------------------+----------------------------------------------------+------------------------
1  | junaid  | <uuid>     | Schedule a coding session. | Hey Junaid! Sounds good. What time works...?       | 2025-04-12 10:00:00+00
2  | junaid  | <uuid>     | What was my last message?  | Your last message was: "Schedule a coding session." | 2025-04-12 10:01:00+00
```

### Step 8.5: Verify Memories Update

```bash
curl http://localhost:8001/memories/junaid
```

**Expected Output**:

```json
{"name":"Junaid","preferred_style":"informal","user_summary":"The user is scheduling a brainstorming session.\n"}%                                                                       
```


### Step 8.6: Check Logs

```bash
docker-compose logs chat-service-app
```

**Expected**:

```
chat-service-app-1  | INFO:main:Successfully fetched history for session c8b43b63-1442-44ab-b3b5-c7a4906a8b3a
chat-service-app-1  | INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
chat-service-app-1  | INFO:main:Publishing to Dapr URL: http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations
chat-service-app-1  | INFO:httpx:HTTP Request: POST http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations "HTTP/1.1 204 No Content"
chat-service-app-1  | INFO:main:Published ConversationUpdated event for junaid, session c8b43b63-1442-44ab-b3b5-c7a4906a8b3a
chat-service-app-1  | INFO:     192.168.65.1:45430 - "POST /chat/ HTTP/1.1" 200 OK
```

```bash
docker-compose logs agent-memory-service-app
```

**Expected**:

```
agent-memory-service-app-1  | INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
agent-memory-service-app-1  | INFO:httpx:HTTP Request: POST http://agent-memory-service-dapr:3501/v1.0/state/statestore "HTTP/1.1 204 No Content"
agent-memory-service-app-1  | INFO:AgentMemoryService:Stored metadata for junaid: {'name': 'Junaid', 'preferred_style': 'informal', 'user_summary': 'The user is scheduling a brainstorming session.\n'}
agent-memory-service-app-1  | INFO:     172.19.0.6:38644 - "POST /conversations HTTP/1.1" 200 OK
agent-memory-service-app-1  | INFO:httpx:HTTP Request: GET http://agent-memory-service-dapr:3501/v1.0/state/statestore/user:junaid "HTTP/1.1 200 OK"
agent-memory-service-app-1  | INFO:     192.168.65.1:41417 - "GET /memories/junaid HTTP/1.1" 200 OK
```

---

## Step 9: Why CockroachDB and SQLModel?

- **CockroachDB Serverless**:
  - **Dapr State Store**: Stores **memories** (e.g., `metadata-junaid`) in `dapr_state`, providing durable key-value storage, unlike Redis’ in-memory cache.
  - **SQLModel**: Stores **history** in `conversation`, enabling relational queries (e.g., `SELECT * FROM conversation WHERE session_id = '<uuid>'`).
  - Managed, auto-scaling, free tier makes it ideal for development and production.
- **Redis**: Fast pub/sub for `ConversationUpdated` events, preserving Tutorial 15’s event-driven architecture.
- **Gemini**: Delivers context-aware replies and user summaries, leveraging memories and history from CockroachDB.
- **Docker Networking**: Uses service names (`chat-service-dapr:3500`, `agent-memory-service-dapr:3501`) for reliable container communication, fixing previous `localhost` issues.

This setup makes **databases** the focus, delivering persistent, queryable storage with a simple, scalable architecture.

---

## Step 10: Exercises and Challenges

### Exercises

1. Add a `tags` field to the `Conversation` model (e.g., `tags: list[str]`) and query conversations by tags (e.g., `SELECT * FROM conversation WHERE 'coding' = ANY(tags)`).
2. Implement a `/conversations/{user_id}` endpoint in **Agent Memory Service** to fetch all conversations for a user.
3. Store additional metadata in Dapr’s state store (e.g., user preferences like favorite topics).
4. Optimize CockroachDB with indexes (e.g., `CREATE INDEX ON conversation (user_id, session_id)`).
5. Add SQLModel joins for conversation analytics (e.g., user activity reports).


### Challenges
Add the following features:
  - Dapr Workflows for Orchestration:
  - Human-in-the-Loop (HITL) Workflow:
  - Observability (Zipkin, Prometheus)
  - Chainlit UI
  - Use Secrets instead of having the CockroachDB URL in cockroachdb.yaml:
    Modify `cockroachdb.yaml` to use `secretKeyRef` with the `secretstore` component from Step 9, storing the connection string in `secrets.json` to keep credentials secure.

## Step 11: Next Steps

You’ve transformed DACA with **CockroachDB Serverless**, using **Dapr’s state store** for **LLM-generated memories** and **SQLModel** for **conversation history**, while keeping **Redis** for fast pub/sub. The **Chat Service** remains simple, just like Tutorial 15, fetching data from **CockroachDB** via **Agent Memory Service**, generating **Gemini** replies, and publishing events—all with proper Docker networking. Fantastic work mastering databases—you’re ready for cloud-native adventures! Keep rocking it! 🎉
