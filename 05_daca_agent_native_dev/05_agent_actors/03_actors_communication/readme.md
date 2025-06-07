# Step 3: Actor-to-Actor Communication (Basic Introduction)

This is the third step of building **AI Agents as Dapr Virtual Actors** in the **Dapr Agentic Cloud Ascent (DACA)** design pattern, as part of the [AI Agents as Virtual Actors learning path](#). 

In this step, you’ll create an advanced multi-agent system with three actors: 
1. a `ChatAgent` (parent), 
2. a `ResponseAgent` (child), and 
3. a `MemoryAgentActor` (event-driven). 

The `ChatAgent` delegates message processing to the `ResponseAgent`, which uses memory from the `MemoryAgentActor` to generate context-aware responses. The `MemoryAgentActor` updates memory based on `ConversationUpdated` events from the `user-chat` pub/sub topic. You’ll learn dynamic actor creation, actor proxies, fault isolation, and event-driven memory management, advancing your skills in building scalable, modular AI agents.

## Overview

The **actors communication** step enhances the Step 2 `ChatAgent` by introducing actor-to-actor communication and memory management. You’ll implement:
- A `ChatAgent` that receives user messages and delegates response generation to a `ResponseAgent`.
- A `ResponseAgent` that generates timestamped responses, enriched with memory from the `MemoryAgentActor`.
- A `MemoryAgentActor` that updates a memory store based on pub/sub events, triggered via the `/subscribe` endpoint.
- Actor proxies to enable asynchronous communication between actors.
- FastAPI endpoints to trigger the system and inspect state.

Each `actor_id` (e.g., `user1`) creates unique instances of `ChatAgent` (`user1`), `ResponseAgent` (`response-user1`), and `MemoryAgentActor` (`memory-user1`), with isolated state in Redis. This system demonstrates collaborative AI agent workflows, aligning with DACA’s goals of building concurrent, resilient, and context-aware systems.

### Learning Objectives
- Dynamically create child actors (`ResponseAgent`, `MemoryAgentActor`) for task-specific roles.
- Use actor proxies for asynchronous communication between actors.
- Ensure fault isolation through independent actor state and execution.
- Trigger memory updates via pub/sub events for event-driven design.
- Incorporate memory into responses for context awareness.
- Validate multi-agent interactions and state persistence.

### Ties to Actor Module Goals:
- **Dynamic Agent Creation**: Spawning `ResponseAgent` and `MemoryAgentActor` mirrors AI systems with task-specific sub-agents.
- **Asynchronous Message Passing**: Proxies and pub/sub enable non-blocking communication, supporting scalability.
- **Fault Isolation**: Isolated actors ensure resilience, a key DACA requirement.
- **Context Awareness**: Memory integration prepares for AI-driven agents.

## Key Concepts

### Actor Model Recap
The **Actor Model** (Hewitt, 1973) defines actors as independent entities with:
- **State**: Private data (e.g., `ChatAgent`’s history, `ResponseAgent`’s count, `MemoryAgentActor`’s memory).
- **Behavior**: Logic to process messages (e.g., delegating, responding, updating memory).
- **Mailbox**: A queue for asynchronous message processing, one at a time.

A POST to `/chat/user1` triggers `ChatAgent` to delegate to `ResponseAgent`, which queries `MemoryAgentActor` for memory. Pub/sub events trigger `MemoryAgentActor` to update memory, all asynchronously via Dapr’s actor model.

### Dynamic Actor Creation
The `ChatAgent` spawns a `ResponseAgent` (`response-user1`), and the `/subscribe` endpoint spawns a `MemoryAgentActor` (`memory-user1`) for each `actor_id`. Actors are created dynamically using Dapr’s actor framework, supporting AI systems where agents spawn sub-agents for tasks like response generation or memory management.

### Actor Proxies
Dapr’s `ActorProxy` enables:
- `ChatAgent` to invoke `ResponseAgent.process_message`.
- `ResponseAgent` to invoke `MemoryAgentActor.get_memory`.
- `/subscribe` to invoke `MemoryAgentActor.update_memory`.
Proxies abstract communication details, ensuring asynchronous message passing in a distributed system.

### Fault Isolation
Each actor operates independently:
- **State Isolation**: `ChatAgent` uses `history-user1`, `ResponseAgent` uses `response-count-user1`, `MemoryAgentActor` uses `memory-user1`.
- **Execution Isolation**: Errors in one actor (e.g., `ResponseAgent` failing) don’t affect others.
- **Single-Threaded Execution**: Dapr ensures each actor processes one message at a time, preventing race conditions.

### Pub/Sub and Memory Management
The `ChatAgent` publishes `ConversationUpdated` events to the `user-chat` topic. The `/subscribe` endpoint triggers `MemoryAgentActor` to update a memory store (e.g., recent messages), which `ResponseAgent` retrieves to enrich responses. This event-driven approach supports scalable, context-aware AI agents.

### Interaction Patterns
The system supports:
- **Request/Response**: FastAPI endpoints trigger `ChatAgent`, which delegates to `ResponseAgent`.
- **Event-Driven**: Pub/sub triggers `MemoryAgentActor` via `/subscribe`.
- **Actor-to-Actor**: Proxies enable `ChatAgent` → `ResponseAgent` → `MemoryAgentActor` communication.

## Hands-On Dapr Virtual Actor

### 0. Setup Code
Use the [00_lab_starter_code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code). Ensure Step 2 is complete.

Install dependencies:
```bash
uv add dapr dapr-ext-fastapi
```

Start the application:
```bash
tilt up
```

### 1. Configure Dapr Components
The starter code includes `statestore.yaml`, `daca-pubsub.yaml`, and `message-subscription.yaml`. Verify their presence in `components/`.

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

### 2. Implement the Multi-Agent System
Create a Python application with `ChatAgent`, `ResponseAgent`, and `MemoryAgentActor`.

**File**: `main.py`
```python
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
```

### 3. Test the App
Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to explore endpoints interactively.

Test the **Actor** route group:
- **GET /healthz**: Verifies Dapr actor configuration (`200 OK` indicates health).
- **GET /dapr/config**: Shows registered actors (`ChatAgent`, `ResponseAgent`, `MemoryAgentActor`).

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message to `ChatAgent`, which delegates to `ResponseAgent`.
- **GET /chat/{actor_id}/history**: Retrieves `ChatAgent`’s conversation history.
- **GET /response/{actor_id}/count**: Retrieves `ResponseAgent`’s message count.
- **GET /memory/{actor_id}**: Retrieves `MemoryAgentActor`’s memory.

### 4. Understand the Code
Review the `main.py` code:
- **Pydantic Model**: `Message` defines structured messages with `role` and `content`.
- **ChatAgent**: Stores conversation history, delegates to `ResponseAgent` via `ActorProxy`, and publishes events.
- **ResponseAgent**: Generates timestamped responses with memory context from `MemoryAgentActor`, tracks message count.
- **MemoryAgentActor**: Updates memory (recent messages, max 3) via pub/sub, provides memory for `ResponseAgent`.
- **FastAPI Endpoints**: Trigger `ChatAgent`, retrieve history, count, and memory, handle pub/sub events.
- **Pub/Sub**: Publishes events synchronously (note: `DaprClient.publish_event` is synchronous, which may block the event loop; monitor performance).

The system flows as follows: a POST to `/chat/user1` triggers `ChatAgent` to store the user message, invoke `ResponseAgent` (which queries `MemoryAgentActor`), store the response, and publish an event. The `/subscribe` endpoint triggers `MemoryAgentActor` to update memory, which `ResponseAgent` uses for context.

### 5. Observe the Dapr Dashboard
Open the Dapr dashboard to monitor actor instances:
```bash
dapr dashboard
```
Navigate to the **Actors** tab. Expect to see `ChatAgent`, `ResponseAgent`, and `MemoryAgentActor`, each with a count of active instances (e.g., `2` for `user1` and `user2`). If counts are higher (e.g., `3`), see **Troubleshooting**.

## Validation

Verify the multi-agent system works as expected:
1. **Message Processing**: POST to `/chat/{actor_id}` returns a timestamped response with memory context from `ResponseAgent`.
2. **Delegation**: Check logs (`dapr logs -a multi-actor`) for `ChatAgent` delegating to `ResponseAgent` and `ResponseAgent` querying `MemoryAgentActor` (e.g., `Processed message for history-user1`, `ResponseAgent processed message`, `Updated memory for memory-user1`).
3. **History Retrieval**: GET `/chat/{actor_id}/history` returns the correct history, with up to 5 entries.
4. **Message Count**: GET `/response/{actor_id}/count` returns the number of messages processed by `ResponseAgent`.
5. **Memory Retrieval**: GET `/memory/{actor_id}` returns the memory store (up to 3 entries) from `MemoryAgentActor`.
6. **Event Publishing**: Check logs for `Published event for history-user1` and `Received event: User user1 sent ...`.
7. **Dashboard Count**: Confirm the dashboard shows expected instances (e.g., `2` for each actor type).


## Key Takeaways
- **Dynamic Actor Creation**: Spawning `ResponseAgent` and `MemoryAgentActor` enables task-specific sub-agents, a core AI pattern.
- **Actor Proxies**: `ActorProxy` simplifies asynchronous actor-to-actor communication, supporting scalability.
- **Fault Isolation**: Independent state and execution ensure resilience, aligning with DACA’s robustness goals.
- **Pub/Sub and Memory**: Event-driven memory updates via `MemoryAgentActor` enhance context awareness.
- **Multi-Agent System**: Collaboration between `ChatAgent`, `ResponseAgent`, and `MemoryAgentActor` models complex AI workflows.

## Challenge: 

Here we have mocked the ai workflow. As a challenge project you will integrate openai agents sdk as agentic engine in this code. Do it yourself and if you are stuck here's an [implementation of the challenge](https://github.com/mjunaidca/vagent_comm)

## Next Steps
- Proceed to **Step 4: advanced_agents** to integrate an LLM (e.g., Gemini) into `ResponseAgent` for dynamic responses, using memory and history in a system prompt.
- Experiment with additional actors (e.g., a `SentimentAgent` to analyze message tone).
- Create a subscriber service to process `user-chat` events (e.g., log to a database).
- Explore running `DaprClient.publish_event` in a separate thread using `asyncio.to_thread` to mitigate blocking.
- Inspect Redis state with `redis-cli` (e.g., `GET history-user1`, `GET memory-user1`).

## Resources
- [Dapr Actors Overview](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/)
- [Dapr Pub/Sub Overview](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-overview/)
- [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [Dapr Python SDK Pub/Sub](https://docs.dapr.io/developing-applications/sdks/python/python-pubsub/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/04_security_fundamentals/00_lab_starter_code)