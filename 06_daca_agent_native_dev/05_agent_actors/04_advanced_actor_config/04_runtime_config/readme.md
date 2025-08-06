# Step 4.4: [Actor Runtime Configuration Parameters](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-runtime-config/)

This is the fourth and final sub-step of **Step 4: Advanced Actor Config** in the **Dapr Agentic Cloud Ascent (DACA)** learning path. Building on **Step 4.3** where you enabled **Reentrancy**, this sub-step explores how to customize various other **Dapr Actor runtime configuration parameters** for the `ChatAgent` application. You'll learn how to fine-tune actor behavior related to lifecycle management (like idle timeouts), scanning intervals, and behavior during node changes, optimizing actors for specific needs.

## Overview

The **actor runtime configuration** sub-step demonstrates how to modify the default settings governing Dapr's actor system beyond just reentrancy. You will:

  - Learn about key configuration parameters like `actorIdleTimeout`, `actorScanInterval`, `drainOngoingCallTimeout`, and `drainRebalancedActors`.
  - Apply these settings to the `ChatAgent` application (which already has reentrancy enabled from Step 4.3 but no timers) using the Python SDK's `ActorRuntimeConfig`.
  - Understand the impact of these settings on actor performance, resource usage, and behavior during scaling or updates.
  - Preserve the core functionality from **Step 2** (message processing, history retrieval, pub/sub) and the reentrancy setting from **Step 4.3**.

By adjusting these parameters, you gain finer control over how Dapr manages your actor instances, which is crucial for optimizing resource utilization and behavior in production environments, aligning with DACA's goals for scalable and robust AI agents.

### Learning Objectives

  - Identify key Dapr actor runtime configuration parameters and their default values.
  - Understand the purpose of parameters like `actorIdleTimeout`, `actorScanInterval`, and `drainOngoingCallTimeout`.
  - Configure these parameters in a Python Dapr application using `ActorRuntimeConfig`.
  - Verify the applied configuration using Dapr's configuration endpoint.
  - Understand how these settings influence actor lifecycle management and resource consumption.

### Ties to Step 4 Overview

  - **Advanced Configuration**: Directly implements advanced tuning of the actor runtime.
  - **Dapr’s Implementation**: Uses Dapr's built-in configuration mechanisms for the actor subsystem.
  - **Scalability & Optimization**: Parameters like idle timeout and scan interval directly impact resource usage and scalability.

## Key Concepts

### Dapr Actor Runtime Parameters

Dapr allows customization of its actor runtime behavior through several parameters, configured application-wide via `ActorRuntimeConfig` in Python. Key parameters include:

  * **`actor_idle_timeout`**: Specifies how long an actor instance can remain idle (unused) before the Dapr runtime deactivates it to free up resources.
      * *Default*: 60 minutes.
      * *Effect*: Shorter timeouts free up memory faster but might cause more frequent actor reactivation overhead if the actor is needed again soon. Longer timeouts keep actors in memory longer, potentially improving latency for subsequent calls but consuming more resources.
  * **`actor_scan_interval`**: Defines how frequently the Dapr runtime scans for actor instances that have exceeded their `actor_idle_timeout`.
      * *Default*: 30 seconds.
      * *Effect*: More frequent scanning ensures actors are deactivated closer to their idle timeout, but adds minor overhead. Less frequent scanning reduces overhead but means actors might stay idle longer than the timeout before being collected.
  * **`drain_ongoing_call_timeout`**: During actor rebalancing (e.g., due to scaling or host restarts), this sets the maximum time Dapr will wait for an currently executing actor method to complete before forcefully deactivating the actor instance on the old host.
      * *Default*: 60 seconds.
      * *Effect*: Allows graceful completion of ongoing work during rebalancing. Setting it too low might interrupt long-running tasks.
  * **`drain_rebalanced_actors`**: A boolean flag indicating whether the draining behavior (waiting for `drain_ongoing_call_timeout`) should be enabled during rebalancing.
      * *Default*: `True`.
      * *Effect*: Setting to `False` causes immediate deactivation during rebalancing, potentially interrupting ongoing calls.
  * **`reentrancy`**: (Configured in Step 4.3) An `ActorReentrancyConfig` object to enable/disable reentrancy and set `maxStackDepth`.
      * *Default*: Disabled (`enabled=False`). Set to `enabled=True` in Step 4.3.
  * **`remindersStoragePartitions`**: Configures partitioning for actor reminders. *Not relevant for this specific code version as it doesn't use reminders.*
      * *Default*: 0.
  * **`entities`**: (Implicitly handled by `register_actor` in Python SDK) Lists the actor types hosted by this application service.
  * **`entitiesConfig`**: Allows specifying configuration overrides (like different timeouts) on a per-actor-type basis.

### Configuration Mechanism

These settings are applied using `ActorRuntime.set_actor_config()` typically near application startup, before actors are registered. The Dapr sidecar retrieves this configuration from the application via the `GET /dapr/config` endpoint.

