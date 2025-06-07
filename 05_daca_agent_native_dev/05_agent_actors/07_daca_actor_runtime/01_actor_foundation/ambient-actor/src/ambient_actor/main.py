import logging

from fastapi import FastAPI
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DACA Ambient Agent", description="DACA Ambient Agent")

# Add Dapr Actor Extension
actor = DaprActor(app)

# Define the actor interface
class HelloAgentInterface(ActorInterface):
    @actormethod(name="AddGreeting")
    async def add_greeting(self, greeting_data: dict) -> None:
        pass

    @actormethod(name="GetGreetingHistory")
    async def get_greeting_history(self) -> list[dict] | None:
        pass

# Implement the actor
class HelloAgent(Actor, HelloAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            await self._state_manager.get_state(self._history_key)
        except KeyError as e:
            logging.info(f"State not found for {self._history_key}, initializing")
            await self._state_manager.set_state(self._history_key, [])
        except Exception as e:
            logging.warning(f"Exception in _on_activate: {e}")
            raise e

    async def add_greeting(self, greeting_data: dict) -> None:
        """Add a greeting to history."""
        try:
            current_history: list = await self._state_manager.get_state(self._history_key)
            current_history.append(greeting_data)
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Added greeting for {self._history_key}: {greeting_data}")
        except Exception as e:
            logging.error(f"Error adding greeting: {e}")
            raise

    async def get_greeting_history(self) -> list[dict] | None:
        """Retrieve greeting history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history
        except Exception as e:
            logging.error(f"Error getting history: {e}")
            return []

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(HelloAgent)
    logging.info(f"Registered actor: {HelloAgent.__name__}")

@app.get("/app-health")
def health_check():
    return {"status": "ok"}

# FastAPI endpoints to invoke the actor
@app.post("/greet/{actor_id}")
async def add_greeting(actor_id: str, greeting: dict):
    """Add a greeting to the actor's history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    await proxy.AddGreeting(greeting)
    return {"status": "Greeting added"}

@app.get("/greet/{actor_id}/history")
async def get_greeting_history(actor_id: str):
    """Retrieve the actor's greeting history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    history = await proxy.GetGreetingHistory()
    return {"history": history}