# Step 4.1: [Reminders](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-timers-reminders/)

This is the first sub-step of **Step 4: Timers and Reminders** in the **Dapr Agentic Cloud Ascent (DACA)** learning path. In this sub-step, you’ll enhance the `ChatAgent` actor from **Step 2** by adding a Dapr actor reminder to clear the conversation history after a set period (10 minutes). This introduces durable scheduling for periodic tasks, ensuring the actor can perform maintenance tasks even after deactivation, aligning with DACA’s goal of reliable, stateful AI agents.

## Overview

The **reminders** sub-step modifies the `ChatAgent` to:
- Register a reminder named `clear_history` during actor activation.
- Implement a `clear_history` method to reset the conversation history in Redis.
- Trigger the reminder after 10 minutes, clearing the history for the actor’s `ActorId`.
- Maintain the existing `process_message` and `get_conversation_history` functionality from **Step 2**.

Reminders are durable, meaning they persist across actor deactivations and reactivations, making them ideal for scheduled tasks like history cleanup in conversational AI agents.

### Learning Objectives
- Configure and register a Dapr actor reminder.
- Implement a method to handle reminder triggers.
- Understand durable scheduling for periodic tasks.
- Validate state reset after a reminder fires.

### Ties to Step 4 Overview
- **Reminders**: This sub-step implements a durable reminder to clear conversation history, ensuring state management reliability.
- **Dapr’s Implementation**: Leverages Dapr’s actor reminder feature for scheduling.
- **Fault Tolerance**: Ensures the reminder persists even if the actor is deactivated.

## Key Concepts

### Dapr Actor Reminders
Dapr actor reminders are durable, periodic tasks associated with an actor instance. They:
- Persist in the state store (Redis) and survive actor deactivation.
- Trigger a specified method (e.g., `clear_history`) at defined intervals.
- Are configured with a `dueTime` (initial delay) and `period` (repeat interval).

In this sub-step, the `ChatAgent` registers a `clear_history` reminder with a 10-second `dueTime` and no repeat (`period=0`), clearing the history once.

### Lightweight Configuration
The reminder is added with minimal changes to the **Step 2** code:
- A new `clear_history` method to reset the history.
- Reminder registration in `_on_activate` using `self._timer_manager`.
- No additional dependencies or complex logic, keeping the configuration lightweight.

### Interaction Patterns
The `ChatAgent` continues to support:
- **Request/Response**: FastAPI endpoints (`/chat/{actor_id}`, `/chat/{actor_id}/history`) for message processing and history retrieval.
- **Event-Driven**: Pub/sub events via `/subscribe` for `ConversationUpdated`.
- **Scheduled Task**: The `clear_history` reminder triggers automatically after 10 seconds, resetting the history.

## Hands-On Dapr Virtual Actor

### 0. Setup Code
Use the [02_chat_actor](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/02_chat_actor) from **Step 2**. Ensure **Step 2** is complete.

Verify dependencies:
```bash
uv add dapr dapr-ext-fastapi
```

Start the application:
```bash
tilt up
```

### 1. Configure Dapr Components
The **Step 2** components (`statestore.yaml`, `daca-pubsub.yaml`, `message-subscription.yaml`) are sufficient. Verify their presence in `components/` and ensure statestore have:

**File**: `components/statestore.yaml`
```yaml
spec:
    ...
  - name: actorStateStore
    value: "true"
```

### 2. Implement the ChatAgent with Reminders
Update the **Step 2** `main.py` to add a reminder to the `ChatAgent`. The reminder clears the conversation history after 1 minute.

**File**: `main.py`
```python
from collections.abc import Awaitable
from datetime import timedelta
import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, Remindable, actormethod
from dapr.clients import DaprClient
from typing import Callable, Dict, Optional

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
        self._reminder_handlers: Dict[str, Callable[[bytes], Awaitable[None]]] = {
            "ClearHistory": self.clear_history
        }

    async def _on_activate(self) -> None:
        """Initialize state and register reminder on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            history = await self._state_manager.get_state(self._history_key)
            if history is None:
                logging.info(f"State not found for {self._history_key}, initializing")
                await self._state_manager.set_state(self._history_key, [])
            else:
                logging.info(f"State found for {self._history_key}: {history}")

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
```

### 3. Test the App
Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to test endpoints interactively.

Test the **Actor** route group:
- **GET /healthz**: Verifies Dapr actor configuration (`200 OK` indicates health).
- **GET /dapr/config**: Confirms `ChatAgent` is registered.

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message and receives a response.
- **GET /chat/{actor_id}/history**: Retrieves the conversation history.
- **POST /subscribe**: Handles `user-chat` topic events.

Use `curl` commands to test:
```bash
curl -X POST http://localhost:8000/chat/user1 -H "Content-Type: application/json" -d '{"role": "user", "content": "Hi there"}'
curl http://localhost:8000/chat/user1/history
# Wait 10 seconds (or modify due_time to 30s for testing)
curl http://localhost:8000/chat/user1/history
```

**Expected Output**:
- First POST: `{"response": {"role": "assistant", "content": "Got your message: Hi there"}}`
- First GET: `{"history": [{"role": "user", "content": "Hi there"}, {"role": "assistant", "content": "Got your message: Hi there"}]}`
- GET after 10 seconds: `{"history": []}`

### 4. Understand the Code
Review the changes in `main.py`:
- **Actor Interface**: Added `ClearHistory` method to `ChatAgentInterface`.
- **Reminder Registration**: In `_on_activate`, `register_reminder` schedules `clear_history` to fire after 1 seconds.
- **Clear History Method**: `clear_history` resets the history to an empty list in Redis.
- **Existing Functionality**: Preserves `process_message`, `get_conversation_history`, and pub/sub from **Step 2**.

The reminder triggers `clear_history` automatically, resetting the history even if the actor is deactivated, demonstrating durable scheduling.

### 5. Observe the Dapr Dashboard
Run:
```bash
dapr dashboard
```
Check the **Actors** tab for `ChatAgent` instances (e.g., `1` for `user1`). Verify logs for `Clearing history for history-user1` after 10 seconds.

## Validation
Verify the reminder functionality:
1. **Message Processing**: POST to `/chat/user1` adds messages to the history.
2. **History Retrieval**: GET `/chat/user1/history` shows the history with up to 5 entries.
3. **Reminder Trigger**: Wait 10 seconds (or set `due_time="30s"` for testing) and confirm GET `/chat/user1/history` returns `[]`.

## Key Takeaways
- **Durable Reminders**: Reminders persist across actor deactivations, ideal for scheduled tasks like history cleanup.
- **Lightweight Configuration**: Minimal changes (new method, reminder registration) add powerful functionality.
- **State Management**: Reminders interact with the state store, ensuring reliable history reset.
- **DACA Alignment**: Supports fault tolerance by maintaining scheduled tasks in a distributed system.

## Next Steps
- Proceed to **Step 4.2: Timers** to add a timer for periodic logging.
- Experiment with different `due_time` values (e.g., `5m`) or repeating reminders (`period="1h"`).
- Explore reminder TTL for expiring reminders after a set time.

## Resources
- [Dapr Actor Reminders](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/#reminders)
- [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code)