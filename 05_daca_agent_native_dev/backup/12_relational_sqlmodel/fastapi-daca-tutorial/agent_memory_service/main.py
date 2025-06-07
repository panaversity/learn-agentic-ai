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
