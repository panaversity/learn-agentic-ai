import logging
import httpx
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprActor
from dapr.actor.runtime.runtime import ActorRuntime
from dapr.actor.runtime.config import ActorRuntimeConfig, ActorTypeConfig, ActorReentrancyConfig
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata
from user_session_actor import UserSessionActor, UserSessionActorInterface
from utils import get_gemini_api_key, settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ChatService")

external_client = None
model = None

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0"
)

config = ActorRuntimeConfig()
config.update_actor_type_configs([ActorTypeConfig(actor_type=UserSessionActor.__name__, reentrancy=ActorReentrancyConfig(enabled=True))])
ActorRuntime.set_actor_config(config)

actor = DaprActor(app)

@app.on_event("startup")
async def startup():
    global external_client, model
    logger.info("Starting up Chat Service")
    await actor.register_actor(UserSessionActor)
    logger.info(f"Registered actor: {UserSessionActor.__name__}")
    try:
        api_key = await get_gemini_api_key()
        external_client = AsyncOpenAI(api_key=api_key, base_url=settings.MODEL_BASE_URL)
        model = OpenAIChatCompletionsModel(model=settings.MODEL_NAME, openai_client=external_client)
        logger.info("Initialized AI client")
    except Exception as e:
        logger.error(f"Error initializing AI client: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_run_config():
    if model and external_client:
        return RunConfig(model=model, model_provider=external_client, tracing_disabled=True)
    return None

@function_tool
def get_current_time() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

async def publish_conversation_event(user_id: str, session_id: str, user_text: str, reply_text: str, dapr_port: int = 3500) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/conversations"
    event_data = {"user_id": user_id, "session_id": session_id, "event_type": "ConversationUpdated", "user_message": user_text, "assistant_reply": reply_text}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Publishing event for user {user_id}, session {session_id}")
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            logger.info(f"Published ConversationUpdated event for user {user_id}, session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event: {e}")

async def get_memory_data(user_id: str, dapr_port: int = 3500) -> Dict[str, str]:
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Fetching metadata for user {user_id}")
            response = await client.get(metadata_url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched metadata for user {user_id}: {data}")
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for user {user_id}: {e}")
            return {"name": user_id, "preferred_style": "casual", "user_summary": f"{user_id} is a new user."}

async def generate_reply(user_id: str, message_text: str, history: List[Dict[str, str]]) -> str:
    try:
        logger.info(f"Generating reply for user {user_id}: {message_text}")
        memory_data = await get_memory_data(user_id)
        name = memory_data.get("name", user_id)
        style = memory_data.get("preferred_style", "casual")
        summary = memory_data.get("user_summary", f"{name} is a new user.")
        history_summary = "No prior conversation." if not history else "\n".join(
            f"User: {entry.get('user_text', '')}\nAssistant: {entry.get('reply_text', '')}" for entry in history[-3:]
        )
        instructions = f"You are a helpful chatbot. Respond in a {style} way. If the user asks for the time, use the get_current_time tool. The user's name is {name}. User summary: {summary}. Conversation history:\n{history_summary}"
        config = get_run_config()
        if not config:
            logger.warning("AI not initialized")
            return "I'm sorry, but I'm not fully initialized yet. Please try again in a moment."
        chat_agent = Agent(name="ChatAgent", instructions=instructions, tools=[get_current_time], model=model)
        result = await Runner.run(chat_agent, input=message_text, run_config=config)
        reply = result.final_output
        logger.info(f"Generated reply: {reply}")
        return reply
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return "I'm sorry, I encountered an error while processing your message."

async def get_conversation_history(user_id: str, dapr_port: int = 3500) -> List[Dict[str, Any]]:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/GetConversationHistory"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Fetching history for user {user_id}")
            response = await client.post(url, json={})
            response.raise_for_status()
            history = response.json()
            logger.info(f"Received history for user {user_id}: {history}")
            return history if history is not None else []
        except httpx.HTTPStatusError as e:
            logger.warning(f"Error getting history: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404 or "ERR_ACTOR_INSTANCE_MISSING" in e.response.text:
                return []
            raise
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            raise

async def add_message(user_id: str, message_data: Dict[str, Any], dapr_port: int = 3500) -> None:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/AddMessage"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Adding message for user {user_id}: {message_data}")
            headers = {"Content-Type": "application/json"}
            response = await client.post(url, json=message_data, headers=headers)
            response.raise_for_status()
            logger.info(f"Message added for user {user_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error adding message: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")

@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Received request to root endpoint")
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Dict[str, Any])
async def chat(message: Message) -> Dict[str, Any]:
    if not message.text.strip():
        logger.warning("Empty message text received")
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    logger.info(f"Processing chat request for user {message.user_id}: {message.text}")
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    try:
        history = await get_conversation_history(message.user_id)
        reply_text = await generate_reply(message.user_id, message.text, history)
        await add_message(message.user_id, {"user_text": message.text, "reply_text": reply_text})
        await publish_conversation_event(message.user_id, session_id, message.text, reply_text, int(settings.DAPR_HTTP_PORT))
        logger.info(f"Chat request completed for user {message.user_id}")
        return {"user_id": message.user_id, "reply": reply_text, "metadata": Metadata(session_id=session_id)}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")