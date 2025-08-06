import os
import httpx
import asyncio

import dapr.ext.workflow as wf  # type: ignore
from dapr.clients import DaprClient
from typing import Any, cast, ClassVar

from uuid import uuid4
from datetime import datetime, UTC
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata, ConversationEntry
from contextlib import asynccontextmanager


# Configuration
@dataclass
class Settings:
    """Application configuration settings loaded from environment variables."""
    DAPR_HTTP_PORT: ClassVar[str] = os.getenv("DAPR_HTTP_PORT", "3500")
    CORS_ORIGINS: ClassVar[list[str]] = ["http://localhost:3000"]
    MODEL_NAME: ClassVar[str] = "gemini-1.5-flash"
    MODEL_BASE_URL: ClassVar[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()

# Fetch Gemini API key from Dapr secrets store
def get_gemini_api_key() -> str:
    dapr_client = DaprClient()
    try:
        secret = dapr_client.get_secret(
            store_name="secretstore",
            key="gemini-api-key"
        )
        return secret.secret["gemini-api-key"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Gemini API key: {e}")
    finally:
        dapr_client.close()

# Initialize AI client at startup
external_client = None
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global external_client, model
    api_key = get_gemini_api_key()
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url=settings.MODEL_BASE_URL,
    )
    model = OpenAIChatCompletionsModel(model=settings.MODEL_NAME, openai_client=external_client)
    
    # Start workflow runtime once at app startup
    wfr.start()
    print("Workflow runtime started")
    
    yield
    
    # Cleanup at shutdown
    wfr.shutdown()
    print("Workflow runtime shut down")

# Workflow Activities
wfr = wf.WorkflowRuntime()
# FastAPI App
app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    api_key = get_gemini_api_key()
    return {"status": "ok", "api_key": api_key}

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

    return {
        "user_id": message.user_id,
        "status": state.runtime_status,
        "state": state,
        "metadata": Metadata(session_id=session_id)
    }