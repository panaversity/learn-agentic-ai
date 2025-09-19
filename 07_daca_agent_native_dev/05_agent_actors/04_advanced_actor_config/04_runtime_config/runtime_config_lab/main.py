from collections.abc import Awaitable
from datetime import timedelta
import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, Remindable, actormethod
from dapr.clients import DaprClient
from typing import Callable

# --- Step 4.3: Add Reentrancy Configuration ---
from dapr.actor.runtime.config import ActorRuntimeConfig, ActorReentrancyConfig
from dapr.actor.runtime.runtime import ActorRuntime

# Configure Reentrancy (from Step 4.3)
reentrancy_config = ActorReentrancyConfig(enabled=True)

logging.info(f"Actor Runtime configured with Reentrancy: {reentrancy_config._enabled}")

# Configure Actor Runtime with additional parameters
runtime_config = ActorRuntimeConfig(
    actor_idle_timeout=timedelta(seconds=20), # Example: Set idle timeout to 10 minutes
    actor_scan_interval=timedelta(seconds=5), # Example: Scan for idle actors every 15 seconds
    drain_ongoing_call_timeout=timedelta(seconds=5), # Example: Wait up to 90s for calls during draining
    drain_rebalanced_actors=True, # Example: Keep draining enabled (default)
    reentrancy=reentrancy_config, # Include reentrancy config from Step 4.3
    # entitiesConfig=[] # Example: Per-entity config could go here if needed
)
ActorRuntime.set_actor_config(runtime_config)
logging.info(f"Actor Runtime configured:")
logging.info(f"  Idle Timeout: {runtime_config._actor_idle_timeout}")
logging.info(f"  Scan Interval: {runtime_config._actor_scan_interval}")
logging.info(f"  Drain Timeout: {runtime_config._drain_ongoing_call_timeout}")
logging.info(f"  Drain Enabled: {runtime_config._drain_rebalanced_actors}")
logging.info(f"  Reminder Partitions: {runtime_config._reminders_storage_partitions}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Ensure logs go to stdout
    ]
)

app = FastAPI(title="ChatAgentService", description="DACA Step 4.2: Reminders")

# Add Dapr Actor Extension
actor = DaprActor(app)

class Message(BaseModel):
    role: str
    content: str

# Define the actor interface
class ChatAgentInterface(ActorInterface):
    @actormethod(name="ProcessMessage")
    async def process_message(self, user_input: dict) -> dict | None:
        pass

    @actormethod(name="GetConversationHistory")
    async def get_conversation_history(self) -> list[dict] | None:
        pass

    @actormethod(name="ClearHistory")
    async def clear_history(self) -> None:
        pass

