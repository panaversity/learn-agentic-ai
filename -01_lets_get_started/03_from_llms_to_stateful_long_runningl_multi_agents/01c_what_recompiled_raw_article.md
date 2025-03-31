# From LLMs to Stateful, Long-Running Multi-Agent Systems

## Introduction

2025 is shaping up to be the year of **Agentic AI**, marking a significant transition as enterprises increasingly adopt AI Agents to automate complex workflows. This raises a key question: what exactly are these AI Agents, and what capabilities should we expect from them?

![Agent Orchestration Layer](./agent-orchestration-layer.png)

---

## Understanding AI Agents

### Definition

AI agents are **large language models (LLMs)** operating in an iterative loop. They autonomously plan, execute actions, and adapt dynamically to achieve goals, using tools and feedback from their environment. Human checkpoints are often integrated to balance autonomy with oversight.

![evoution](./evalution.jpeg)

Reference:

https://www.linkedin.com/posts/rakeshgohel01_how-did-the-agentic-ai-era-evolve-in-the-activity-7310276654218493953-8G4v


#### Key Components:
- **LLMs:** The core intelligence driving agent decisions.
- **Iterative Loop:** Continuous "think-act-observe" cycles.
- **Tools:** External functions or APIs (e.g., data fetching, sending messages).
- **Environmental Feedback:** Results from tool calls or interactions influencing subsequent actions.
- **Autonomous Action:** Dynamic planning rather than scripted tasks.
- **Human Checkpoints:** Human validation for critical decisions.

AI Agents differ fundamentally from traditional workflows by their adaptive, goal-driven behavior.

---

## Role of LLM APIs

### Democratizing Agent Development

The emergence of **LLM APIs** (e.g., OpenAI, Anthropic, Google Gemini) has drastically reduced complexity, cost, and barriers in agent development.

#### Benefits:
- **Text Generation & Reasoning:** Answering queries, planning actions.
- **Tool Invocation:** Function-calling capabilities.
- **Structured Outputs:** Easily parseable responses enabling automated actions.

### API Standardization

As of March 2025, the industry has standardized around OpenAI's **Chat Completion API**. This API is widely adopted, offering a unified approach to conversational AI development.

#### Evolution to Responses API

OpenAI introduced the **Responses API**, a significant enhancement and superset of the Chat Completion API, incorporating advanced features:
- Built-in support for multiple tools (web search, file retrieval, computation).
- Complex workflow orchestration capabilities.
- Consolidation of features from the soon-to-be-retired Assistants API by mid-2026.

The Responses API is designed explicitly for building autonomous, action-oriented agents—streamlining agentic workflows and future-proofing agent development.

---

## Agent Memory Systems

### Short-Term Memory

- **Definition:** Immediate context (recent interactions).
- **Implementation:** Embedded directly within prompts (context window).
- **Example:** Keeping recent chat history to maintain coherence.

### Long-Term Memory

- **Definition:** Persistent storage of user preferences, facts, or historical interactions.
- **Implementation:** External databases (vector or key-value stores) accessed via retrieval mechanisms (e.g., embeddings, explicit tool calls).
- **Agentic RAG (Retrieval-Augmented Generation):** Advanced method enabling agents to reason, plan, and actively retrieve long-term memory dynamically, often through explicit tool calls.

Long-term memory retrieval can be either implicit (automated retrieval) or explicit (agent-decided retrieval), increasingly favoring the latter in modern agentic designs.

---

## Multi-Agent Systems

### Defining Roles via System Prompts

- **Purpose:** Tailor each agent’s behavior, personality, and objectives.
- **Example:** "You are a researcher agent," "You are a coordinator agent."

### Inter-Agent Communication

- **Method:** Primarily tool-calling for communication ("handoff").
- **Alternatives:** Non-tool mechanisms (memory queues, event-driven communication).

Multi-agent communication allows complex coordination, enabling sophisticated task delegation and orchestration.

---

## Standardization with Model Context Protocol (MCP)

### Purpose of MCP

- Provides a standardized, interoperable way for AI agents to discover and utilize external tools dynamically.
- Reduces complexity by offering a uniform, "USB-C-like" interface for agent-tool interactions.

### Architecture

- **Servers:** Expose tools or data sources.
- **Clients:** Agents dynamically discover and invoke these tools through standardized JSON-RPC calls.

### Advantage

MCP allows AI agents to interact effortlessly with common services like Google Drive, Slack, or custom databases without hardcoded integrations.

---

## Enhancing Web Interactions with `/llms.txt`

Due to limited context windows and complex webpage structures, a standard for LLM-friendly web content, `/llms.txt`, is emerging. It simplifies content retrieval, providing concise, structured data optimized specifically for LLM consumption, complementing MCP rather than competing with it.

---

## Design Patterns for Multi-Agent Systems

Anthropic’s research identifies key design patterns:

- **Prompt Chaining:** Sequential processing of outputs.
- **Routing:** Classifying and directing tasks to specialized agents.
- **Parallelization:** Simultaneous, distributed processing.
- **Orchestrator-Workers:** Central coordination of delegated tasks.
- **Evaluator-Optimizer:** Iterative refinement through evaluation and feedback.

### Agentic vs. Workflow Systems
- **Workflows:** Predefined and orchestrated processes.
- **Agents:** Dynamically controlled by LLMs with autonomous decision-making.

These patterns can be implemented:
- **Locally:** Short-term, transient workflows orchestrated via Python or similar tools.
- **In the Cloud:** Long-running, stateful workflows requiring persistent storage, scalability, and reliability, leveraging cloud infrastructure (AWS, GCP, Kubernetes, etc.).

---

## Transition from Local to Cloud-Based Multi-Agent Systems

### Short-Term Multi-Agent Workflows

- **Local Execution:** Ideal for brief, ephemeral interactions without persistent state.
- **Tools:** Python scripts or frameworks like LangChain, enabling lightweight orchestration.

### Long-Term Stateful Multi-Agent Systems

- **Cloud Infrastructure:** Essential for persistence, concurrency, reliability, and scalability.
- **Technologies:** Cloud databases (PostgreSQL, DynamoDB), distributed computing platforms (serverless, Kubernetes), and robust service architectures.

Cloud infrastructure becomes indispensable as complexity, concurrency, and state persistence requirements grow.

---

## Conclusion

The trajectory toward agentic AI is clear: from leveraging powerful LLM APIs, structured outputs, and dynamic tool calls to adopting standardized protocols (MCP, `/llms.txt`) and advanced design patterns. The future is shaped by intelligent, autonomous, and coordinated multi-agent systems, scalable both locally for lightweight tasks and in the cloud for robust, stateful, long-running workflows.

## Subject: Analysis of Agentic AI Framework Design: Layered vs. Unified Approaches

https://github.com/panaversity/learn-agentic-ai/blob/main/-01_from_llms_to_stateful_long_runningl_multi_agents/01d_what_raw_formated_article.md#subject-analysis-of-agentic-ai-framework-design-layered-vs-unified-approaches


