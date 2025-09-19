# Orchestrating Microservices with [Dapr Workflows](https://docs.dapr.io/getting-started/quickstarts/workflow-quickstart/)

**Workflows aren’t just fancy—they **save you from losing users** when things go wrong (e.g., network drops) and **cut dev time** when you scale up.**

> [!IMPORTANT] 
> This Step is a Work In Progress - Dapr Workflows, Architecture, Patterns!

Welcome to the eighth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll enhance the microservices from **07_dapr_pubsub_messaging** by integrating Dapr’s **Workflows** building block. In Tutorial 07, the Chat Service fetched user metadata synchronously, generated a reply with an LLM, and published a “ConversationUpdated” event for the Agent Memory Service to update history and metadata asynchronously. We’ll replace this loose sequence with a Dapr Workflow, orchestrating these steps into a reliable, multi-step process with retries and timeouts. This makes your chatbot tougher—handling flaky connections or service hiccups without dropping the ball—and easier to grow as you add features. Let’s dive in!

---

## What You’ll Learn
- How to use Dapr Workflows to turn a series of microservice actions into a dependable, orchestrated process.
- Defining a workflow in the Chat Service to fetch user metadata, generate an LLM reply, and publish a “ConversationUpdated” event, with retries for each step.
- Configuring timeouts and retries to keep things running smoothly even when networks or services falter.
- Running microservices with Dapr Workflows enabled and seeing the difference in action.
- Updating unit tests to verify the workflow-driven Chat Service.

### Why This Matters
- **Reliability**: If the Agent Memory Service is down for a sec or the LLM call times out, workflows retry automatically—no more lost chats or manual fixes.
- **Future-Proofing**: Adding a new step (like logging chats) is a breeze with workflows, not a code tangle like before.
- **Real-World Value**: Your chatbot stays online and consistent, even in messy, distributed systems—crucial for a scalable AI assistant.

