# [Securely Managing Secrets with Dapr](https://docs.dapr.io/developing-applications/building-blocks/secrets/secrets-overview/)

Welcome to the ninth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we enhance the microservices from **08_dapr_workflows** by integrating Dapr’s **Secrets Management** building block. In Tutorial 08, the Chat Service used a Gemini API key (via an environment variable `GEMINI_API_KEY`) within a Dapr Workflow to orchestrate chat processing. This approach, while functional, is insecure for production due to the risk of exposing the key. Here, we’ll configure Dapr to manage the Gemini API key in a secrets store and update the Chat Service to retrieve it securely using the Dapr Python SDK. This bolsters our system’s security, aligning with best practices for production-ready distributed systems. Let’s get started!

---

## What You’ll Learn
- How to use Dapr’s Secrets Management to securely manage sensitive data like API keys.
- Configuring a local file-based Dapr secrets store for the Gemini API key.
- Updating the Chat Service to fetch the API key from the Dapr secrets store.
- Running microservices with Secrets Management alongside existing Dapr features (Workflows, Pub/Sub, etc.).
- Updating unit tests to verify secrets integration.

---

## Prerequisites
- Completion of **08_dapr_workflows** (Chat Service with Dapr Workflows, Agent Memory Service with Pub/Sub).
- Dapr CLI and runtime installed (v1.15+, per **04_dapr_theory_and_cli**).
- Docker installed (for Dapr sidecars and Redis).
- Python 3.12+ installed.
- A Gemini API key (previously set as `GEMINI_API_KEY`).

---

## Step 1: Recap of Tutorial 08
In **08_dapr_workflows**, we built:
- **Chat Service**:
  - Uses a Dapr Workflow to fetch user metadata and history (via Service Invocation), generate a reply with Gemini (via `AsyncOpenAI`), and publish a “ConversationUpdated” event (via Pub/Sub).
  - Relies on `GEMINI_API_KEY` from an environment variable.
- **Agent Memory Service**:
  - Subscribes to the `conversations` topic, updates history, and regenerates `user_summary` with the LLM.

### Current Limitations
- **Insecure API Key Storage**: The Gemini API key in `GEMINI_API_KEY` risks exposure (e.g., logs, version control).
- **No Centralized Secret Management**: Lacks a secure, scalable way to manage secrets.
- **Security Risks**: Environment variables don’t meet production security standards.

### Goal for This Tutorial
We’ll:
- Configure a Dapr secrets store to hold the Gemini API key.
- Update the Chat Service to retrieve it securely, removing the environment variable dependency.
- Maintain the workflow-driven architecture from Tutorial 08.

### Project Structure (from Tutorial 08)
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
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
│   └── subscriptions.yaml
└── README.md
```

---

## Step 2: Why Use Dapr Secrets Management?
Dapr’s **Secrets Management** building block provides a secure way to manage and access sensitive data (e.g., API keys, database credentials) in a distributed system. It offers several advantages over environment variables or hardcoded secrets:
- **Security**: Secrets are stored in a dedicated secrets store (e.g., local file, HashiCorp Vault, AWS Secrets Manager), reducing the risk of accidental exposure.
- **Centralized Management**: Secrets can be managed centrally, making it easier to rotate, update, or revoke them without changing application code.
- **Access Control**: Dapr supports fine-grained access control for secrets (depending on the secrets store), ensuring only authorized services can access them.
- **Abstraction**: Dapr provides a consistent API for accessing secrets, regardless of the underlying secrets store, making it easy to switch stores (e.g., from local to cloud-based).
- **Production-Readiness**: Aligns with best practices for handling sensitive data in production environments.

In DACA, Secrets Management is crucial for:
- Securely managing the OpenAI API key used by the Chat Service.
- Preparing the system for production deployment, where secrets must be handled securely.
- Supporting a scalable architecture where multiple services might need access to shared secrets.

---

Take Last Step Code as your starter code.

## Step 3: Configure Dapr Secrets Store
Dapr uses a secrets store component to manage secrets. For this tutorial, we’ll use a **local file-based secrets store** for simplicity, as it doesn’t require external infrastructure. In a production environment, you’d use a secure secrets store like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault.

### Step 3.1: Create a Secrets File
In the project root:
```bash
cd fastapi-daca-tutorial
touch secrets.json
```
Edit `secrets.json`:
```json
{
  "gemini-api-key": "your-actual-gemini-api-key"
}
```
Replace `"your-actual-gemini-api-key"` with your Gemini API key.

### Step 3.2: Define the Secrets Store Component
Add to `components/`:
```bash
touch components/secretstore.yaml
```
Edit `components/secretstore.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: ../secrets.json
  - name: nestedSeparator
    value: "."
