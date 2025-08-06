# Dapr Intro (Hands On with Helm, Dapr State, Dapr Pub/Sub)

This tutorial introduces **Dapr** (Distributed Application Runtime), a tool that simplifies building distributed applications like microservices. It’s part of the **Dapr Agentic Cloud Ascent (DACA)** learning path, which focuses on creating scalable, resilient AI systems. We’ll use **Helm** to deploy Dapr on a Kubernetes cluster (Rancher Desktop), test its features with `curl`, explore the Dapr Dashboard, and build a FastAPI app with hot reloading for development, using Dapr’s state management and pub/sub capabilities.

### What is Dapr?
Dapr is a portable, event-driven runtime that makes it easy for developers to build resilient, stateless, and stateful applications for cloud and edge environments. It supports any programming language and abstracts complex distributed system challenges.

#### Key Features of Dapr
- **Language Agnostic**: Works with Python, Go, Java, etc., via HTTP or gRPC APIs.
- **Sidecar Architecture**: Runs as a separate container (sidecar) next to your app, ensuring isolation and portability.
- **Building Blocks**: Provides APIs for common patterns like state management, pub/sub messaging, and service invocation.
- **Pluggable Components**: Supports multiple backends (e.g., Redis, Kafka) configured via YAML files.
- **Cloud-Native**: Designed for Kubernetes but works locally too.

#### Dapr Architecture
Dapr uses a **sidecar pattern**:
- **Application**: Your app (e.g., a FastAPI service).
- **Dapr Sidecar**: A container in the same pod, exposing APIs on port 3500 (HTTP).
- **Dapr APIs**: Your app calls the sidecar (e.g., `http://localhost:3500/v1.0/state`) to perform tasks.
- **Components**: The sidecar connects to backends (e.g., Redis for state) based on configuration.

For example, your app sends an HTTP request to the sidecar to save data, and the sidecar stores it in Redis, handling retries and errors transparently.

#### Why Dapr for DACA?
Dapr aligns with DACA’s goals:
- **Simplified Communication**: Streamlines service-to-service calls and messaging.
- **State Management**: Manages state for stateless apps, fitting DACA’s container design.
- **Resilience**: Offers retries and fault tolerance for robust systems.
- **Scalability**: Integrates with Kubernetes for planet-scale deployments.
- **Flexibility**: Supports free-tier services (e.g., Upstash Redis) for prototyping.

### Dapr Building Blocks
Dapr provides **building blocks** to solve distributed system challenges, each with a standardized API and multiple backend options. Key blocks for DACA include:
1. **Service Invocation**: Synchronous calls between services with discovery and retries.
   - Example: A Chat Service calls an Analytics Service.
2. **State Management**: Key-value storage for data like user sessions.
   - Example: Store message counts in Redis.
3. **Publish/Subscribe (Pub/Sub)**: Asynchronous messaging via brokers like Redis.
   - Example: Publish a “MessageSent” event for subscribers to process.
4. **Bindings**: Connect to external systems (e.g., databases).
5. **Actors**: Manage stateful objects for concurrent processing.
6. **Workflows**: Orchestrate long-running processes.
7. **Secrets**: Securely store API keys.
8. **Configuration**: Manage feature flags.
9. **Observability**: Trace and monitor with tools like Zipkin.

## Learning Objectives
1. Install and configure Dapr using Helm.
2. Understand Dapr’s control plane, sidecar, and CLI.
3. Deploy Redis and Dapr components.
4. Interact with Dapr’s state and pub/sub APIs directly.
5. Verify state data in Redis.
6. Monitor with the Dapr Dashboard.
7. Build a FastAPI app with hot reloading and Dapr integration.

## Prerequisites
- **Rancher Desktop**: Installed and running with Kubernetes enabled.
- **Helm**: Installed (v3).
- **kubectl**: Configured for Rancher Desktop.
- **nerdctl**: For building and loading images into `containerd`.
- **Python 3.9+**: For FastAPI.
- **uv**: For Python dependency management (`pip install uv`).
- **curl**: For API testing.

Complete the steps 
- 1. Dapr Helm Hands On
- 2. Setup Dapr with FastAPI
- 3. Add hot reloading in FastAPI for *Cloud Native Local Development Environment*.
- 4 Finally Setup Dapr Sidecar and Complete  *Cloud Native Local Development Environment*. Setup.

## DACA Context
This setup supports DACA:
- **Stateless Computing**: FastAPI app offloads state to Redis.
- **Event-Driven Architecture**: Pub/sub enables reactive workflows.
- **Cloud-First**: Helm ensures portability.
- **Resilience**: Dapr’s sidecar handles retries.

## Resources
- Dapr Kubernetes Deployment: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/
- Dapr Helm Chart: https://github.com/dapr/dapr/tree/master/charts/dapr
- Dapr Dashboard: https://docs.dapr.io/operations/monitoring/dashboard/
- FastAPI: https://fastapi.tiangolo.com/
- UV: https://docs.astral.sh/uv/