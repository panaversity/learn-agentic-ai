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