# Implement the actor
class ChatAgent(Actor, ChatAgentInterface, Remindable):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"
        self._actor_id = actor_id
        # Map reminder names to handler methods
        self._reminder_handlers: dict[str, Callable[[bytes], Awaitable[None]]] = {
            "ClearHistory": self.clear_history
        }

    async def _on_activate(self) -> None:
        """Initialize state and register reminder on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            try:
                await self._state_manager.get_state(self._history_key)
            except Exception as e:
                logging.info(f"State not found for {self._history_key}, initializing")
                await self._state_manager.set_state(self._history_key, [])

            # Register reminder to clear history after 10 seconds
            logging.info(f"\n ->[REMINDER] Registering ClearHistory reminder for {self._history_key}")
            try:
                await self.register_reminder(
                    name="ClearHistory",
                    state=b"clear_history_data",  # Non-empty state
                    due_time=timedelta(seconds=10),
                    period=timedelta(seconds=0),  # Non-repeating
                    ttl=timedelta(seconds=0)      # No expiration
                )
                logging.info(f"Successfully registered ClearHistory reminder for {self._history_key}")
            except Exception as e:
                logging.error(f"Failed to register ClearHistory reminder for {self._history_key}: {e}")
                raise
        except Exception as e:
            logging.error(f"Error in _on_activate for {self._history_key}: {e}")
            await self._state_manager.set_state(self._history_key, [])

    async def process_message(self, user_input: dict) -> dict:
        """Process a user message and append to history."""
        try:
            logging.info(f"Processing message for {self._history_key}: {user_input}")
            # Load history
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []

            # Append user message
            current_history.append(user_input)

            # Generate response
            response_content = f"Got your message: {user_input['content']}"
            response = {"role": "assistant", "content": response_content}

            # Append assistant response
            current_history.append(response)
            if len(current_history) > 5:  # Limit to last 5 exchanges
                current_history = current_history[-5:]

            # Save updated history
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Processed message for {self._history_key}: {user_input['content']}")

            # Publish event
            await self._publish_conversation_event(user_input, response)

            return response
        except Exception as e:
            logging.error(f"Error processing message for {self._history_key}: {e}")
            raise

    async def _publish_conversation_event(self, user_input: dict, response: dict) -> None:
        """Publish a ConversationUpdated event to the user-chat topic."""
        event_data = {
            "actor_id": self._actor_id.id,
            "history_key": self._history_key,
            "actor_type": "ChatAgent",
            "event_type": "ConversationUpdated",
            "input": user_input,
            "output": response
        }
        with DaprClient() as client:
            try:
                client.publish_event(
                    pubsub_name="daca-pubsub",
                    topic_name="user-chat",
                    data=json.dumps(event_data)
                )
                logging.info(f"Published event for {self._history_key}: {event_data}")
            except Exception as e:
                logging.error(f"Failed to publish event: {e}")

    async def get_conversation_history(self) -> list[dict]:
        """Retrieve conversation history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history for {self._history_key}: {e}")
            return []

    async def clear_history(self, state: bytes = b"") -> None:
        """Clear conversation history when reminder triggers."""
        try:
            logging.info(f"Clearing history for {self._history_key} due to reminder, state: {state.decode('utf-8') if state else 'empty'}")
            await self._state_manager.set_state(self._history_key, [])
            logging.info(f"History cleared for {self._history_key}")
        except Exception as e:
            logging.error(f"Error clearing history for {self._history_key}: {e}")
            raise

    async def receive_reminder(self, name: str, state: bytes, due_time: timedelta, period: timedelta, ttl: timedelta | None = None) -> None:
        """Handle reminder callbacks from Dapr dynamically."""
        logging.info(f"\n\n ->[REMINDER] Received reminder {name} for {self._history_key}")
        logging.info(f"\n\n ->[REMINDER] State: {state.decode('utf-8') if state else 'empty'}")
        handler = self._reminder_handlers.get(name)
        if handler:
            await handler(state)
            logging.info(f"Executed reminder handler for {name} in {self._history_key}")
        else:
            logging.warning(f"No handler found for reminder {name} in {self._history_key}")

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(ChatAgent)
    logging.info(f"Registered actor: {ChatAgent.__name__}")

# FastAPI endpoints to invoke the actor
@app.post("/chat/{actor_id}")
async def process_message(actor_id: str, data: Message):
    """Process a user message for the actor."""
    if not data.content or not isinstance(data.content, str):
        raise HTTPException(status_code=400, detail="Invalid or missing 'content' field")
    message_dict = data.model_dump()
    proxy = ActorProxy.create("ChatAgent", ActorId(actor_id), ChatAgentInterface)
    response = await proxy.ProcessMessage(message_dict)
    return {"response": response}

@app.get("/chat/{actor_id}/history")
async def get_conversation_history(actor_id: str):
    """Retrieve the actor's conversation history."""
    proxy = ActorProxy.create("ChatAgent", ActorId(actor_id), ChatAgentInterface)
    history = await proxy.GetConversationHistory()
    return {"history": history}

# Subscription endpoint for pub/sub events
@app.post("/subscribe")
async def subscribe_message(data: dict):
    """Handle events from the user-chat topic."""
    try:
        logging.info(f"\n\n->[SUBSCRIPTION] Received event: {data}\n\n")
        event_data_raw = data.get("data", "{}")
        event_data = json.loads(event_data_raw)
        user_id = event_data.get("actor_id", "unknown")
        input_message = event_data.get("input", {}).get("content", "no message")
        output_message = event_data.get("output", {}).get("content", "no response")
        logging.info(f"Received event: User {user_id} sent '{input_message}', got '{output_message}'")
        return {"status": "SUCCESS"}  # Dapr expects SUCCESS, RETRY, or DROP
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode event data: {e}")
        return {"status": "DROP"}