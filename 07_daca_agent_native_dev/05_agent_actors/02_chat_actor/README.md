# Step 2: Chat Actor - Building a Chat Agent

This is the second step of building **AI Agents as Dapr Virtual Actors** in the **Dapr Agentic Cloud Ascent (DACA)** design pattern, as part of the [AI Agents as Virtual Actors learning path](#). In this step, you’ll implement a `ChatAgent` actor that maintains conversation history and uses Dapr’s pub/sub for event-driven communication, building on the `HelloAgent` from Step 1. This step introduces complex state management and asynchronous messaging, setting the stage for scalable, interactive AI agents.

## Overview

The **chat_actor** step extends Dapr Virtual Actors to model a conversational AI agent. You’ll implement a `ChatAgent` actor that:
- Accepts user messages via a `process_message` method, appending them to a conversation history and returning a response.
- Stores the history (user and assistant messages) in a Redis state store, limited to the last 5 exchanges.
- Publishes `ConversationUpdated` events to a Dapr pub/sub topic for event-driven communication.
- Retrieves the conversation history via a `get_conversation_history` method.

The actor integrates with FastAPI using the `DaprActor` extension, and each unique `actor_id` (e.g., `user1`) creates a separate `ChatAgent` instance, ensuring per-user conversation isolation. This aligns with DACA’s goal of building concurrent, scalable systems and prepares you for integrating AI models in later steps.

### Learning Objectives
- Manage complex actor state (conversation history) with Dapr’s state store.
- Define actor methods for specific interactions (e.g., processing messages).
- Understand actor ID uniqueness and per-user instance creation.
- Implement pub/sub for event-driven communication in Dapr.
- Use FastAPI endpoints for request/response interaction patterns.

### Ties to README
- **Actors as the Fundamental Unit**: The `ChatAgent` encapsulates state (conversation history) and behavior (message processing, event publishing).
- **State Persistence**: Dapr persists actor state in Redis, ensuring durable conversations.
- **Dapr’s Implementation of the Actor Model**: Virtual Actors support scalable, per-user instances.
- **Pub/Sub Messaging**: Introduces asynchronous, event-driven communication for AI agent interactions.

## Key Concepts

### Complex Actor State
The `ChatAgent` manages conversation history as a list of dictionaries (e.g., `[{"user": "Hi", "assistant": "Hello!"}]`), stored in Redis with a key like `history-user1`. This state is:
- **Complex**: A structured list, unlike Step 1’s simple greeting list.
- **Persistent**: Saved in Redis for durability across actor activations.

### Actor Methods
The `ChatAgent` defines:
- `process_message(user_input: str) -> str`: Appends the user’s message and a static response (e.g., “Got your message: {input}”) to the history, publishes an event, and returns the response.
- `get_conversation_history() -> List[Dict]`: Retrieves the history for the actor’s `ActorId`.

These methods handle specific interactions, supporting DACA’s goal of modular, task-focused AI agents.

### Actor ID Uniqueness
Each `ActorId` (e.g., `user1`, `user2`) creates a unique `ChatAgent` instance, ensuring isolated state. For example:
- `user1`’s history (`history-user1`) is separate from `user2`’s (`history-user2`).
- Multiple calls to `/chat/user1` reuse the same `user1` instance, maintaining a single conversation thread per user.

This per-user model is ideal for AI agents, where each user or session requires independent state.

### Interaction Patterns
The `ChatAgent` supports:
- **Request/Response**: FastAPI endpoints (`/chat/{actor_id}`) allow clients to send messages and receive responses synchronously.
- **Event-Driven**: Pub/sub publishes `ConversationUpdated` events to a `conversations` topic, enabling asynchronous communication (e.g., notifying other services of new messages).

### Dapr Pub/Sub
Dapr’s pub/sub component enables event-driven communication. The `ChatAgent` uses `DaprClient` to publish `ConversationUpdated` events to the `user-chat` topic on the `daca-pubsub` component. The `/subscribe` endpoint, configured via `message-subscription.yaml`, receives these events, allowing other services to react (e.g., logging or notifying users). This introduces asynchronous messaging, a key pattern for scalable AI systems in DACA.

## Hands-On Dapr Virtual Actor

### 0. Setup Code
Use the [00_lab_starter_code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code). Ensure Step 1 is complete, as this step builds on its setup.

Install additional dependencies:
```bash
uv add dapr-ext-fastapi
```

Start the application:
```bash
tilt up
```

### 1. Configure Dapr Components
The starter code includes `statestore.yaml`, `daca-pubsub.yaml`, and `message-subscription.yaml`. Verify their presence in the `components/` directory.

**File**: `components/statestore.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

**File**: `components/daca-pubsub.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: daca-pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379
  - name: redisPassword
    value: ""
```

**File**: `components/message-subscription.yaml`
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: message-subscription
spec:
  pubsubname: daca-pubsub
  topic: user-chat
  routes:
    default: /subscribe
    rules:
      - match: event.type == "update"
        path: /subscribe
```


### 2. Implement the ChatAgent Actor
Create a Python application with a `ChatAgent` actor that manages conversation history, processes messages, and publishes events using `DaprClient`.


**File**: `main.py`
```python
import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ChatAgentService", description="DACA Step 2: Chat Actor")

# Add Dapr Actor Extension
actor = DaprActor(app)

class Message(BaseModel):
    role: str
    content: str

# Define the actor interface
class ChatAgentInterface(ActorInterface):
    @actormethod(name="ProcessMessage")
    async def process_message(self, user_input: Message) -> Message | None:
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

    async def process_message(self, user_input: Message) -> Message:
        """Process a user message and append to history."""
        try:
            logging.info(f"Processing message for {self._history_key}: {user_input}")
            user_input = Message.model_validate(user_input)
            # Load history
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            
            # Append user message
            current_history.append({"role": "user", "content": user_input.content})
            
            # Generate response (static for simplicity)
            # CHALLENGE: Make the response dynamic by calling an LLM (e.g., via an API like Gemini)
            response = Message(role="assistant", content=f"Got your message: {user_input.content}")
            
            # Append assistant response
            current_history.append(response.model_dump())
            if len(current_history) > 5:  # Limit to last 5 exchanges
                current_history = current_history[-5:]
            
            # Save updated history
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Processed message for {self._history_key}: {user_input.content}")
            
            # Publish event
            await self._publish_conversation_event(user_input, response)
            
            return response.model_dump()
        except Exception as e:
            logging.error(f"Error processing message for {self._history_key}: {e}")
            raise

    async def _publish_conversation_event(self, user_input: Message, response: Message) -> None:
        """Publish a ConversationUpdated event to the user-chat topic."""
        event_data = {
            "actor_id": self._actor_id.id,
            "history_key": self._history_key,
            "actor_type": "ChatAgent",
            "event_type": "ConversationUpdated",
            "input": user_input.model_dump(),
            "output": response.model_dump()
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
    proxy = ActorProxy.create("ChatAgent", ActorId(actor_id), ChatAgentInterface)
    response = await proxy.ProcessMessage(data.model_dump())
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

### 3. Test the App
Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to explore endpoints interactively.

Test the **Actor** route group:
- **GET /healthz**: Verifies Dapr actor configuration (`200 OK` indicates health).
- **GET /dapr/config**: Shows registered actors (`ChatAgent` should appear).

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message and receives a response.
- **GET /chat/{actor_id}/history**: Retrieves the conversation history.
- **POST /subscribe**: Handles `user-chat` topic events (triggered automatically by pub/sub).

### 4. Understand the Code
Review the `main.py` code:
- **Actor Interface**: Defines `ProcessMessage` and `GetConversationHistory` with `@actormethod`.
- **Actor Implementation**: Manages conversation history in Redis, publishes events via `DaprClient`, and handles messages.
- **FastAPI Endpoints**: Invokes the actor via `ActorProxy` for request/response, and handles pub/sub events via `/subscribe`.
- **Pub/Sub**: Publishes `ConversationUpdated` events to the `user-chat` topic, processed by `/subscribe`.

The actor processes messages asynchronously: a POST to `/chat/user1` sends a message to the `user1` actor’s mailbox, triggering `process_message` to update the history and publish an event, which is logged by `/subscribe`.

### 5. Observe the Dapr Dashboard
Open the Dapr dashboard to monitor actor instances:
```bash
dapr dashboard
```
Navigate to the **Actors** tab. Expect to see `ChatAgent` with a count of active instances (e.g., `2` for `user1` and `user2`). If the count is higher (e.g., `3`), see **Troubleshooting**.

## Validation

Verify the `ChatAgent` works as expected:
1. **Message Processing**: POST requests to `/chat/{actor_id}` return a response (e.g., `{"response": "Got your message: Hi"}`).
2. **History Retrieval**: GET requests to `/chat/{actor_id}/history` return the correct history, with up to 5 entries.
3. **State Persistence**: Send multiple POSTs for the same `actor_id` and confirm the history persists in Redis (e.g., `history-user1`).
4. **Per-User Isolation**: Verify `user1` and `user2` have separate histories, confirming each `ActorId` has its own instance.
5. **Dashboard Count**: Confirm the Dapr dashboard shows the expected number of `ChatAgent` instances (e.g., `2` for `user1` and `user2`).
6. **Subscription**: Verify `/subscribe` logs events (e.g., `Received event: User user1 sent 'Hi there', got 'Got your message: Hi there'`).

## Key Takeaways
- **Complex Actor State**: The `ChatAgent` manages conversation history as a structured list, persisted in Redis.
- **Actor Methods**: `process_message` and `get_conversation_history` handle specific interactions, supporting modular AI agents.
- **Actor ID Uniqueness**: Each `ActorId` creates a unique `ChatAgent` instance, enabling per-user conversations.
- **Interaction Patterns**: Request/response via FastAPI and event-driven pub/sub provide flexible communication.
- **Dapr Pub/Sub**: Using `DaprClient` to publish events to `user-chat` enables asynchronous, scalable messaging.

# Challenge
Here we have mocked the ai workflow. As a challenge project you will integrate openai agents sdk as agentic engine in this code. 

## Next Steps
- Proceed to **Step 3: multi_actors** to integrate multiple actors for collaborative AI tasks.
- Experiment with dynamic responses in `process_message` (e.g., add rule-based logic or a mock AI).
- Create a separate service to subscribe to `user-chat` events and process them (e.g., store logs).
- Inspect Redis state with `redis-cli` (e.g., `GET history-user1`) to understand persistence.

## Resources
- [Dapr Actors Overview](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/)
- [Dapr Pub/Sub Overview](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-overview/)
- [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [Dapr Python SDK Pub/Sub](https://docs.dapr.io/developing-applications/sdks/python/python-pubsub/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/04_security_fundamentals/00_lab_starter_code)