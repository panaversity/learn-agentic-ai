# Step 2: Serialization

In this step, you’ll enhance the `ChatAgent` actor from **Agent Actors Step 2** by implementing custom serialization using Protocol Buffers (Protobuf) for conversation history stored in Redis. This optimizes storage and performance, aligning with DACA’s goal of building efficient, scalable AI agents.

## Overview

The **serialization** step modifies the `ChatAgent` to:
- Define a Protobuf schema for conversation history messages.
- Serialize conversation history to Protobuf format before saving to Redis and deserialize on retrieval.
- Test serialization by verifying reduced storage size and correct history retrieval.
- Preserve the existing `process_message` and `get_conversation_history` functionality from **Step 2**.

Custom serialization with Protobuf reduces state size and improves performance compared to JSON, benefiting AI agents with large conversation histories.

## Is this Worth It or an Overhead?

### ✅ **Actual Value of Using Protobuf Here**

**1. Size & Speed Gains in Real Workloads**

* **Smaller storage size**: Protobuf messages are *much* more compact than JSON. In large-scale deployments (thousands of actors, each with long histories), this reduces Redis memory footprint and network I/O.
* **Faster processing**: Protobuf is faster than JSON for both serialization and deserialization, which matters under load.

**2. Schema Enforcement**

* You define a `.proto` contract—making the stored structure explicit and versionable.
* This adds safety and clarity, especially when multiple services interact with state.

**3. Migration-Ready**

* The `_on_activate()` migration logic helps transition existing JSON data to Protobuf safely.
* This is a realistic and mature step in building **production-ready** systems.

---

### ⚠️ **But Also Consider the Overhead**

**1. Increased Complexity**

* You add `.proto` files, code generation steps, and manual field mapping (`MessageToDict`, etc.).
* Debugging Protobuf in Redis is harder than just looking at JSON.

**2. Not Needed for Simple/Short Histories**

* If your app deals with short chats (e.g., 5–10 messages) or runs few actors, **Protobuf likely gives negligible performance benefits**.
* JSON is more human-readable and requires less tooling.

**3. Redis Isn’t the Bottleneck Yet**

* For most Dapr setups, **Redis network or Dapr actor activation latency** are bigger bottlenecks than JSON overhead.

---

### 🟡 **So, Is It Worth it?**

If your **goal is to learn production techniques**, especially in:

* **High-throughput multi-user actor systems**
* **Latency-sensitive, memory-constrained environments**
* **Prepping for multi-language, cross-service communication**

➡️ Then **yes**, this is a *valuable step* with clear scalability implications.

But if your app is:

* Small-scale or educational,
* Mostly for local experimentation,
* And you're not seeing Redis memory or performance issues,

➡️ Then **no**, this step adds overhead you might skip for now.

