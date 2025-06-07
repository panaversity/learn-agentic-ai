# Dapr Actor Fundamentals

This is the first step of building **AI Agents as Dapr Virtual Actors** in the **Dapr Agentic Cloud Ascent (DACA)** design pattern, as part of the [AI Agents as Virtual Actors learning path](#). In this step, you’ll create and invoke a simple Dapr Virtual Actor, the `HelloAgent`, to understand the fundamentals of the Actor Model, Dapr’s actor implementation, and state persistence. This is your "Hello World" for Dapr Actors, setting the foundation for scalable, stateful AI agents.

## Overview

The **hello_actors** step introduces Dapr Virtual Actors, lightweight, stateful entities based on the Actor Model (Hewitt, 1973), ideal for modeling AI agents in DACA. You’ll implement a `HelloAgent` actor that:
- Accepts a greeting message (e.g., `{"message": "Hello, World!"`) via an `AddGreeting` method.
- Stores the message in a user-specific history list, limited to the last 5 entries.
- Retrieves the history via a `GetGreetingHistory` method.

The actor uses a Dapr-managed state store (e.g., Redis) for persistence and is integrated with FastAPI using the `DaprActor` extension. Each unique `actor_id` (e.g., `sir_zia`) creates a separate `HelloAgent` instance, storing its own greeting history, enabling per-user state management. This aligns with DACA’s goal of building concurrent, scalable systems and prepares you for more complex agent implementations.

### Learning Objectives
- Understand the Actor Model and its role in concurrent, distributed systems.
- Create a Dapr Virtual Actor using Python, FastAPI, and the `DaprActor` extension.
- Persist user-specific state in a Dapr state store with robust initialization.
- Invoke the actor via FastAPI endpoints and interpret Dapr dashboard metrics.

#### Ties to DACA Agent Actors Modules
- **Actors as the Fundamental Unit**: The `HelloAgent` encapsulates state (greeting history) and behavior (adding/retrieving greetings).
- **State Persistence**: Dapr persists actor state in Redis, ensuring durability across activations.
- **Dapr’s Implementation of the Actor Model**: Virtual Actors are activated on-demand, optimizing resources.

## Hands On Dapr Virtual Actor

### 0. Setup Code

We will take the 00_lab_starter_code as the base code. It is the same starter code we had in 04_security fundamentals. So it's best to complete dapr intro before starting this module. 

Setup Environment and install package in lab starter code:

```bash
uv add dapr-ext-fastapi
```

Start 
```bash
tilt up
```

### 1. Update the Dapr State Store Configuration
Configure Redis as the state store for actor state persistence. Update components/statestore.yaml:

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

### 2. Implement the HelloAgent Actor
Create a Python application with a `HelloAgent` actor that:
- Accepts a greeting message (e.g., {"message": "Hello!"}) via an AddGreeting method.
- Stores the message in a user-specific history list, limited to the last 5 entries.
- Retrieves the history via a GetGreetingHistory method.

**File**: `main.py`
```python
import logging
from fastapi import FastAPI
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="HelloAgentService", description="DACA Step 1: Dapr Actor Fundamentals")

# Add Dapr Actor Extension
actor = DaprActor(app)

# Define the actor interface
class HelloAgentInterface(ActorInterface):
    @actormethod(name="AddGreeting")
    async def add_greeting(self, greeting_data: dict) -> None:
        pass

    @actormethod(name="GetGreetingHistory")
    async def get_greeting_history(self) -> list[dict] | None:
        pass

# Implement the actor
class HelloAgent(Actor, HelloAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"

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

    async def add_greeting(self, greeting_data: dict) -> None:
        """Add a greeting to history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            current_history.append(greeting_data)
            if len(current_history) > 5:  # Limit to last 5 greetings
                current_history = current_history[-5:]
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Added greeting for {self._history_key}: {greeting_data}")
        except Exception as e:
            logging.error(f"Error adding greeting: {e}")
            raise

    async def get_greeting_history(self) -> list[dict] | None:
        """Retrieve greeting history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history: {e}")
            return []

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(HelloAgent)
    logging.info(f"Registered actor: {HelloAgent.__name__}")

# FastAPI endpoints to invoke the actor
@app.post("/greet/{actor_id}")
async def add_greeting(actor_id: str, greeting: dict):
    """Add a greeting to the actor's history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    await proxy.AddGreeting(greeting)
    return {"status": "Greeting added"}

@app.get("/greet/{actor_id}/history")
async def get_greeting_history(actor_id: str):
    """Retrieve the actor's greeting history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    history = await proxy.GetGreetingHistory()
    return {"history": history}
```

### 3. Test the App
Open the docs at http://localhost:8000/docs

Try the different endpoints:

In Actor route group
- GET /healthz tells our dapr actors config is setup correctly
- GET /dapr/config shows the registered actor names
  Output:
  ```bash
  {
    "actorIdleTimeout": "1h0m0s0ms0μs",
    "actorScanInterval": "0h0m30s0ms0μs",
    "drainOngoingCallTimeout": "0h1m0s0ms0μs",
    "drainRebalancedActors": true,
    "entitiesConfig": [],
    "entities": [
      "HelloAgent"
    ]
  }
  ```

In default route group try:
- POST: /greet/{actor_id}
- GET: /greet/{actor_id}

Send HTTP requests to invoke the `HelloAgent` and verify its behavior. Use swagger or curl

```bash
curl -X POST http://localhost:8000/greet/sir_zia -H "Content-Type: application/json" -d '{"message": "Hello, World!"}'
curl http://localhost:8000/greet/sir_zia/history
curl -X POST http://localhost:8000/greet/sir_zia -H "Content-Type: application/json" -d '{"message": "Hi again!"}'
curl http://localhost:8000/greet/sir_zia/history
```


### 4. Understand the Code
Review the `main.py` code below, which implements the `HelloAgent` actor and FastAPI endpoints:
- **Actor Interface**: Defines `AddGreeting` and `GetGreetingHistory` methods with `@actormethod`.
- **Actor Implementation**: Manages greeting history with state persistence and logging.
- **FastAPI Endpoints**: Invokes the actor using `ActorProxy` with the registered method names (`AddGreeting`, `GetGreetingHistory`).

The actor processes messages asynchronously, where a POST to /greet/sir_zia sends a message to the sir_zia actor’s mailbox, triggering the add_greeting method to update its history.


### 5. Observe the Dapr Dashboard
Open the Dapr dashboard to monitor actor instances:
```bash
dapr dashboard
```
- Navigate to the **Actors** tab.

Optionally connect to redis and see the data saved there
```bash
kubectl run redis-client --namespace default --restart='Never' --image docker.io/bitnami/redis:7.4.2-debian-12-r11 --command -- sleep infinity
kubectl get pods
kubectl exec -it redis-client --namespace default -- redis-cli -h redis-master
```

```bash
redis-master:6379> KEYS *
redis-master:6379> HGETALL "daca-ai-app||HelloAgent||sir_zia||history-sir_zia"
```

### Key Concepts: What have we done?

Actor Model

The Actor Model, introduced by Carl Hewitt, Peter Bishop, and Richard Steiger in 1973, is a framework for concurrent and distributed computation. Actors are independent entities with:

- State: Private data, such as the HelloAgent’s greeting history stored in Redis.
- Behavior: Logic to process messages, like adding or retrieving greetings.
- Mailbox: A queue for receiving asynchronous messages, processed one at a time.

For example, when you send a POST to /greet/sir_zia with {"message": "Hello!"}, the message enters the sir_zia actor’s mailbox, triggering add_greeting to append the greeting to its history. This ensures concurrency without shared state, as sir_zia and other actors operate independently.

#### Dapr Virtual Actors

**Dapr (Distributed Application Runtime)** implements the Actor Model through **Virtual Actors**, which are designed for cloud-native, distributed systems. Key features include:
- **Virtual Lifecycle**: Actors are activated when a message is received (e.g., a POST to `/greet/junaid`) and deactivated after an idle period to save resources.
- **State Persistence**: Dapr stores state in Redis, ensuring durability. The HelloAgent uses keys like history-sir_zia for its history.
- **Single-Threaded Concurrency**: Each actor processes one message at a time, simplifying concurrency management. Dapr distributes actors across a cluster for scalability.
- **Per-User Instances**: Each unique ActorId (e.g., sir_zia, ahmad) creates a separate HelloAgent instance, each with its own state.

### Actor Instances and the Dapr Dashboard
When you call `/greet/junaid` and `/greet/ahmad`, Dapr creates a `HelloAgent` instance for each unique `ActorId`: The Dapr dashboard (`dapr dashboard`) shows the total number of active actor instances for each actor type. 


To verify, check the Dapr logs (`dapr logs -a hello-actor`) for activation messages (e.g., `Activating actor for history-junaid`) to identify all `ActorId`s. You can also use `redis-cli` to list keys (e.g., `KEYS history-*`) to see all active history keys.

### State Management in Dapr Actors

Dapr persists actor state in a state store (Redis in this case), using a unique key per actor instance (e.g., `history-junaid` for `ActorId("junaid")`). The `HelloAgent` manages state as follows:
- **Initialization**: The `_on_activate` method runs when the actor is activated, checking if the state exists in Redis. If not, it initializes an empty list (`[]`), ensuring robustness even if Redis is temporarily unavailable.
- **Adding Greetings**: The `add_greeting` method appends a greeting to the history list, limits it to 5 entries, and saves it to Redis.
- **Retrieving History**: The `get_greeting_history` method fetches the history from Redis, returning an empty list if no state exists.

This approach ensures that each user’s greetings are stored persistently and independently, supporting DACA’s goal of scalable, user-specific AI agents.

### Key Takeaways
- **Actor Model**: Actors like `HelloAgent` encapsulate state (greeting count) and behavior (greeting logic).
- **Dapr Virtual Actors**: Dapr manages actor lifecycle, making them lightweight and scalable.
- **State Management**: Dapr persists state in Redis, ensuring durability.
- **FastAPI Integration**: Actors are easily invoked via REST APIs, aligning with DACA’s polyglot approach.

## Next Steps
- Proceed to **Step 2: chat_actor** to build a chat agent with conversation history and pub/sub integration.
- Experiment with additional greeting data (e.g., `{"message": "Hello", "timestamp": "2025-05-05T12:00:00Z"}`) in `HelloAgent`.
- Use the Dapr dashboard to monitor actor instances and state changes in real-time.
- Connect with redis cli like we did in module 2 and see what is persisted there.

## Resources
- [Dapr Actors Overview](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/)
- [Dapr Python SDK Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [Dapr Python SDK Example](https://github.com/dapr/python-sdk/tree/master/examples/actor)
- [Actor Model Patterns](https://www.geeksforgeeks.org/design-patterns-for-building-actor-based-systems/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Panaversity Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/04_security_fundamentals/00_lab_starter_code)
