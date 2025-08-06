# Step 4.3: Reentrancy

This is the third sub-step of **Step 4: Advanced Actor Config** in the **Dapr Agentic Cloud Ascent (DACA)** learning path. Following **Step 4.2: Timers**, this sub-step focuses on enabling **Dapr Actor Reentrancy** for the `ChatAgent` actor. 

Enabling reentrancy allows an actor to be called again by the same caller (or within the same call chain) before the initial method execution completes, facilitating more complex interaction patterns while preserving the actor model's turn-based concurrency for different call contexts.

## Overview

The **reentrancy** sub-step modifies the `ChatAgent` application's runtime configuration to:

  - Enable the actor reentrancy feature provided by Dapr.
  - Understand the implications of allowing reentrant calls (e.g., Actor A -\> Actor B -\> Actor A).
  - Preserve all existing functionality from **Step 4.2** (message processing, history retrieval, pub/sub, reminders).

Reentrancy is crucial for scenarios where an actor might call another service or actor that, as part of its workflow, needs to call back into the original actor within the same logical operation.

### Learning Objectives

  - Understand the concept of actor reentrancy and its use cases.
  - Configure Dapr actor runtime settings in Python to enable reentrancy.
  - Recognize how reentrancy affects actor call chains while maintaining single-threaded execution per turn for distinct contexts.
  - Verify reentrancy configuration using Dapr's configuration endpoint.

### Ties to Step 4 Overview

  - **Reentrancy**: Implements configuration for actor reentrancy.
  - **Dapr’s Implementation**: Leverages Dapr’s actor runtime configuration features.
  - **Turn-Based Concurrency**: Understands how reentrancy interacts with the single-threaded execution guarantee within a specific call context.

## Key Concepts

### Dapr Actor Reentrancy

By default, Dapr actors enforce single-threaded execution. When a method on an actor instance is invoked, Dapr places a lock on that actor instance, preventing any other calls (even from the same client or another actor) from executing until the first call completes.

Reentrancy modifies this behavior. When enabled, it allows calls that are part of the **same call chain (or context)** to "re-enter" the locked actor.

  * **Allowed by Reentrancy:**
      * Actor A calls a method on itself (`Actor A -> Actor A`).
      * Actor A calls Actor B, and Actor B subsequently calls Actor A (`Actor A -> Actor B -> Actor A`).
  * **Still Blocked:** A completely separate, independent call trying to invoke a method on Actor A while it's busy with the first call chain will still be blocked until the initial chain completes its turn.

Reentrancy enables more complex workflows and recursive patterns without deadlocking, while still protecting the actor's state from concurrent access by *different* logical operations.

### `maxStackDepth`

Dapr includes a `maxStackDepth` setting (default: 32) for reentrancy. This limits the number of reentrant calls allowed within a single call chain, preventing potential infinite recursion issues.

### Configuration via `/dapr/config`

Actor runtime settings, including reentrancy, are configured by the application and exposed via the `GET /dapr/config` endpoint, which the Dapr sidecar (daprd) calls during initialization. In Python, this is typically done using `ActorRuntimeConfig` and `ActorRuntime`.

## Hands-On Dapr Virtual Actor

### 1. Setup Code

Use the code from **Step 4.1: Reminders**. Ensure that step is complete and functional. The `main.py` file from Step 4.1 will be our starting point.

Start the application:

```bash
tilt up
```

### 2. Implement Reentrancy Configuration

Update the `main.py` from **Step 4.2** to include the actor runtime configuration for enabling reentrancy. The changes involve importing necessary configuration classes and setting the configuration *before* registering the actor.

**File**: `main.py` (Modify the version from Step 4.2)

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

# --- Step 4.3: Add Reentrancy Configuration ---
from dapr.actor.runtime.config import ActorRuntimeConfig, ActorReentrancyConfig
from dapr.actor.runtime.runtime import ActorRuntime

# Configure Reentrancy
reentrancy_config = ActorReentrancyConfig(enabled=True) # Enable reentrancy

runtime_config = ActorRuntimeConfig(
    reentrancy=reentrancy_config
    # Other configurations like actor_idle_timeout, scan_interval etc. can be added here
)
ActorRuntime.set_actor_config(runtime_config)
logging.info(f"Actor Runtime configured with Reentrancy: {reentrancy_config._enabled}")

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