```
- `secretsFile: ../secrets.json`: Relative path works when running Dapr from service directories with `--components-path ../components`.

### Step 3.3: Production Considerations
For production, use:
- **HashiCorp Vault**:
  ```yaml
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: secretstore
  spec:
    type: secretstores.hashicorp.vault
    version: v1
    metadata:
    - name: vaultAddr
      value: "https://your-vault-server:8200"
    - name: vaultToken
      value: "your-vault-token"
  ```
- **AWS Secrets Manager**:
  ```yaml
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: secretstore
  spec:
    type: secretstores.aws.secretmanager
    version: v1
    metadata:
    - name: region
      value: "us-east-1"
    - name: accessKey
      value: "your-access-key"
    - name: secretKey
      value: "your-secret-key"
  ```
For this tutorial, we’ll stick with the local file-based store for simplicity.

---

## Step 4: Update the Chat Service
We’ll modify `chat_service/main.py` to fetch the Gemini API key from Dapr Secrets Management, integrating with the existing workflow.

### Step 4.1: Install Dapr SDK (if not already present)
```bash
cd chat-service
uv add dapr dapr-ext-workflow
```

### Step 4.2: Modify `chat_service/main.py`
```python
import os
import httpx
import asyncio
from typing import Any, cast
from uuid import uuid4
from datetime import datetime, UTC
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata, ConversationEntry
from dapr.clients import DaprClient
import dapr.ext.workflow as wf

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

# Configuration
@dataclass
class Settings:
    DAPR_HTTP_PORT: str = os.getenv("DAPR_HTTP_PORT", "3500")
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    MODEL_NAME: str = "gemini-1.5-flash"
    MODEL_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()

# Fetch Gemini API key from Dapr secrets store
async def get_gemini_api_key() -> str:
    with DaprClient() as dapr_client:
        try:
            secret = await dapr_client.get_secret(
                store_name="secretstore",
                key="gemini-api-key"
            )
            return secret.secret["gemini-api-key"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve Gemini API key: {e}")

# Initialize AI client at startup
external_client = None
model = None

@app.on_event("startup")
async def startup():
    global external_client, model
    api_key = await get_gemini_api_key()
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url=settings.MODEL_BASE_URL,
    )
    model = OpenAIChatCompletionsModel(model=settings.MODEL_NAME, openai_client=external_client)

config = RunConfig(model=model, model_provider=cast(ModelProvider, external_client), tracing_disabled=True)

# Workflow Setup
wfr = wf.WorkflowRuntime()

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

async def get_memory_data(user_id: str, dapr_port: int = 3500) -> dict[str, str]:
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(metadata_url)
            memory_response.raise_for_status()
            return memory_response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch metadata: {e}")
            return {"name": user_id, "preferred_style": "casual", "user_summary": f"{user_id} is a new user."}

