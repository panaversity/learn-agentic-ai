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
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=cast(
    ModelProvider, external_client), tracing_disabled=True)

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
            raise HTTPException(
                status_code=500, detail="Failed to store metadata")


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
    state_data = [{"key": f"session:{session_id}",
                   "value": {"history": history}}]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=state_data)
            response.raise_for_status()
            logger.info(
                f"Stored conversation history for session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to store conversation history: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to store conversation")


async def generate_user_summary(user_id: str, history: list[dict]) -> str:
    summary_agent = Agent(
        name="SummaryAgent",
        instructions="Generate a concise summary of the user based on their conversation history (e.g., 'Junaid enjoys coding and scheduling tasks'). Use only the provided history.",
        model=model
    )
    history_text = "\n".join(
        # Last 5 entries
        [f"{entry['role']}: {entry['content']}" for entry in history[-5:]])
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

    logger.info(
        f"Event validation: type={event_type}, user_id={user_id}, session_id={session_id}, user_message={user_message}, assistant_reply={assistant_reply}")

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
        metadata = {"name": user_id, "preferred_style": "casual",
                    "user_summary": f"{user_id} is a new user."}
    metadata["user_summary"] = await generate_user_summary(user_id, history)
    await set_user_metadata(user_id, metadata)

    return {"status": "SUCCESS"}  # Uppercase to match Dapr’s expectation