## Hands-On Dapr Virtual Actor

### 1. Setup Code

Use the code from **Step 4.3: Reentrancy** The `main.py` file from that step (with reentrancy enabled, and 1 reminder) is the starting point.

Verify dependencies (no new dependencies needed):

Start the application:

```bash
tilt up
```

### 2\. Implement Extended Runtime Configuration

Update the `main.py` from **Step 4.3 (timer-less version)** to modify the `ActorRuntimeConfig` instantiation, setting values for several parameters besides reentrancy.

**File**: `main.py` (Modify the timer-less version from Step 4.3)

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
```

### 3\. Test the App

The primary validation method is checking the Dapr configuration endpoint.

1.  **Call the Dapr Config Endpoint**:

2.  **Expected Output**: Verify the JSON response reflects the new settings applied in `ActorRuntimeConfig`. Check the values for `actorIdleTimeout`, `actorScanInterval`, `drainOngoingCallTimeout`, `drainRebalancedActors`, `reentrancy`, and `remindersStoragePartitions`. Timeouts should reflect the `timedelta` values (e.g., "10m", "15s", "1m30s", or similar ISO 8601 duration format).

    ```json
        {
        "actorIdleTimeout": "0h0m20s0ms0μs",
        "actorScanInterval": "0h0m15s0ms0μs",
        "drainOngoingCallTimeout": "0h1m30s0ms0μs",
        "drainRebalancedActors": true,
        "reentrancy": {
            "enabled": true,
            "maxStackDepth": 32
        },
        "remindersStoragePartitions": 1,
        "entitiesConfig": [],
        "entities": [
            "ChatAgent"
        ]
        }
    ```

4.  **Verify Existing Functionality**: Ensure all endpoints (`/chat/{id}`, `/chat/{id}/history`) and the pub/sub subscription mechanism function correctly.

### 4\. Understand the Code

Review the updated `main.py`:

  - **`ActorRuntimeConfig` Update**: The key change is adding parameters (`actor_idle_timeout`, `actor_scan_interval`, `drain_ongoing_call_timeout`, `remindersStoragePartitions`) alongside the existing `reentrancy` setting in the `ActorRuntimeConfig` instantiation. `timedelta` is used for duration settings.
  - **Removed Timer Logic**: All code related to Dapr Timers (interface method, handler method, registration in `_on_activate`) has been removed as per the requirement to base this step on a timer-less version.
  - **Configuration Timing**: The configuration is applied via `ActorRuntime.set_actor_config()` *before* actors are registered, ensuring Dapr uses these settings from the start.
  - **Impact**: These settings alter how Dapr manages actor lifecycles and resources globally for this application. For example, the `ChatAgent` actors will now be eligible for deactivation after 10 minutes of inactivity instead of the default 60.

## Validation

Confirm the following:

1.  **Runtime Configuration Updated**: The `GET /dapr/config` endpoint shows the newly configured values for `actorIdleTimeout`, `actorScanInterval`, `drainOngoingCallTimeout`, `remindersStoragePartitions`, and confirms `reentrancy` is still enabled.
2.  **Existing Functionality**: Chat message processing, history retrieval, and pub/sub subscriptions all function correctly.
3.  **No Timer Logs**: Verify that no timer-related log messages (`->[TIMER]...`) appear in the application logs.
4.  **(Optional Observation)**: If you leave an actor idle for more than 10 minutes (the new `actorIdleTimeout`) and monitor the Dapr dashboard or logs, you might observe the actor instance being deactivated.

## Key Takeaways

  - **Fine-grained Control**: Dapr provides parameters to precisely control actor lifecycle (idle timeout, scanning) and behavior during updates (draining).
  - **Configuration via SDK**: These settings are easily applied in Python using `ActorRuntimeConfig` and `timedelta`.
  - **Optimization**: Tuning these parameters allows optimizing actor resource consumption and behavior based on application requirements.
  - **Verification**: The `/dapr/config` endpoint is essential for verifying that runtime settings have been applied correctly.

## Next Steps / Conclusion of Step 4

This concludes Step 4: Advanced Actor Config. You have explored various ways to configure actor behavior beyond the basics:

  - **4.1 Reminders** (If covered previously)
  - **4.2 Timers** (If covered previously, now removed in this track)
  - **4.3 Reentrancy** (Enabled)
  - **4.4 Runtime Configuration** (Idle timeout, scan interval, draining, etc.)

**Further Exploration:**

  - Experiment with different values for the runtime parameters and observe their effects on resource usage and actor activation/deactivation times using the Dapr dashboard and logs.
  - Investigate `entitiesConfig` for applying different settings to different actor types if your service hosts multiple types.

## Resources

  - [Dapr Docs: Actor runtime configuration parameters](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-runtime-config/)
  - [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
  - [Python `datetime.timedelta`](https://www.google.com/search?q=%5Bhttps://docs.python.org/3/library/datetime.html%23timedelta-objects%5D\(https://docs.python.org/3/library/datetime.html%23timedelta-objects\))