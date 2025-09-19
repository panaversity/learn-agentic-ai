# Step 4.2: [Timers](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-timers-reminders/)

This is the second sub-step of **Step 4: Advanced Actor Confif** in the **Dapr Agentic Cloud Ascent (DACA)** learning path. In this sub-step, you’ll enhance the `ChatAgent` actor from **Step 2** by adding a Dapr actor timer to log the number of messages in the conversation history every 5 seconds for 10 invocations (50 seconds). This introduces temporary periodic tasks, demonstrating how actors can perform lightweight monitoring tasks, aligning with DACA’s goal of scalable, concurrent AI agents.

## Overview

The **timers** sub-step modifies the `ChatAgent` to:
- Register a timer named `LogMessageCount` during actor activation.
- Implement a `log_message_count` method to log the current number of messages in the Redis-backed conversation history.
- Trigger the timer every 5 seconds, stopping after 10 invocations (50 seconds).
- Preserve the `process_message`, `get_conversation_history`, and pub/sub functionality from **Step 2**.

Timers are temporary, in-memory tasks that stop when the actor is deactivated, making them suitable for short-lived monitoring tasks like logging message counts.

### Learning Objectives
- Configure and register a Dapr actor timer using `register_timer`.
- Implement a method to handle timer triggers and log state.
- Understand the lifecycle of temporary periodic tasks (stop on actor deactivation).

### Ties to Step 4 Overview
- **Timers**: Implements a timer to log message counts periodically, showcasing temporary task scheduling.
- **Dapr’s Implementation**: Leverages Dapr’s actor timer feature for lightweight monitoring.
- **Turn-Based Concurrency**: Timers run concurrently with message processing, demonstrating actor concurrency.

## Key Concepts

### Dapr Actor Timers
Dapr actor timers are temporary, periodic tasks associated with an actor instance. They:
- Run in-memory and stop when the actor is deactivated (e.g., after 1 hour of inactivity, per `actorIdleTimeout`).
- Trigger a specified method (e.g., `log_message_count`) at defined intervals.
- Are configured with a `dueTime` (initial delay) and `period` (repeat interval).

In this sub-step, the `ChatAgent` registers a `LogMessageCount` timer with a 5-second `dueTime` and `period`, logging the message count every 5 seconds.

### Lightweight Configuration
The timer is added with minimal changes to the **Step 2** code:
- A new `LogMessageCount` method in the actor interface.
- A `log_message_count` method to log the history length.
- Timer registration in `_on_activate` using `self._timer_manager`.

### Interaction Patterns
The `ChatAgent` supports:
- **Request/Response**: FastAPI endpoints (`/chat/{actor_id}`, `/chat/{actor_id}/history`) for message processing and history retrieval.
- **Event-Driven**: Pub/sub events via `/subscribe` for `ConversationUpdated` events.
- **Periodic Task**: The `LogMessageCount` timer logs message counts every 5 seconds, independent of user interactions.

## Hands-On Dapr Virtual Actor

### 1. Setup Code
Use the [02_chat_actor](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/02_chat_actor) from **Step 2**. Ensure **Step 2** is complete.

Verify dependencies in your `pyproject.toml` or `requirements.txt`:
```bash
uv add dapr dapr-ext-fastapi fastapi
```

Start the application:
```bash
tilt up
```

### 2. Implement the ChatAgent with Timers
Update the **Step 2** `main.py` to add a timer to the `ChatAgent`. The timer logs the message count every 5 seconds for 10 invocations.

**File**: `main.py`
```python
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
                callback=self._timer_handlers["LogMessageCount"],
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
```

### 3. Test the App
Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to test endpoints interactively.

Test the **Actor** route group:
- **GET /healthz**: Verifies Dapr actor configuration (`200 OK` indicates health).
- **GET /dapr/config**: Confirms `ChatAgent` is registered and actor settings (e.g., `actorIdleTimeout: 1h`).

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message and receives a response.
- **GET /chat/{actor_id}/history**: Retrieves the conversation history.