## Extra Reading
- [Workflow Overview](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
- [Workflow Patterns](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/)
- [Workflow Architecture](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/)
- [Agentic Patterns Implementations Code Inspiration](https://github.com/dapr/python-sdk/tree/main/examples/workflow)

## Prerequisites
- Completion of **07_dapr_pubsub_messaging** (Chat Service and Agent Memory Service with Dapr Service Invocation, State Management, and Pub/Sub).
- Dapr CLI and runtime installed (v1.15+, per Tutorial 07 logs).
- Docker installed (for Dapr sidecars and Redis).
- Python 3.12+ installed (consistent with Tutorial 07).
- A Gemini API key (set as `GEMINI_API_KEY`).

---

## Step 1: Recap of Tutorial 07
In **07_dapr_pubsub_messaging**, we built:
- **Chat Service**:
  - Fetches user metadata (e.g., `user_summary`) from Agent Memory Service via Dapr Service Invocation.
  - Generates a reply using the Gemini LLM (via OpenAI Agents SDK).
  - Publishes a “ConversationUpdated” event to the `conversations` topic.
- **Agent Memory Service**:
  - Subscribes to `conversations`, updates conversation history, and refreshes `user_summary` with the LLM.

### Current Limitations
- **Fragile Flow**: If fetching metadata fails (e.g., network blip), you fallback to defaults, but there’s no retry—users might get a generic reply.
- **No Safety Net**: If publishing the event fails, history doesn’t update, and you’re stuck debugging manually.
- **Hard to Expand**: Adding a step (e.g., saving chats to a log) means rewriting the endpoint, risking errors.

### Goal for This Tutorial
We’ll use Dapr Workflows to:
- Orchestrate fetching metadata, generating a reply, and publishing the event as a single, reliable process.
- Add retries and timeouts so transient failures (e.g., Agent Memory Service lag) don’t break the chat.
- Show how workflows make your system tougher and simpler to extend—real value for a growing AI assistant.

### Current Project Structure (From Tutorial 7)
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

## Step 2: Why Use Dapr Workflows?
Think of workflows as a recipe for your chatbot’s tasks. In Tutorial 07, you were cooking freestyle—grabbing ingredients (metadata), mixing a dish (reply), and shouting “done” (event). If the stove died mid-cook, you’d start over. Workflows give you:
- **Retries**: Oven’s slow? Try again automatically.
- **Order**: Steps happen in sequence, no skipping.
- **Recovery**: Power cuts out? Pick up where you left off.
- **Growth**: Add a “serve dessert” step without burning the kitchen down.

For DACA, this means:
- **Chat Stays Alive**: No dropped messages when services hiccup.
- **Easier Upgrades**: Bolt on features (e.g., analytics) without chaos.
- **Agentic Edge**: Reliable workflows support smarter, multi-step AI interactions.

---

## Step 3: Configure Dapr Workflow Component
Workflows need a state store to track progress. Tutorial 07’s `components/statestore.yaml` (Redis) works fine:
```bash
cat components/statestore.yaml
```
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
- Dapr Workflows use this to save workflow state.
- No extra setup needed—`dapr init` from Tutorial 07 has Redis running.

Check the logs when starting services to confirm the workflow engine starts (e.g., “Workflow engine started”).

---

## Step 4: Update the Chat Service
We’ll rework `chat_service/main.py` to use a Dapr Workflow for:
1. Fetching metadata from Agent Memory Service.
2. Generating a reply with Gemini.
3. Publishing “ConversationUpdated.”

### Step 4.1: Install Dapr Python SDK
```bash
cd chat_service
uv add dapr dapr-ext-workflow
```
- Adds `dapr` to `pyproject.toml` and `uv.lock`.

## Step 4.1.1 Update statestore.yml

Add the following lines at end of current statestore.yml
```yaml
  - name: actorStateStore
    value: "true"  # Enables Redis as an actor state store for workflows
```

### Step 4.2: Update `chat_service/main.py`
Here’s the workflow version, building on Tutorial 07:
```python
import os
import httpx
import asyncio
import dapr.ext.workflow as wf  # type: ignore

from typing import Any, cast, ClassVar
from dotenv import load_dotenv

from uuid import uuid4
from datetime import datetime, UTC
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata, ConversationEntry


load_dotenv()


# Configuration
@dataclass
class Settings:
    """Application configuration settings loaded from environment variables."""
    GEMINI_API_KEY: ClassVar[str | None] = os.getenv("GEMINI_API_KEY")
    DAPR_HTTP_PORT: ClassVar[str] = os.getenv("DAPR_HTTP_PORT", "3500")
    CORS_ORIGINS: ClassVar[list[str]] = ["http://localhost:3000"]
    MODEL_NAME: ClassVar[str] = "gemini-1.5-flash"
    MODEL_BASE_URL: ClassVar[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()

if not settings.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Workflow Activities
wfr = wf.WorkflowRuntime()
# FastAPI App
app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI model
external_client = AsyncOpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url=settings.MODEL_BASE_URL,
)
model = OpenAIChatCompletionsModel(
    model=settings.MODEL_NAME, openai_client=external_client)

config = RunConfig(
    model=model, 
    model_provider=cast(ModelProvider, external_client), 
    tracing_disabled=True
)

# Utility Functions
@function_tool
def get_current_time() -> str:
    """Return the current UTC time formatted as a string."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

async def publish_conversation_event(
    user_id: str, 
    session_id: str, 
    user_text: str, 
    reply_text: str, 
    dapr_port: int = 3500
) -> None:
    """Publish a conversation update event to the Dapr pubsub component."""
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
    """Fetch user metadata from the memory service."""
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(metadata_url)
            memory_response.raise_for_status()
            return memory_response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch metadata: {e}")
            return {
                "name": user_id,
                "preferred_style": "casual",
                "user_summary": f"{user_id} is a new user."
            }

async def get_conversation_history(session_id: str, dapr_port: int = 3500) -> list[dict[str, Any]]:
    """Fetch conversation history from the memory service."""
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
    """Generate instructions for the chat agent based on user memory and conversation history."""
    name = memory_data.get("name", user_id)
    style = memory_data.get("preferred_style", "casual")
    summary = memory_data.get("user_summary", f"{name} is a new user.")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    
    return (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user's name is {name}. User summary: {summary}. {context}"
    )


@wfr.activity(name='fetch_context')
def fetch_context(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> dict[str, Any]:
    """Fetch both conversation history and user memory data in a single activity."""
    print(f"Fetching context for user {activity_input['user_id']}, session {activity_input['session_id']}")
    
    history = asyncio.run(get_conversation_history(
        activity_input["session_id"],
        int(activity_input["dapr_port"])
    ))
    
    memory = asyncio.run(get_memory_data(
        activity_input["user_id"],
        int(activity_input["dapr_port"])
    ))
    
    print(f"Fetched {len(history)} history entries and user memory data")
    return {"history": history, "memory": memory}

@wfr.activity(name='generate_response')
def generate_response(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> str:
    """Generate a response to the user's message using the chat agent."""
    print(f"Generating response for user {activity_input['user_id']}")
    
    context = activity_input["context"]
    instructions = generate_chat_instructions(
        context["memory"],
        context["history"],
        activity_input["user_id"]
    )

    # Add current user message to history
    current_message = ConversationEntry(role="user", content=activity_input["user_text"])
    history = context["history"]
    history.append(current_message.model_dump())

    # Create and run chat agent
    chat_agent = Agent(
        name="ChatAgent",
        instructions=instructions,
        tools=[get_current_time],
        model=model
    )

    # Remove timestamps for model input
    history_without_timestamps = [
        {k: v for k, v in msg.items() if k != "timestamp"}
        for msg in history
    ]

    result = asyncio.run(Runner.run(
        chat_agent,
        input=history_without_timestamps, # type: ignore
        run_config=config
    ))
    
    print(f"Response generated successfully")
    return result.final_output

@wfr.activity(name='save_conversation')
def save_conversation(ctx: wf.WorkflowActivityContext, activity_input: dict[str, Any]) -> None:
    """Save the conversation by publishing an update event."""
    print(f"Saving conversation for user {activity_input['user_id']}, session {activity_input['session_id']}")
    
    asyncio.run(publish_conversation_event(
        activity_input["user_id"],
        activity_input["session_id"],
        activity_input["user_text"],
        activity_input["response"],
        int(activity_input["dapr_port"])
    ))
    
    print(f"Conversation saved successfully")

@wfr.activity(name='handle_error')
def handle_error(ctx: wf.WorkflowActivityContext, error: str) -> None:
    """Handle workflow errors with logging and potential recovery actions."""
    print(f'Error in workflow: {error}')
    # TODO: Add proper error handling (logging, monitoring, etc.)

# Main Workflow
@wfr.workflow(name='chat_workflow')
def chat_workflow(ctx: wf.DaprWorkflowContext, wf_input: dict[str, Any]) -> Any:
    """
    Main workflow that orchestrates the chat processing steps:
    1. Fetch context (conversation history and user memory)
    2. Generate response to user message
    3. Save the conversation
    """
    try:
        # Fetch context (conversation history and user memory)
        context = yield ctx.call_activity(fetch_context, input=wf_input)

        # Generate response
        response = yield ctx.call_activity(
            generate_response,
            input={**wf_input, "context": context}
        )

        # Save conversation
        yield ctx.call_activity(
            save_conversation,
            input={**wf_input, "response": response}
        )

    except Exception as e:
        yield ctx.call_activity(handle_error, input=str(e))
        raise

    return [response]


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/")
async def chat(message: Message) -> dict[str, Any]:
    """
    Process a chat message and return the response.
    
    Args:
        message: The user's message including text and metadata
        
    Returns:
        A dictionary containing the response status and metadata
    """
    # Validate input
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    # Start workflow runtime
    wfr.start()

    # Use existing session_id from metadata if provided, otherwise generate a new one
    session_id = (
        message.metadata.session_id 
        if message.metadata and message.metadata.session_id 
        else str(uuid4())
    )

    # Prepare workflow input
    workflow_input = {
        "user_id": message.user_id,
        "session_id": session_id,
        "user_text": message.text,
        "dapr_port": settings.DAPR_HTTP_PORT,
    }

    # Start and wait for workflow
    wf_client = wf.DaprWorkflowClient()
    instance_id = wf_client.schedule_new_workflow(
        workflow=chat_workflow, 
        input=workflow_input
    )
    print(f'Workflow started. Instance ID: {instance_id}')
    
    state = wf_client.wait_for_workflow_completion(instance_id)
    print(f'Workflow completed! Status: {state.runtime_status}')
    
    # Shutdown workflow runtime
    wfr.shutdown()

    return {
        "user_id": message.user_id,
        "status": state.runtime_status,
        "state": state,
        "metadata": Metadata(session_id=session_id)
    }
```

#### Changes
1. **Workflow Setup**: Added Dapr Workflow imports and runtime.
2. **Activities**: The Steps in WorkFlow
3. **Workflow**: Ties steps together with retries.
4. **Endpoint**: Triggers the workflow and returns the reply.

---

## Step 5: Verify Agent Memory Service
No changes needed—it still handles “ConversationUpdated” events as in Tutorial 07.

---

## Step 6: Run the Microservices
### Start Agent Memory Service
```bash
cd agent_memory_service
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start Chat Service
```bash
cd chat_service
dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Check Logs
Look for “Workflow engine started” in Chat Service logs.

---

## Step 7: Test It
### Initialize Metadata
```bash
curl -X POST http://localhost:8001/memories/junaid/initialize -H "Content-Type: application/json" -d '{"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is new."}'
```

### Chat Request
```bash
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "Hi there"}'
```
- **Expected**: Reply like “Greetings, Junaid! How may I assist you?”
- **Logs**: See retries if you stop Agent Memory Service briefly.

### Verify History
```bash
curl http://localhost:8001/conversations/<session_id_from_response>
i.e: curl http://localhost:8001/conversations/f160203e-ff72-442b-8bca-4fddba98964b
```

---

## Step 8: Value Created
- **No More Dropped Chats**: Workflows retry flaky steps—your chatbot keeps talking even if services lag.
- **Simpler Growth**: Add a logging step? Just plug in an activity, not rewrite everything.
- **Scalable AI**: Reliable workflows mean your assistant can handle more users without breaking.

---

## Step 9: Next Steps
Next up: **09_dapr_secrets_management** for securing that Gemini key.

### Exercises
1. Add a logging activity to save chats.
2. Test retries by stopping Agent Memory Service mid-workflow.
3. Study Workflow Patterns
---

## Conclusion
Workflows make your Chat Service a rock-solid conversationalist, ready for real-world hiccups and future features. Onward to secrets!