# Security Fundamentals: Securing DACA Agents in Kubernetes

## Overview
This module introduces essential Kubernetes security practices for building secure DACA agentic applications, following **03_dapr_intro**. It focuses on core areas to align with the [Kubernetes Security Concepts](https://kubernetes.io/docs/concepts/security/) and prepare learners for secure Dapr Actors in **05_agent_actors**.

### Learning Progression
1. **ConfigMaps**: Externalize non-sensitive configuration for the FastAPI app, teaching resource management basics.
2. **Secrets**: Secure sensitive data (e.g., Gemini API keys), building on ConfigMaps.
3. **API-endpoint Security & JWT/OAuth2 Scopes**: Secure FastAPI endpoints using JWT tokens and OAuth2 scopes.
4. **OAuth2 Grant Flows**: Implement Client Credentials and Authorization Code + PKCE flows for secure API access.

This progression moves from foundational resource management to application-level API security, applied to the DACA FastAPI app from **03_dapr_intro/**.

## Why Security Matters for DACA
DACA’s agentic architecture relies on distributed systems in Kubernetes, where:
- **ConfigMaps** enable dynamic configuration of agent settings (e.g., logging levels, API endpoints).
- **Secrets** protect sensitive data (e.g., API keys for the OpenAI Agents SDK).
- **API-endpoint Security & JWT/OAuth2 Scopes** secure user and service interactions with agent APIs (e.g., group chat endpoints).
- **OAuth2 Grant Flows** provide flexible authentication for users and services, ensuring secure access to agent resources.

These practices prevent unauthorized access and data leaks, aligning with DACA’s goals of resilience, scalability, and secure cloud-native deployment.

## Learning Objectives
1. **Create and Use ConfigMaps**: Configure the FastAPI app dynamically.
2. **Manage Secrets Securely**: Store and access sensitive data with restricted access.
3. **Secure API Endpoints**: Implement JWT/OAuth2 scopes for FastAPI endpoint protection.
4. **Implement OAuth2 Grant Flows**: Use Client Credentials and Authorization Code + PKCE for secure API access.
5. **Apply Security Practices**: Secure the FastAPI app for actor-based agents in **05_agent_actors**.


## Prerequisites
- **Completed Modules**:
  - **01_ai_agents_first/**: OpenAI Agents SDK basics.
  - **02_agent_native_cloud_setup/**: Kubernetes, Helm, Rancher Desktop.
  - **03_dapr_intro/**: Dapr setup, pub/sub, state management, FastAPI integration (up to `04_dapr_sdk/`).
- **Tools**:
  - Rancher Desktop with Kubernetes (3GB+ memory).
  - Dapr CLI, Helm, `kubectl`, Skaffold/Tilt, Python 3.9+.
  - `nerdctl` for container management.
  - Gemini API key.


## Module Structure
The module consists of four sections, each with two phases:

1. **01_configmaps**: Managing Configuration with ConfigMaps
2. **02_secrets**: Securing Sensitive Data with Secrets
3. **03_api_endpoint_security**: API-endpoint Security with JWT/OAuth2 Scopes
4. **04_oauth2_grant_flows**: OAuth2 Grant Flows (Client Credentials, Authorization Code + PKCE)

### Learning Phases
Each step will:
- **Phase 1: Core + Practical**: Theoretical concepts with practical explanations and examples, introducing DACA relevance.
- **Phase 2: Lab**: Hands-on implementation using starter code, with step-by-step tasks to apply security practices to the FastAPI app.

## Next Steps
- After completing this module proceed to **04_agent_actors/01_actor_fundamentals/** to build AI agents as Dapr Actors, applying security practices (e.g., RBAC for actor deployments, Secrets for API keys, OAuth2 for user access, mTLS for A2A communication).
- Explore advanced security in **00_concepts_strategies_technologies/08_observability/** for monitoring secure systems.
- Prepare for **04_agent_actors/07_a2a_integration/** to deepen mTLS and A2A security practices.

## Resources
- [Kubernetes Security Concepts](https://kubernetes.io/docs/concepts/security/)
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [API Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)