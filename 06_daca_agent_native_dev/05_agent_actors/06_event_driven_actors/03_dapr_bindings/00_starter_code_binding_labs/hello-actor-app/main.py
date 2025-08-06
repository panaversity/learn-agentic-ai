import logging
from fastapi import FastAPI
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Hello Actor App", description="Starter Code for Bindings")

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
            history = await self._state_manager.get_state(self._history_key)
            if history is None:
                logging.info(f"State not found for {self._history_key}, initializing")
                await self._state_manager.set_state(self._history_key, [])
            else:
                logging.info(f"State found for {self._history_key}: {history}")
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate: {e}")
            await self._state_manager.set_state(self._history_key, [])

    async def add_greeting(self, greeting_data: dict) -> None:
        """Add a greeting to history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            current_history.append(greeting_data)
            if len(current_history) > 5:  # Limit to last 5 greetings
                current_history = current_history[-5:]
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Added greeting for {self._history_key}: {greeting_data}")
        except Exception as e:
            logging.error(f"Error adding greeting: {e}")
            raise

    async def get_greeting_history(self) -> list[dict] | None:
        """Retrieve greeting history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history: {e}")
            return []

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(HelloAgent)
    logging.info(f"Registered actor: {HelloAgent.__name__}")

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