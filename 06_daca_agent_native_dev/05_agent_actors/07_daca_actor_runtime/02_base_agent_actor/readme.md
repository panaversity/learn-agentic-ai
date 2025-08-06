# Implement DACA AgentCore Core Capabilities

The is self challenge for you to complete. Here we will plan an interface and implement the processing message for it.

Now let's take `01_actor_foundation` as starter code and create a fully featured `BaseActor` (DACA AgentCore) for the **DACA Actor Runtime**, plug-and-play framework for AI agents using Dapr Virtual Actors. 

The actor, temporarily called an “Ambient Agent” for this lab, supports reactive message handling, proactive task scheduling, and event-driven pub/sub integration, aligning with the Dapr Agentic Cloud Ascent (DACA) pattern.

🎯 **End Goal**: A scalable `BaseActor` that serves as the foundation for specialized agents (e.g., `ChatActor`, `MemoryActor`), addressing gaps in frameworks like LangGraph and CrewAI.

🔁 **Analogy**: The `BaseActor` is a Dapr-powered engine, always ready to process messages, schedule tasks, or react to events, much like a smart assistant waiting for your command or acting on its own schedule.

## Prerequisites

- Completed `01_actor_foundation` setup.
- Python 3.12+, Dapr CLI, Tilt, and Rancher Desktop.

## Clone and Run the Code

Clone the `01_actor_foundation` repo or continue from your existing setup:
```bash
tilt up
```

Open:
- Tilt UI: `http://localhost:1035`
- Dapr Dashboard: `http://localhost:8080`
- DACA Actor Interface: `http://localhost:30080/docs`
- Metrics Tracing Interface: `http://localhost:9090`
- Jaeger UI Interface: `http://localhost:16686`

Follow the guide below to implement `02_base_agent_actor` or use the provided code as a reference.


This `BaseActor` will serve as the superclass for more specialized actors like `ChatActor`, `MemoryActor`, `TriageAgent`, etc., within the multi-agent system, providing them with a rich set of DACA-aligned capabilities out-of-the-box.

### Step 1: Setup Foundation Code

The `01_foundation_actor` have Base Code and a Guide to implement it from scratch.

Follow the guide or just clone and run the code. At end you will have the following services

- Tilt UI: http://localhost:1035
- Dapr Dashboard: http://localhost:8080
- Ambient Actor Interface: http://localhost:30080/docs
- Metrics Tracing Interface: http://localhost:9090
- Jaegur UI Interface: http://localhost:16686/

Now in step 2, 3, 4, 5, 6 we will create the base actor - the final code is present in 02_base_actor.

### Step 2: Create Base Actor Interface

- In ambient-actor/src/actors create a new folder named `actors`.
- In actors directory create following files:
    - base_interface.py
    - base_actor.py

Now let's plan the and create BaseActorInterface (in src/ambient_actor/actors/interfaces.py)

Review src/ambient_actor/actors/interfaces.py

### Step 3: Implemet Base Actor Skeleton

This class will implement the BaseActorInterface and Dapr's Actor and Remindable classes.

Review ambient_actor/actors/base_actor.py and ambient_actor/agents

### Step 4: Add Advanced Actor Config Learnings to Base Actor

Review main.py

### Step 5: Add Bindings, PubSub and State Invocation Components

Self Challenge: Extend the Methods and implement business logic

## ✅ Learning Outcomes

By completing this step, you will:
- Refactor a Dapr project for modularity and extensibility.
- Implement a generic `BaseActor` with message handling, state management, reminders, and pub/sub.
- Integrate Dapr pub/sub for event-driven communication.
- Test actor functionality via FastAPI and Dapr APIs.
- Debug using Prometheus metrics and Jaeger traces.