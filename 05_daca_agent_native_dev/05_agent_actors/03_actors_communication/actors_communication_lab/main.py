import logging
import json
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="MultiAgentService", description="DACA Step 3: Actor-to-Actor Communication")

# Add Dapr Actor Extension
actor = DaprActor(app)

class Message(BaseModel):
    role: str
    content: str

# Define actor interfaces
class ChatAgentInterface(ActorInterface):
    @actormethod(name="ProcessMessage")
    async def process_message(self, user_input: dict) -> dict | None:
        pass

    @actormethod(name="GetConversationHistory")
    async def get_conversation_history(self) -> list[dict] | None:
        pass

class ResponseAgentInterface(ActorInterface):
    @actormethod(name="ProcessMessage")
    async def process_message(self, user_input: dict) -> dict | None:
        pass

    @actormethod(name="GetMessageCount")
    async def get_message_count(self) -> int | None:
        pass

class MemoryAgentInterface(ActorInterface):
    @actormethod(name="UpdateMemory")
    async def update_memory(self, user_message: dict, response_message: dict) -> None:
        pass

    @actormethod(name="GetMemory")
    async def get_memory(self) -> list[dict] | None:
        pass

# Implement the ChatAgent (parent)
class ChatAgent(Actor, ChatAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"
        self._actor_id = actor_id

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating ChatAgent for {self._history_key}")
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

    async def process_message(self, user_input: dict) -> dict:
        """Delegate message processing to ResponseAgent."""
        try:
            logging.info(f"Processing message for {self._history_key}: {user_input}")

            # Load history
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            current_history.append(user_input)

            # Create ResponseAgent proxy
            response_actor_id = ActorId(f"response-{self._actor_id.id}")
            response_proxy = ActorProxy.create("ResponseAgent", response_actor_id, ResponseAgentInterface)
            
            # Delegate to ResponseAgent
            response = await response_proxy.ProcessMessage(user_input)
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
        # Note: publish_event is synchronous and may block; consider asyncio.to_thread in Step 5
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

# Implement the ResponseAgent (child)
class ResponseAgent(Actor, ResponseAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._count_key = f"response-count-{actor_id.id}"
        self._actor_id = actor_id

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating ResponseAgent for {self._count_key}")
        try:
            count = await self._state_manager.get_state(self._count_key)
            if count is None:
                logging.info(f"State not found for {self._count_key}, initializing")
                await self._state_manager.set_state(self._count_key, 0)
            else:
                logging.info(f"State found for {self._count_key}: {count}")
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate: {e}")
            await self._state_manager.set_state(self._count_key, 0)

    async def process_message(self, user_input: dict) -> dict:
        """Generate a response with timestamp and memory context."""
        try:
            logging.info(f"Processing message for {self._count_key}: {user_input}")

            # Increment message count
            count = await self._state_manager.get_state(self._count_key)
            count = count if isinstance(count, int) else 0
            count += 1
            await self._state_manager.set_state(self._count_key, count)
            logging.info(f"Incremented count for {self._count_key}: {count}")

            # Retrieve memory from MemoryAgentActor
            memory_actor_id = ActorId(f"memory-{self._actor_id.id}")
            memory_proxy = ActorProxy.create("MemoryAgentActor", memory_actor_id, MemoryAgentInterface)
            memory = await memory_proxy.GetMemory()
            memory_context = "; ".join([f"{m['role']}: {m['content']}" for m in memory]) if memory else f"Message count: {count}"
            logging.info(f"Memory context: {memory_context}")

            # Generate response with timestamp and memory
            timestamp = datetime.now(UTC).isoformat()
            response_content = f"Memory: {memory_context}. Got your message: {user_input['content']} at {timestamp}"
            response = {"role": "assistant", "content": response_content}
            
            logging.info(f"ResponseAgent processed message for {self._count_key}: {response_content}")
            return response
        except Exception as e:
            logging.error(f"Error processing message for {self._count_key}: {e}")
            raise

    async def get_message_count(self) -> int:
        """Retrieve the number of messages processed."""
        try:
            count = await self._state_manager.get_state(self._count_key)
            return count if isinstance(count, int) else 0
        except Exception as e:
            logging.error(f"Error getting count for {self._count_key}: {e}")
            return 0

# Implement the MemoryAgentActor (event-driven)
class MemoryAgentActor(Actor, MemoryAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._memory_key = f"memory-{actor_id.id}"
        self._count_key = f"memory-count-{actor_id.id}"

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating MemoryAgentActor for {self._memory_key}")
        try:
            memory = await self._state_manager.get_state(self._memory_key)
            count = await self._state_manager.get_state(self._count_key)
            if memory is None:
                logging.info(f"State not found for {self._memory_key}, initializing")
                await self._state_manager.set_state(self._memory_key, [])
            if count is None:
                logging.info(f"State not found for {self._count_key}, initializing")
                await self._state_manager.set_state(self._count_key, 0)
            else:
                logging.info(f"State found for {self._memory_key}: {memory}, count: {count}")
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate: {e}")
            await self._state_manager.set_state(self._memory_key, [])
            await self._state_manager.set_state(self._count_key, 0)

    async def update_memory(self, message: dict) -> None:
        """Update memory with user and response messages."""
        try:
            user_message = message.get("user_message")
            response_message = message.get("response_message")
            logging.info(f"\n -> Updating memory for {self._memory_key}: user={user_message}, response={response_message}")

            # Increment memory count
            count = await self._state_manager.get_state(self._count_key)
            count = count if isinstance(count, int) else 0
            count += 1
            await self._state_manager.set_state(self._count_key, count)
            logging.info(f"Incremented count for {self._count_key}: {count}")

            # Update memory
            memory = await self._state_manager.get_state(self._memory_key)
            current_memory = memory if isinstance(memory, list) else []
            current_memory.append(user_message)
            current_memory.append(response_message)
            await self._state_manager.set_state(self._memory_key, current_memory)
            logging.info(f"Updated memory for {self._memory_key}: {current_memory}, count: {count}")
        except Exception as e:
            logging.error(f"Error updating memory for {self._memory_key}: {e}")
            raise

    async def get_memory(self) -> list[dict]:
        """Retrieve memory."""
        try:
            memory = await self._state_manager.get_state(self._memory_key)
            logging.info(f"\n -> Memory: {memory}")
            return memory if isinstance(memory, list) else []
        except Exception as e:
            logging.error(f"Error getting memory for {self._memory_key}: {e}")
            return []

# Register actors
@app.on_event("startup")
async def startup():
    await actor.register_actor(ChatAgent)
    await actor.register_actor(ResponseAgent)
    await actor.register_actor(MemoryAgentActor)
    logging.info("Registered actors: ChatAgent, ResponseAgent, MemoryAgentActor")

# FastAPI endpoints
@app.post("/chat/{actor_id}")
async def process_message(actor_id: str, data: Message):
    """Process a user message via ChatAgent."""
    logging.info(f"Processing message for {actor_id}: {data}")
    if not data.content or not isinstance(data.content, str):
        raise HTTPException(status_code=400, detail="Invalid or missing 'content' field")
    message_dict = data.model_dump()
    proxy = ActorProxy.create("ChatAgent", ActorId(actor_id), ChatAgentInterface)
    response = await proxy.ProcessMessage(message_dict)
    return {"response": response}

@app.get("/chat/{actor_id}/history")
async def get_conversation_history(actor_id: str):
    """Retrieve ChatAgent's conversation history."""
    proxy = ActorProxy.create("ChatAgent", ActorId(actor_id), ChatAgentInterface)
    history = await proxy.GetConversationHistory()
    return {"history": history}

@app.get("/response/{actor_id}/count")
async def get_message_count(actor_id: str):
    """Retrieve ResponseAgent's message count."""
    proxy = ActorProxy.create("ResponseAgent", ActorId(f"response-{actor_id}"), ResponseAgentInterface)
    count = await proxy.GetMessageCount()
    return {"count": count}

@app.get("/memory/{actor_id}")
async def get_memory(actor_id: str):
    """Retrieve MemoryAgentActor's memory."""
    proxy = ActorProxy.create("MemoryAgentActor", ActorId(f"memory-{actor_id}"), MemoryAgentInterface)
    memory = await proxy.GetMemory()
    return {"memory": memory}

@app.post("/subscribe")
async def subscribe_message(data: dict):
    """Handle events from the user-chat topic and trigger MemoryAgentActor."""
    try:
        logging.info(f"Received raw event data: {data}")
        # Dapr sends event data in a structure with 'data' field
        event_data = data.get("data", {})
        if isinstance(event_data, str):
            event_data = json.loads(event_data)
        logging.info(f"PARSED Event data: {event_data}")
        user_id = event_data.get("actor_id", "unknown")
        input_message = event_data.get("input", {})
        output_message = event_data.get("output", {})
        
        # Trigger MemoryAgentActor
        memory_actor_id = ActorId(f"memory-{user_id}")
        memory_proxy = ActorProxy.create("MemoryAgentActor", memory_actor_id, MemoryAgentInterface)
        await memory_proxy.UpdateMemory({
            "user_message": input_message,
                "response_message": output_message
            })
        
        logging.info(f"Processed event: User {user_id} sent '{input_message.get('content', '')}', got '{output_message.get('content', '')}'")
        return {"status": "Event processed"}
    except Exception as e:
        logging.error(f"Failed to process event data: {e}")
        return {"status": f"Error: {str(e)}"}