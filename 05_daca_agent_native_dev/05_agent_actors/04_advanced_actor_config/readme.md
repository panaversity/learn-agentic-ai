# Step 4: Advanced Actor Configurations

Welcome to **Step 4** of the **Dapr Agentic Cloud Ascent (DACA)** learning path, located in the `05_agent_actors/04_advanced_actor_config/` directory. In this step, you will enhance the `ChatAgent` actor from **Step 2** by exploring advanced Dapr Virtual Actor features. Through seven sub-steps, you’ll learn how to schedule tasks, handle concurrent messages, ensure reliability, scale across distributed systems, isolate deployments, and optimize resources, all to build robust and efficient conversational AI agents.

## What You’ll Learn

This step focuses on advanced configurations for Dapr Virtual Actors to make the `ChatAgent` production-ready. You’ll discover how to:
- Schedule automated tasks using timers and reminders.
- Process multiple messages concurrently with reentrancy.
- Handle errors reliably with fault tolerance.
- Scale the `ChatAgent` across multiple nodes using partitioning.
- Isolate deployments for different environments using namespacing.
- Optimize resource usage by deactivating idle actors.

These skills align with DACA’s goal of creating scalable, reliable, and efficient AI agents that can handle real-world conversational workloads.

## Why It Matters

In production, AI agents need to manage tasks automatically, handle errors gracefully, scale to support many users, and use resources efficiently. By applying these advanced Dapr features, you’ll transform the `ChatAgent` into a powerful, distributed system capable of:
- **Reliability**: Recovering from failures like state store issues.
- **Scalability**: Supporting thousands of users across multiple servers.
- **Efficiency**: Reducing resource usage by deactivating idle instances.
- **Flexibility**: Operating in isolated environments for different use cases.

These capabilities are essential for building agentic AI systems that are robust and cost-effective.

## Sub-Steps Overview

This step is divided into four sub-steps, each focusing on a specific Dapr Virtual Actor feature. Each sub-step has its own directory (e.g., `01_actor_timers/`) with a detailed `README.md` to guide you through the implementation and validation.

1. **Actor Timers** (`01_actor_timers`):
   - Learn to use timers to schedule temporary tasks, such as logging the number of messages every few seconds.
   - Objective: Understand lightweight, in-memory scheduling for real-time monitoring.
   - Why It Matters: Timers help you track agent activity without persistent storage.

2. **Actor Reminders** (`02_actor_reminders`):
   - Set up durable reminders to perform tasks like clearing conversation history after a period of inactivity.
   - Objective: Master persistent scheduling that survives actor deactivation.
   - Why It Matters: Reminders ensure long-term state management for user interactions.

3. **Actor Reentrancy** (`03_actor_reentrancy`):
   - Enable reentrancy to process multiple messages concurrently, such as handling follow-up responses.
   - Objective: Explore concurrent message handling for complex conversation flows.
   - Why It Matters: Reentrancy supports dynamic, multi-step interactions with users.

4. **Actor runtime configuration** (`04_runtime_config`):
   - Modify the default Dapr actor runtime configuration behavior.

## What You Need to Do

To complete **Step 4**, follow these steps:

1. **Set Up Prerequisites**:
   - Ensure **Step 2** (`ChatAgent`) is complete, with the starter code from [00_lab_starter_code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code).
   - Set up a Kubernetes cluster (e.g., `minikube`) and install dependencies (`dapr`, `dapr-ext-fastapi`, `pydantic`) using:
     ```bash
     uv add dapr dapr-ext-fastapi pydantic
     ```
   - Start the application with:
     ```bash
     tilt up
     ```

2. **Work Through Sub-Steps**:
   - Navigate to each sub-step directory (`01_actor_timers/`)
   - Read the `README.md` in each directory for detailed instructions on:
     - Modifying the `ChatAgent` code (`main.py`) or adding Dapr components (`components/`).
     - Testing the feature using FastAPI endpoints (`/chat/{actor_id}`, `/chat/{actor_id}/history`) or logs.
     - Validating the feature with tools like Dapr dashboard, Redis, or Kubernetes.

3. **Test and Validate**:
   - Use the FastAPI API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to test endpoints.
   - Monitor the Dapr dashboard (`dapr dashboard`) to observe actor instances and behavior.
   - Check Redis (`redis-cli`) and logs (`dapr logs -a chat-agent`) to verify state and feature functionality.

4. **Explore and Experiment**:
   - Combine features (e.g., use timers with partitioning) to see how they interact.
   - Adjust configurations (e.g., change timer intervals, deactivation timeouts) to test different scenarios.

## Getting Started

Start with the first sub-step, `01_actor_timers/`, and work through each sub-step in order. Each sub-step builds on the **Step 2** `ChatAgent`, adding one new feature at a time. Refer to the sub-step READMEs for specific tasks, such as updating code, configuring Dapr components, or running validation tests.

## Key Takeaways
- **Advanced Features**: Timers, reminders, reentrancy, and deactivation policies enhance the `ChatAgent`’s scheduling and resource management.
- **Reliability**: Fault tolerance ensures the agent remains operational during failures.
- **Scalability**: Partitioning and namespacing support large-scale, multi-tenant deployments.
- **DACA Goals**: These features make the `ChatAgent` robust, scalable, and efficient, ready for real-world AI applications.

## Next Steps
- Experiment with real-world scenarios, such as integrating an AI model (e.g., xAI’s Grok via [https://x.ai/api](https://x.ai/api)).
- Explore how these features can be combined for more complex agent behaviors.

## Resources
- [Dapr Virtual Actors Overview](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/)
- [Dapr Python SDK for Actors](https://docs.dapr.io/developing-applications/sdks/python/python-actor/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code)