import logging
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient
from google.protobuf.json_format import MessageToDict, ParseDict
import message_pb2

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ChatAgentService", description="DACA Step 8: Serialization")

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

# Implement the actor
class ChatAgent(Actor, ChatAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"
        self._actor_id = actor_id

    async def _on_activate(self) -> None:
        """Initialize state on actor activation and attempt migration."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            history_bytes = await self._state_manager.get_state(self._history_key)
            if not history_bytes:
                logging.info(f"State not found for {self._history_key}, initializing with Protobuf")
                await self._state_manager.set_state(self._history_key, message_pb2.ConversationHistory().SerializeToString())
            else:
                try:
                    history = message_pb2.ConversationHistory()
                    history.ParseFromString(history_bytes)
                    logging.info(f"Protobuf state found for {self._history_key}: {len(history_bytes)} bytes")
                except Exception as e:
                    logging.warning(f"Failed to parse Protobuf state for {self._history_key}. Attempting migration from list.")
                    try:
                        # Attempt to load as a list (assuming this was the old format)
                        old_history_list = json.loads(history_bytes.decode('utf-8'))
                        new_history = message_pb2.ConversationHistory()
                        for item in old_history_list:
                            msg = new_history.messages.add()
                            msg.role = item.get('role', '')
                            msg.content = item.get('content', '')
                        await self._state_manager.set_state(self._history_key, new_history.SerializeToString())
                        logging.info(f"Successfully migrated state for {self._history_key} to Protobuf.")
                    except Exception as migration_error:
                        logging.error(f"Failed to migrate state for {self._history_key}: {migration_error}")
                        # Consider initializing a new Protobuf state if migration fails
                        await self._state_manager.set_state(self._history_key, message_pb2.ConversationHistory().SerializeToString())
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate: {e}")
            await self._state_manager.set_state(self._history_key, message_pb2.ConversationHistory().SerializeToString())

    async def process_message(self, user_input: dict) -> dict:
        """Process a user message and append to history with Protobuf serialization."""
        try:
            logging.info(f"Processing message for {self._history_key}: {user_input}")
            # Load history
            history_bytes = await self._state_manager.get_state(self._history_key)
            history = message_pb2.ConversationHistory()
            if history_bytes:
                history.ParseFromString(history_bytes)
            else:
                history = message_pb2.ConversationHistory()
            
            # Append user message
            user_message = history.messages.add()
            user_message.role = user_input["role"]
            user_message.content = user_input["content"]
            
            # Generate response
            response_content = f"Got your message: {user_input['content']}"
            response = {"role": "assistant", "content": response_content}
            response_message = history.messages.add()
            response_message.role = response["role"]
            response_message.content = response["content"]
            
            # Limit to last 5 exchanges (10 messages, as each exchange has 2 messages)
            if len(history.messages) > 10:
                history.messages[:] = history.messages[-10:]
            
            # Save updated history
            await self._state_manager.set_state(self._history_key, history.SerializeToString())
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
        """Retrieve conversation history with Protobuf deserialization."""
        try:
            history_bytes = await self._state_manager.get_state(self._history_key)
            if not history_bytes:
                return []
            history = message_pb2.ConversationHistory()
            history.ParseFromString(history_bytes)
            # Convert Protobuf to list of dicts for compatibility
            history_dict = MessageToDict(history)
            return history_dict.get("messages", [])
        except Exception as e:
            logging.error(f"Error getting history for {self._history_key}: {e}")
            return []

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(ChatAgent)
    logging.info(f"Registered actor: {ChatAgent.__name__}")

@app.post("/test/json")
async def test_json(message: Message):
    raw = json.dumps(message.model_dump()).encode("utf-8")
    return {"encoding": "json", "size_bytes": len(raw)}

@app.post("/test/protobuf")
async def test_protobuf(message: Message):
    # Create a ConversationHistory protobuf message
    history = message_pb2.ConversationHistory()
    new_message = history.messages.add()
    new_message.role = message.role
    new_message.content = message.content

    # Serialize to bytes and return size
    proto_bytes = history.SerializeToString()
    return {"encoding": "protobuf", "size_bytes": len(proto_bytes)}

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
        return {"status": "SUCCESS"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode event data: {e}")
        return {"status": "FAILED"}