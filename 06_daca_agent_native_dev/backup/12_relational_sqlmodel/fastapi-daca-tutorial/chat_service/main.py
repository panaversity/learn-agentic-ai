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
    dapr_url = "http://chat-service-dapr:3500/v1.0/publish/pubsub/conversations"
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
            logger.info(f"Published ConversationUpdated event for {user_id}, session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())

    # Fetch metadata from Agent Memory Service (PostgreSQL Dapr state)
    metadata_url = "http://chat-service-dapr:3500/v1.0/invoke/agent-memory-service/method/memories/{user_id}".format(
        user_id=message.user_id
    )
    logger.info(f"Fetching metadata from {metadata_url}")

    memory_data = {"name": message.user_id, "preferred_style": "casual", "user_summary": f"{message.user_id} is new."}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(metadata_url)
            response.raise_for_status()
            memory_data = response.json()
            logger.info(f"Successfully fetched metadata for {message.user_id}")
    except httpx.HTTPStatusError as e:
        logger.warning(f"Failed to fetch metadata: {e}. Using default metadata.")

    # Fetch conversation history from Agent Memory Service (CockroachDB SQLModel)
    history_url = "http://chat-service-dapr:3500/v1.0/invoke/agent-memory-service/method/conversations/{session_id}".format(
        session_id=session_id
    )
    logger.info(f"Fetching history from {history_url}")

    history = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(history_url)
            response.raise_for_status()
            history = response.json()["history"]
            logger.info(f"Successfully fetched history for session {session_id}")
    except httpx.HTTPStatusError:
        logger.info(f"No prior history for session {session_id}")

    name = memory_data.get("name", message.user_id)
    style = memory_data.get("preferred_style", "casual")
    summary = memory_data.get("user_summary", f"{name} is new.")
    context = "No prior conversation." if not history else f"Recent chat: {history[-1]['content']}"
    personalized_instructions = (
        f"You are a helpful chatbot. Respond in a {style} way. "
        f"The user's name is {name}. User summary: {summary}. {context}\n"
        f"Message: {message.text}\nReply:"
    )

    current_user_message = ConversationEntry(role="user", content=message.text)
    history.append(current_user_message.model_dump())
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

    # Publish event to Redis pub/sub
    await publish_conversation_event(message.user_id, session_id, message.text, reply_text)

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata(session_id=session_id, timestamp=datetime.now(UTC).isoformat())
    )