```

### 3. Test the App

The primary way to verify that reentrancy is *enabled* is by checking the Dapr configuration endpoint for your application.

1.  **Find the Dapr HTTP Port:** Check the output of `dapr list` or your `tilt` logs to find the HTTP port Dapr assigned to your `chat-agent` app (e.g., `3500` or similar).

2.  **Query the Config Endpoint:** /dapr/config endpoint in docs i.e: http://localhost:8000/docs#/Actor/dapr_config_dapr_config_get.


3.  **Expected Output:** Look for the `reentrancy` section in the JSON response. It should show `enabled: true`.

    ```json
    {
    "actorIdleTimeout": "1h0m0s0ms0μs",
    "actorScanInterval": "0h0m30s0ms0μs",
    "drainOngoingCallTimeout": "0h1m0s0ms0μs",
    "drainRebalancedActors": true,
    "reentrancy": {
        "enabled": true,
        "maxStackDepth": 32
    },
    "entitiesConfig": [],
    "entities": [
        "ChatAgent"
    ]
    }
    ```

4.  **Verify Existing Functionality:** Test the endpoints from Step 4.2 to ensure they still work:

      * `POST /chat/{actor_id}`
      * `GET /chat/{actor_id}/history`
      * Check logs for reminder messages
      * Check logs for subscription messages (`->[SUBSCRIPTION] Received...`)

Enabling reentrancy should not change the behavior of these existing non-reentrant calls.

### 4. Understand the Code

Review the changes in `main.py`:

  - **Imports**: Added `ActorRuntimeConfig`, `ActorReentrancyConfig`, `ActorRuntime`.
  - **Configuration**: Created instances of `ActorReentrancyConfig` (with `enabled=True`) and `ActorRuntimeConfig`.
  - **Applying Config**: Called `ActorRuntime.set_actor_config(runtime_config)` *before* FastAPI app initialization or actor registration. This ensures the Dapr runtime is aware of the reentrancy setting when the actor type (`ChatAgent`) is registered.
  - **No Actor Logic Change**: The `ChatAgent` class itself remains unchanged because this step only *enables* the capability at the runtime level. Implementing actual reentrant calls would require modifying actor methods (e.g., having `process_message` potentially call another method on the same actor or trigger a workflow that calls back).

## Validation

Confirm the following:

1.  **Reentrancy Enabled**: The `GET /dapr/config` endpoint for your application shows `"reentrancy": {"enabled": true, ...}`.
2.  **Existing Functionality**: Message processing, history retrieval, timers, and pub/sub subscriptions all function as they did in Step 4.2.

*Note:* This step only enables reentrancy. To observe its effect, you would need to implement a scenario where reentrancy is required, such as an actor method calling itself or using a multi-actor pattern where Actor A calls Actor B, which then calls back to Actor A within the same logical transaction.

## Key Takeaways

  - **Reentrancy Configuration**: Actor reentrancy is enabled via Dapr's runtime configuration, set using the Python SDK's `ActorRuntimeConfig`.
  - **Preserves Concurrency Guarantees**: Reentrancy only applies to calls within the *same context/call chain*. Calls from different contexts remain subject to the actor's turn-based concurrency lock.
  - **Enables Complex Workflows**: Allows actors to call themselves or participate in circular call patterns (A-\>B-\>A) without deadlocking.
  - **`maxStackDepth`**: Provides protection against excessive recursion in reentrant calls.

## Next Steps

  - Explore implementing a specific reentrant call pattern within the `ChatAgent` or between multiple actors (tying into Step 3: multi\_actors if applicable). For example, modify `process_message` to call another (hypothetical) method on the same actor.
  - Consider scenarios where reentrancy might be beneficial in an AI agent context (e.g., an orchestrator actor calling worker actors which report back results to the orchestrator within the same request).
  - Review the Dapr documentation on actor timers, reminders, and reentrancy to understand how they interact.

## Resources

  - [Dapr Docs: How-to: Enable and use actor reentrancy](https://www.google.com/search?q=https://docs.dapr.io/developing-applications/building-blocks/actors/howto-reentrancy/) (As provided in the prompt)
  - [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
  - [Dapr Actor Runtime Configuration](https://www.google.com/search?q=https://docs.dapr.io/operations/configuration/configure-actors/)