# Monitor logs for 50 seconds
**Expected Output**:
```
  daca-ai-app │ [app] 2025-05-05 21:42:12,009 - DEBUG - Logging message count for history-poi
  daca-ai-app │ [app] 2025-05-05 21:42:12,010 - DEBUG - State: None
  daca-ai-app │ [app] 2025-05-05 21:42:12,010 - INFO - 
  daca-ai-app │ [app]  ->[TIMER] Triggered for history-poi: 12 messages in history
  daca-ai-app │ [app] 2025-05-05 21:42:12,010 - DEBUG - called timer. actor: ChatAgent.poi, timer: LogMessageCount
  daca-ai-app │ [app] INFO:     127.0.0.1:51000 - "PUT /actors/ChatAgent/poi/method/timer/LogMessageCount HTTP/1.1" 200 OK
  daca-ai-app │ [app] 2025-05-05 21:42:12,014 - DEBUG - Logging message count for history-JULISA
  daca-ai-app │ [app] 2025-05-05 21:42:12,014 - DEBUG - State: None
  daca-ai-app │ [app] 2025-05-05 21:42:12,014 - INFO - 
  daca-ai-app │ [app]  ->[TIMER] Triggered for history-JULISA: 11 messages in history
  daca-ai-app │ [app] 2025-05-05 21:42:12,014 - DEBUG - called timer. actor: ChatAgent.JULISA, timer: LogMessageCount
  daca-ai-app │ [app] INFO:     127.0.0.1:51000 - "PUT /actors/ChatAgent/JULISA/method/timer/LogMessageCount HTTP/1.1" 200 OK
  daca-ai-app │ [app] 2025-05-05 21:42:13,004 - DEBUG - Logging message count for history-par
  daca-ai-app │ [app] 2025-05-05 21:42:13,005 - DEBUG - State: 
  daca-ai-app │ [app] 2025-05-05 21:42:13,006 - INFO -
```

### 4. Understand the Code
Review the changes in `main.py`:
- **Actor Interface**: Added `LogMessageCount` method to `ChatAgentInterface`.
- **Timer Registration**: In `_on_activate`, `register_timer` schedules `log_message_count` to fire every 5 seconds, starting after 5 seconds.
- **Existing Functionality**: Preserves `process_message`, `get_conversation_history`, and pub/sub from **Step 2**.
- **Error Handling**: Robust `try-except` blocks with re-raised exceptions ensure failures are logged and propagated.
- **Dynamic Handlers**: Uses `_timer_handlers` for extensibility, mapping timer names to methods.

The timer runs concurrently with message processing, logging the message count until the actor deactivates (after 1 hour of inactivity).


## Validation
Verify the timer functionality:
1. **Message Processing**: POST to `/chat/user1` adds messages to the history (2 messages per POST: user + assistant).
2. **History Retrieval**: GET `/chat/user1/history` shows up to 5 entries.
3. **Timer Logging**: Run `dapr logs -a chat-agent | grep -E "TIMER|Unregistered"` to confirm:
   - `Successfully registered LogMessageCount timer` on activation.
   - `->[TIMER] Triggered for history-user1: 4 messages in history` every 5 seconds after two POSTs (4 messages total).
   - `Unregistered LogMessageCount timer` after 50 seconds (10 invocations).

## Key Takeaways
- **Temporary Timers**: Timers enable lightweight, periodic tasks like monitoring, stopping on actor deactivation (e.g., after 1 hour of inactivity).
- **Lightweight Configuration**: Minimal changes (new method, timer registration) add monitoring functionality.
- **Turn-Based Concurrency**: Timers run alongside message processing, leveraging Dapr’s actor concurrency model.
- **DACA Alignment**: Enhances actor scalability with periodic, non-durable tasks for monitoring.

## Next Steps
- Proceed to **Step 4.3: Reentrancy** to enable concurrent message handling in the `ChatAgent`.
- Experiment with different timer intervals (e.g., `period="10s"`).
- Combine timers with reminders from **Step 4.1** to log and clear history in the same actor.
- Explore Dapr’s actor reentrancy for handling concurrent timer and message calls.

## Resources
- [Dapr Actor Timers](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/#timers)
- [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code)