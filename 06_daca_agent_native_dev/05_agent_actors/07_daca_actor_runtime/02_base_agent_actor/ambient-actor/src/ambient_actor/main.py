import logging
import os

from fastapi import FastAPI, HTTPException
from dapr.ext.fastapi import DaprActor # type: ignore
from dapr.actor import ActorProxy, ActorId

from pydantic import BaseModel

from ambient_actor.actors.base_actor import BaseActor
from ambient_actor.actors.interface import BaseActorInterface
# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DACA Ambient Agent", description="DACA Ambient Agent")

# Add Dapr Actor Extension
actor = DaprActor(app)


class Message(BaseModel):
    role: str
    content: str


# Register the actor
@app.on_event("startup")
async def startup():
    logging.info("Set the global client for the OpenAI Engine Adapter")
    api = os.getenv("GEMINI_API_KEY")
    logging.info(f"GEMINI_API_KEY: {api}")
    if api is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set")
    logging.info("Starting up the Ambient Agent")
    await actor.register_actor(BaseActor)
    logging.info(f"Registered actor: {BaseActor.__name__}")

@app.get("/app-health")
def health_check():
    return {"status": "ok"}

# Core Actor APIs
@app.post("/actor/{actor_id}/message")
async def process_user_message(actor_id: str, message: Message):
    """Process a message through the actor."""
    try:
        proxy = ActorProxy.create("BaseActor", ActorId(actor_id), BaseActorInterface)
        engine_config = {
            "run_method": "run",
            "engine_type": "openai",
            "name": "DACA Agent",
            "instructions": "You are a helpful assistant",
            "tools": [],
            "model": "gemini/gemini-2.0-flash"
        }
        input_data = {
            "message_data": message.model_dump(),
            "engine_config": engine_config,
            "engine_type": "openai"
        }
        logging.info(f"Processing message: {input_data}")
        result = await proxy.ProcessMessage(input_data)
        logging.info(f"Processed message: {result}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actor/{actor_id}/profile")
async def get_profile(actor_id: str):
    """Get the actor's profile and capabilities."""
    try:
        proxy = ActorProxy.create("BaseActor", ActorId(actor_id), BaseActorInterface)
        profile = await proxy.GetAgentProfile()
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/actor/{actor_id}/history")
async def get_conversation_history(actor_id: str):
    """Get the conversation history."""
    try:
        proxy = ActorProxy.create("BaseActor", ActorId(actor_id), BaseActorInterface)
        history = await proxy.GetConversationHistory()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
