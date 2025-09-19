import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient
from typing import Callable, Any
from datetime import timedelta
from collections.abc import Awaitable

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Ensure logs go to stdout
    ]
)

app = FastAPI(title="ChatAgentService", description="DACA Step 4.2: Timers")

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

    @actormethod(name="LogMessageCount")
    async def log_message_count(self) -> None:
        pass

# Implement the actor
class ChatAgent(Actor, ChatAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"
        self._actor_id = actor_id
        self._timer_handlers: dict[Callable[[Any], Awaitable[None]]] = {
            "LogMessageCount": self.log_message_count
        }

    async def _on_activate(self) -> None:
        """Initialize state and register timer on actor activation."""
        logging.debug(f"Activating actor for {self._history_key}")
        try:
            try:
                await self._state_manager.get_state(self._history_key)
            except KeyError as e:
                logging.error(f"Error in _on_activate for {self._history_key}: {e}")
                await self._state_manager.set_state(self._history_key, [])
                await self._state_manager.save_state()  # Ensure state is persisted
                logging.debug(f"State initialized and saved for {self._history_key}")

            # Register timer to log message count every 5 seconds
            logging.debug(f"\n ->[TIMER] Registering LogMessageCount timer for {self._history_key}")
            await self.register_timer(
                name="LogMessageCount",
                callback=self._timer_handlers["LogMess ageCount"],
                due_time=timedelta(seconds=5),
                period=timedelta(seconds=5),
                state=None
            )
            logging.info(f"Successfully registered LogMessageCount timer for {self._history_key}")
        except Exception as e:
            logging.error(f"Error in _on_activate for {self._history_key}: {e}")
            raise

    async def process_message(self, user_input: dict) -> dict:
        """Process a user message and append to history."""
        try:
            logging.debug(f"Processing message for {self._history_key}: {user_input}")
            # Load history with fallback
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            # Append user message
            current_history.append(user_input)

            # Generate response
            response_content = f"Got your message: {user_input['content']}"
            response = {"role": "assistant", "content": response_content}

            # Append assistant response
            current_history.append(response)

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

    async def log_message_count(self, state: Any) -> None:
        """Log the number of messages in the history."""
        try:
            logging.debug(f"Logging message count for {self._history_key}")
            logging.debug(f"State: {state}")
            history = await self._state_manager.get_state(self._history_key)
            message_count = len(history) if isinstance(history, list) else 0
            logging.info(f"\n ->[TIMER] Triggered for {self._history_key}: {message_count} messages in history")
        except Exception as e:
            logging.error(f"Error logging message count for {self._history_key}: {e}")
            raise

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