Note: Dapr uses both HTTP and GRPC Protocols. To [enable GRPC for communication](https://docs.dapr.io/operations/configuration/grpc/) you can following this config guide.

### Learning Objectives
- Implement custom serialization with Protocol Buffers for actor state.
- Optimize state storage and retrieval in Redis.
- Validate serialized state data and performance.
- Maintain lightweight changes with minimal code modifications.

### Ties to DACA
- **Efficiency**: Protobuf reduces storage and network overhead, improving performance.
- **Scalability**: Optimized state handling supports high user loads.
- **Production-Readiness**: Custom serialization ensures efficient data management for AI agents.

## Key Concepts

### Dapr State Serialization
Dapr uses JSON serialization by default for state stores like Redis. Custom serialization (e.g., Protobuf) offers:
- **Compact Data**: Protobuf produces smaller payloads than JSON, reducing storage and bandwidth.
- **Performance**: Faster serialization/deserialization improves state operations.
- **Schema Definition**: Protobuf requires a schema (`.proto` file) to define data structures.

In this step, you’ll define a Protobuf schema for conversation history, serialize history to Protobuf before saving to Redis, and deserialize on retrieval, optimizing `ChatAgent` state management.

### Lightweight Configuration
Serialization is added with minimal changes:
- A new Protobuf schema file (`message.proto`) for conversation history.
- A dependency (`protobuf`) and generated Python code for serialization/deserialization.
- Updates to `ChatAgent`’s state management methods to use Protobuf.
- No changes to Dapr components or pub/sub, keeping the setup lightweight.

### Interaction Patterns
The `ChatAgent` supports:
- **Request/Response**: FastAPI endpoints (`/chat/{actor_id}`, `/chat/{actor_id}/history`) with Protobuf-serialized state.
- **Event-Driven**: Pub/sub events via `/subscribe` for `ConversationUpdated`.
- **Efficient Storage**: Conversation history is stored in compact Protobuf format in Redis.

## Hands-On Dapr Virtual Actor

### 0. Setup Code
Use the [00_lab_starter_code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code) from **Step 2**. Ensure **Step 2** is complete and you have a Kubernetes cluster (e.g., `minikube`).

Install additional dependencies:
```bash
uv add protobuf grpcio-tools
```

### 1. Define Protobuf Schema
Create a Protobuf schema for the conversation history.

**File**: `message.proto`
```protobuf
syntax = "proto3";

message Message {
  string role = 1;
  string content = 2;
}

message ConversationHistory {
  repeated Message messages = 1;
}
```

Generate Python code from the schema:
```bash
uv run python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. message.proto
```

This creates `message_pb2.py` and `message_pb2.pyi` for use in `main.py`.

### 2. Configure Dapr Components
Keep the **Step 2** components (`statestore.yaml`, `daca-pubsub.yaml`, `message-subscription.yaml`) unchanged (see **Step 4.1** README), as serialization is handled in the application code.

### 3. Update the ChatAgent Code
Update the **Step 2** `main.py` to use Protobuf for serializing/deserializing conversation history.

**File**: `main.py`
```python
import logging
import json
from fastapi import FastAPI, HTTPException
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
        return {"status": "Event processed"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode event data: {e}")
        return {"status": "Invalid event data format"}
```

### 4. Test the App

```bash
tilt up
```

#### Understand Protobuf vs JSON (Post `tilt up`)

Before diving into how we're using Protobuf in the actor's state, let’s **understand why we're switching from JSON to Protobuf**, and how they differ.

##### 🔍 What’s the Difference?

| Feature            | JSON                  | Protobuf                          |
| ------------------ | --------------------- | --------------------------------- |
| Human-readable     | ✅ Yes                 | ❌ No (binary)                     |
| Schema enforcement | ❌ No                  | ✅ Yes (`.proto` files required)   |
| Payload size       | ❌ Larger (text-based) | ✅ Smaller (compact binary format) |
| Speed              | ❌ Slower to parse     | ✅ Faster to serialize/deserialize |
| Flexibility        | ✅ Very flexible       | ❌ Requires compiled definitions   |

---

##### 🧪 Try It Yourself: Test JSON vs Protobuf Encoding

Use these two test endpoints we’ve added in the FastAPI service to compare the serialization formats:

#####  ➤ 1. JSON Test

```bash
curl -X POST http://localhost:8000/test/json \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "hello"}'
```

**Expected Output:**

```json
{
  "encoding": "json",
  "size_bytes": 36
}
```

#### ➤ 2. Protobuf Test

```bash
curl -X POST http://localhost:8000/test/protobuf \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "hello"}'
```

**Expected Output:**

```json
{
  "encoding": "protobuf",
  "size_bytes": 15
}
```

The Protobuf version is nearly **half the size** — that’s the advantage of binary serialization!

---

### 🧠 What’s Actually Happening?

Here’s a visual summary:

```
Message JSON (text)             ➝  {"role": "user", "content": "hello"}
Size: ~36 bytes

Message Protobuf (binary)       ➝  [binary stream]
Size: ~15 bytes
```

> 💡 We use Protobuf in Dapr actors to **store conversation history compactly** and **enforce structure**.

---

Now we will can move on to:

* How the actor now saves history using `message_pb2.ConversationHistory`
* The migration fallback logic
* The size difference in persisted state
* Event publication using Protobuf-originated data

#### Testing ChatAgent

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message.
- **GET /chat/{actor_id}/history**: Retrieves the conversation history.
- **POST /subscribe**: Handles `user-chat` topic events.

Use `curl` commands to generate state data:
```bash
curl -X POST http://localhost:8000/chat/user1 -H "Content-Type: application/json" -d '{"role": "user", "content": "Hi there"}'
curl -X POST http://localhost:8000/chat/user1 -H "Content-Type: application/json" -d '{"role": "user", "content": "Hello"}'
curl http://localhost:8000/chat/user1/history
```

Check Redis to verify serialized data size:
```bash
kubectl exec -it $(kubectl get pods -n default | grep redis | awk '{print $1}') -- redis-cli
TYPE daca-ai-app||ChatAgent||user1||history-user1
HGETALL daca-ai-app||ChatAgent||user1||history-user1
```

**Expected Output**:
- POST: `{"response": {"role": "assistant", "content": "Got your message: Hi there"}}`
- GET: `{"history": [{"role": "user", "content": "Hi there"}, {"role": "assistant", "content": "Got your message: Hi there"}, {"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Got your message: Hello"}]}`
- Redis GET: Binary data (e.g., `"\x0a\x0e..."`), indicating Protobuf serialization.

### 5. Understand the Setup
Review the setup:
- **Code Changes**: Updated `_on_activate`, `process_message`, and `get_conversation_history` to use Protobuf serialization/deserialization.
- **Protobuf Schema**: `message.proto` defines the conversation history structure.
- **Dependency**: Added `protobuf` for Protobuf handling.
- **Existing Functionality**: Preserves `process_message`, `get_conversation_history`, and pub/sub from **Step 2**.

Protobuf serialization reduces state size and improves performance, optimizing `ChatAgent` for large conversation histories.

### 6. Observe the Dapr Dashboard
Run:
```bash
dapr dashboard
```
Check the **Actors** tab for `ChatAgent` instances (e.g., `1` for `user1`). Use `redis-cli` to confirm serialized state data, and check logs (`dapr logs -a chat-agent`) for successful state operations with Protobuf.

## Validation
Verify serialization functionality:
1. **Message Processing**: POST to `/chat/user1` succeeds and stores history.
2. **History Retrieval**: GET `/chat/user1/history` returns the correct history, indicating proper deserialization.
3. **Serialized State**: Use `redis-cli GET history-user1` to confirm binary Protobuf data (not JSON).
5. **Logs**: Check `dapr logs -a chat-agent` for no serialization errors and correct message processing.

## Key Takeaways
- **Serialization**: Protobuf optimizes state storage and performance for conversation history.
- **Lightweight Configuration**: Minimal code changes and a Protobuf schema enable custom serialization.
- **Efficiency**: Reduced state size supports scalable AI agents.
- **DACA Alignment**: Enhances performance for conversational AI in distributed systems.

## Next Steps
- Experiment with other serialization formats (e.g., Avro, MessagePack).
- Measure performance improvements with large conversation histories (e.g., 100 exchanges).

## Resources
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [Python Protobuf](https://developers.google.com/protocol-buffers/docs/pythontutorial)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code)