import logging
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserMetadata, ConversationHistory, ConversationEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DACA Agent Memory Service",
    description="A FastAPI-based service for user metadata and conversation history",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8010"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_user_metadata(user_id: str, dapr_port: int = 3501) -> dict:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/user:{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return {}

async def set_user_metadata(user_id: str, metadata: dict, dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
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
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore/session:{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            state_data = response.json()
            return state_data.get("history", [])
        except httpx.HTTPStatusError:
            return []

async def set_conversation_history(session_id: str, history: list[dict], dapr_port: int = 3501) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/statestore"
    state_data = [{"key": f"session:{session_id}", "value": {"history": history}}]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(dapr_url, json=state_data)
            response.raise_for_status()
            logger.info(f"Stored conversation history for session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to store conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to store conversation")

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Agent Memory Service! Access /docs for the API documentation."}

@app.get("/memories/{user_id}", response_model=UserMetadata)
async def get_memories(user_id: str):
    metadata = await get_user_metadata(user_id)
    if not metadata:
        return UserMetadata(name=user_id, preferred_style="casual", goal="chat")
    return UserMetadata(**metadata)

@app.post("/memories/{user_id}/initialize", response_model=dict)
async def initialize_memories(user_id: str, metadata: UserMetadata):
    await set_user_metadata(user_id, metadata.dict())
    return {"status": "success", "user_id": user_id, "metadata": metadata.dict()}

@app.get("/conversations/{session_id}", response_model=ConversationHistory)
async def get_conversation(session_id: str):
    history = await get_conversation_history(session_id)
    return ConversationHistory(history=[ConversationEntry(**entry) for entry in history])

@app.post("/conversations/{session_id}", response_model=dict)
async def update_conversation(session_id: str, history: ConversationHistory):
    await set_conversation_history(session_id, [entry.dict() for entry in history.history])
    return {"status": "success", "session_id": session_id}