async def get_conversation_history(session_id: str, dapr_port: int = 3500) -> list[dict[str, Any]]:
    history_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/conversations/{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            history_response = await client.get(history_url)
            history_response.raise_for_status()
            return history_response.json()["history"]
        except httpx.HTTPStatusError:
            print(f"No prior history for session {session_id}")
            return []

def generate_chat_instructions(memory_data: dict[str, str], history: list[dict[str, Any]], user_id: str) -> str:
    name = memory_data.get("name", user_id)
    style = memory_data.get("preferred_style", "casual")
    summary = memory_data.get("user_summary", f"{name} is a new user.")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    return (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user’s name is {name}. User summary: {summary}. {context}"
    )

@wfr.activity(name='fetch_context')
def fetch_context(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> dict[str, Any]:
    print(f"Fetching context for user {activity_input['user_id']}, session {activity_input['session_id']}")
    history = asyncio.run(get_conversation_history(activity_input["session_id"], int(activity_input["dapr_port"])))
    memory = asyncio.run(get_memory_data(activity_input["user_id"], int(activity_input["dapr_port"])))
    print(f"Fetched {len(history)} history entries and user memory data")
    return {"history": history, "memory": memory}

@wfr.activity(name='generate_response')
def generate_response(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> str:
    print(f"Generating response for user {activity_input['user_id']}")
    context = activity_input["context"]
    instructions = generate_chat_instructions(context["memory"], context["history"], activity_input["user_id"])
    current_message = ConversationEntry(role="user", content=activity_input["user_text"])
    history = context["history"]
    history.append(current_message.dict())
    chat_agent = Agent(name="ChatAgent", instructions=instructions, tools=[get_current_time], model=model)
    result = asyncio.run(Runner.run(chat_agent, input=activity_input["user_text"], run_config=config))
    print(f"Response generated successfully")
    return result.final_output

@wfr.activity(name='save_conversation')
def save_conversation(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> None:
    print(f"Saving conversation for user {activity_input['user_id']}, session {activity_input['session_id']}")
    asyncio.run(publish_conversation_event(
        activity_input["user_id"], activity_input["session_id"], activity_input["user_text"],
        activity_input["response"], int(activity_input["dapr_port"])
    ))
    print(f"Conversation saved successfully")

@wfr.activity(name='handle_error')
def handle_error(ctx: wf.WorkflowActivityContext, error: str) -> None:
    print(f'Error in workflow: {error}')

@wfr.workflow(name='chat_workflow')
def chat_workflow(ctx: wf.DaprWorkflowContext, wf_input: dict[str, Any]) -> Any:
    try:
        context = yield ctx.call_activity(fetch_context, input=wf_input)
        response = yield ctx.call_activity(generate_response, input={**wf_input, "context": context})
        yield ctx.call_activity(save_conversation, input={**wf_input, "response": response})
    except Exception as e:
        yield ctx.call_activity(handle_error, input=str(e))
        raise
    return [response]

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/")
async def chat(message: Message) -> dict[str, Any]:
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    wfr.start()
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    workflow_input = {
        "user_id": message.user_id,
        "session_id": session_id,
        "user_text": message.text,
        "dapr_port": settings.DAPR_HTTP_PORT,
    }
    wf_client = wf.DaprWorkflowClient()
    instance_id = wf_client.schedule_new_workflow(workflow=chat_workflow, input=workflow_input)
    print(f'Workflow started. Instance ID: {instance_id}')
    state = wf_client.wait_for_workflow_completion(instance_id)
    print(f'Workflow completed! Status: {state.runtime_status}')
    wfr.shutdown()
    return {
        "user_id": message.user_id,
        "status": state.runtime_status,
        "state": state,
        "metadata": Metadata(session_id=session_id)
    }
```

#### Changes
1. **Secrets Retrieval**: Added `get_gemini_api_key` to fetch the API key from `secretstore`.
2. **Startup Initialization**: Initialized `external_client` and `model` with the fetched key at startup.
3. **Removed Env Vars**: Eliminated `load_dotenv` and `os.getenv("GEMINI_API_KEY")`.
4. **Workflow Intact**: Kept the workflow structure from Tutorial 08.



---

## Step 5: Verify Agent Memory Service
No changes needed—it uses Pub/Sub as in Tutorial 08. Optionally, update it to use Secrets Management for its LLM calls (exercise).

---

## Step 6: Run the Microservices
### Start Agent Memory Service
```bash
cd agent_memory_service
uv venv
source .venv/bin/activate
uv sync
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 --components-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start Chat Service
```bash
cd chat_service
uv venv
source .venv/bin/activate
uv sync
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 --components-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Verify
```bash
dapr list
```

---

## Step 7: Test the Microservices
### Initialize Metadata
```bash
curl -X POST http://localhost:8001/memories/junaid/initialize -H "Content-Type: application/json" -d '{"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}'
```

### Test Chat
```bash
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "What time is it?"}'
```
Expected:
```json
{
  "user_id": "junaid",
  "status": "COMPLETED",
  "state": {...},
  "metadata": {"timestamp": "...", "session_id": "..."}
}
```

### Verify Metadata
```bash
curl http://localhost:8001/memories/junaid
```
Expected: Updated `user_summary`.

### Run Tests
```bash
cd chat_service
uv run pytest test_main.py -v
```

---

## Step 8: Why Secrets Management for DACA?
- **Security**: Protects the Gemini API key from exposure.
- **Centralization**: Simplifies secret management.
- **Production-Ready**: Enhances distributed system security.
- **Scalability**: Supports secure growth.

---

## Step 9: Next Steps
Next: **10_dapr_actors** for stateful user sessions.

### Exercises
1. Update Agent Memory Service for Secrets Management.
2. Use a production secrets store (e.g., Vault).
3. Inspect secrets via `dapr dashboard`.

---

## Conclusion
We’ve integrated Dapr Secrets Management, securing the Gemini API key within our workflow-driven Chat Service. This strengthens DACA’s foundation for production. Onward to Actors!
