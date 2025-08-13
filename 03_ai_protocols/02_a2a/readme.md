# Google Agent to Agent (A2A) Protocol - Agents Communicating with Agents

[Agent2Agent (A2A) Crash Course: Full Walkthrough With Real Multi-Agent Examples](https://www.youtube.com/watch?v=mFkw3p5qSuA)

The Agent-to-Agent (A2A) protocol is new standard for enabling AI agents to communicate with each other regardless of the underlying framework they use. Whether your agents are built with OpenAI Agents SDK, ADK, CrewAI, LangGraph, or any other framework, A2A provides a standardized communication layer. This will increase autonomy and multiply productivity gains, while lowering long-term costs.

> [Google Cloud has donated A2A to the Linux Foundation](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/)! A2A is now an open, vendor-neutral standard backed by Amazon Web Services, Cisco, Google, Microsoft, Salesforce, SAP, and ServiceNow etc.

---

## Why A2A Protocol?

### The Problem Without A2A

Imagine you have a personal assistant agent that needs to:

- Book a hotel through a hotel booking agent
- Rent a car through a car rental agent
- Get weather information from a weather agent

Without A2A, for each agent you want to communicate with, you need to:

- Figure out what the agent can do
- Understand what format of information to send (audio, text, JSON?)
- Learn what kind of response to expect
- Build custom tools and wrappers for each agent

This creates redundant work and complexity as you scale to more agents.

### The Solution With A2A
A2A standardizes agent communication by providing:

- Uniform discovery: Standard way to find out what agents can do
- Consistent messaging: Standardized message format across all agents
- Framework agnostic: Works with any AI framework underneath
- Scalable architecture: Easy to add new agents without custom integration

## 1. What Value is A2A Providing?

- Interoperability & opacity – Agents running on different stacks can cooperate without leaking internal prompts, weights, or tool code.

- Async-first design – Long tasks, human-in-the-loop approvals, and incremental artefact uploads are first-class citizens.

- Enterprise readiness – Spec includes TLS, mTLS, OAuth 2 / JWT, push-notification hardening, and error codes.

- Analysts see A2A (alongside MCP) as a key building block for future multi-agent ecosystems.

---

## 📐 Design Principles

Here’s a polished and integrated **Design Principles** section for your A2A learning guide, drawing directly from official sources:

### 1. **Embrace agentic capabilities**

A2A empowers agents to collaborate in their native, unstructured modalities—whether reasoning, synthesizing, or conversing—**without sharing memory, tools, or internal context**. This enables true multi-agent workflows rather than reducing each agent to a single-function “tool”.

---

### 2. **Build on existing standards**

Instead of reinventing the wheel, A2A builds on proven open standards—**HTTP(S)** for transport, **JSON‑RPC 2.0** for structured messaging, and **Server‑Sent Events (SSE)** for real-time streaming. This makes integration with existing IT systems smoother and more maintainable.

---

### 3. **Secure by default**

Security is foundational in A2A. The protocol includes **enterprise-grade authentication and authorization**, aligning with OpenAPI security schemes (e.g., OAuth2, bearer tokens, JWT). This ensures agents interact over **encrypted, trusted channels** right out of the gate.

---

### 4. **Support for long-running tasks**

Agent-enabled tasks often span large timeframes—from seconds to hours or even days. A2A is built to support this with real-time insights into task state (“working”, “input‑required”, “completed”), **streaming updates**, and notifications meant for human-in‑the‑loop workflows.

---

### 5. **Modality agnostic**

The protocol doesn’t limit agents to plain text. Whether it’s **audio, video, images, structured data, or interactive UI components**, A2A supports rich and evolving communication forms, enabling truly versatile multi-agent systems.

---

## Core Concepts

### 1. Agent Discovery

Agents find each other using **Agent Cards**, JSON files hosted at a well-known URI (e.g., `/.well-known/agent-card.json`). These cards detail an agent’s capabilities and how to connect.

#### 1. Agent Cards
Think of agent cards as business cards for AI agents. Each agent publishes a card that includes:

- Name: The agent's identifier
- Description: High-level overview of what the agent does
- URL: Where the agent is hosted
- Input/Output modes: Supported data types (text, audio, etc.)
- Skills: Specific capabilities the agent offers
- Example queries: Sample requests the agent can handle

Example agent card structure:
```json
{
  "name": "Hotel Booking Agent",
  "description": "Personal concierge for booking and managing hotel reservations",
  "url": "localhost:1003",
  "skills": [
    {
      "name": "book_room",
      "description": "Book a hotel room for specified dates"
    },
    {
      "name": "check_availability", 
      "description": "Check room availability for given dates"
    }
  ],
  "examples": [
    "Book a room for this weekend",
    "Are there any king suites available?"
  ]
}
```

### 2. Message and Tasks

A2A uses two main communication types:
1. Messages: For quick, immediate responses. Messages contain:
    - Role: Who sent it (user, agent, etc.)
    - Parts: The actual content (text, audio, etc.)
    - Metadata: Message ID, task ID, context ID for state management

Tasks: For long-running operations that take time to complete. Tasks include:
    - Artifacts: Where the agent stores its work output
    - Status: Current state (submitted, in-progress, completed, failed)
-  Updates: Real-time status changes

Tasks are created to handle requests, with states like `working`, `completed`, or `input-required`. Clients can poll task status or receive updates via streaming or notifications.

Artifacts Outputs (file, text, data) streamed or returned when complete

### 3. Agent Executor
A wrapper class that standardizes how agents receive and process requests. Every A2A-compliant agent must implement:

- execute(): Processes incoming requests
- cancel(): Handles cancellation requests

The agent executor bridges the gap between A2A's standard interface and your specific agent framework.

## Understanding A2A Fundamentals

### Basic Workflow

1. Discovery: Client agent fetches agent cards from remote agents
2. Selection: Based on capabilities, client chooses appropriate agent
3. Communication: Client sends standardized messages via HTTP/HTTPS
4. Processing: Remote agent processes request through agent executor
5. Response: Remote agent returns standardized message or task

### Communication Flow Example

Personal Agent → Hotel Agent
1. GET /well-known/agents.json (fetch agent card)
2. POST /messages (send booking request)
3. Response: Message with booking confirmation

The A2A protocol represents an important step toward more collaborative and interoperable AI agent ecosystems, enabling developers to focus on building great agents rather than worrying about integration complexity.

## 🛠️ How A2A Works

A2A enables seamless, secure collaboration between a **Client Agent** (who initiates tasks) and a **Remote Agent** (who executes them). The interaction proceeds through four key capabilities:

### 1. Capability Discovery

Each remote agent exposes an **Agent Card**—a JSON file (typically at `/.well-known/agent-card.json`) that declares its skills, supported input/output types, UI modalities, and authentication methods. Client agents fetch these cards to find the right specialist agent for a task.

---

### 2. Task Management

Tasks are stateful units of work with a clear lifecycle: `submitted` → `working` → (`input‑required`) → `completed`/`failed`/`canceled`.
Client agents create tasks and monitor progress, while remote agents process them, update status, and eventually produce **artifacts**—the finalized outputs (text, files, media, structured data).

---

### 3. Collaboration and Messaging

Agents exchange structured **messages** via JSON-RPC over HTTP. Messages include multiple **parts**, where each part contains a complete piece of content (e.g., text snippet, image, or widget). This lets agents ask clarifying questions, share context, or pass intermediate results.

---

### 4. User-Experience Negotiation

Each message part indicates its content type and optional UI hints. This allows agents to adapt outputs to client-side interfaces—whether it’s rendering an iframe, playing a video, showing a form, or simply streaming text. This negotiation ensures outputs are displayed well in the end-user UI.

---

### 🔄 Typical Interaction Flow

| Step                        | Description                                                                                    |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| 1. Discovery                | Client fetches the Agent Card to learn capabilities and connection details.                    |
| 2. Initiation               | Client sends a task via `message/send` or starts streaming with `message/stream`.              |
| 3. Execution                | Remote agent updates task state, streaming progress via SSE or pushing via webhooks.           |
| 4. Collaboration (Optional) | If input is needed, remote agent flags `input-required`, prompting additional messages.        |
| 5. Completion               | Task transitions to final state; client retrieves artifacts via `tasks/get` or streaming ends. |

---

## How A2A differs from MCP (one-liner)

MCP is **agent ↔ context**; A2A is **agent ↔ agent**. Both reuse JSON-RPC over HTTP and SSE, but A2A layers discovery (Agent Card), task lifecycle, and push-notification workflows specialised for peer-to-peer collaboration.

---

## A2A Learning Path 🛠️

### **Phase 0: A2A Transport Specification (Step 0)**

_Master A2A transport layer specifications before implementation_

```
00_protocol_transports_spec/    # A2A Protocol Transport Specifications
                               # - Transport layer requirements (HTTPS mandatory)
                               # - JSON-RPC 2.0, gRPC, HTTP+JSON specifications
                               # - Message formats across transport protocols
                               # - Security constraints and compliance strategies
```

### **Phase 1: A2A Fundamentals (Step 1)**

_Discovery, agent cards, skills, and ecosystem understanding_

```
01_a2a_fundamentals/        # Complete A2A discovery system
                           # - Agent cards and capabilities
                           # - Skills definition and examples  
                           # - Multiple agent ecosystem
                           # - Visual browser examples
```

### **Phase 2: Core A2A Protocol (Steps 2-4)**

_Build the fundamental A2A communication patterns_

```
02_agent_executor/          # Agent executor pattern (execute/cancel)
03_client_messaging/        # Client discovery & messaging (merged step)
04_streaming_and_tasks/     # Server-sent events & task management
```

### **Phase 3: Multi-Agent Orchestration (Step 5)** ⭐

_The main event - complete multi-agent system_

```
05_multi_agent_systems/     # Host + 3 remotes (ADK/CrewAI/LangGraph)
                           # Complete Table Tennis scheduling demo
                           # ★ This is the "wow" moment ★
```

### **Phase 4: Enterprise Production (Steps 6-13)**

_Security, performance, and protocol convergence_

```
06_push_notifications/      # Async webhooks for disconnected scenarios
07_multi_turn_conversations/# Context persistence & referenceTaskIds
08_authentication/          # OAuth2, JWT, API keys, JWKS
09_mcp_a2a_bridge/          # MCP-A2A protocol convergence (MCPAgent pattern)
10_grpc_production/         # Dual transport, monitoring, CI/CD deployment
11_multiple_cards/          # Advanced agent card patterns
12_latency_routing/         # Health checks, fastest-agent selection
13_security_hardening/      # TLS/mTLS, signed cards, replay protection
```

## 🚀 The Multi-Agent Demo (Step 5)

**Scenario**: Schedule a game with friends across different AI frameworks

```
┌─────────────────┐    A2A     ┌──────────────────┐
│   Host Agent    │◄────────────►│                 │
│                 │             │  Calendar Agent  │
│  Orchestrator   │             └──────────────────┘
│                 │    A2A     ┌──────────────────┐
│ - Discovery     │◄────────────►│                 │
│ - Scheduling    │             │  Calendar Agent  │
│ - Court Booking │             └──────────────────┘
│                 │    A2A     ┌──────────────────┐
│                 │◄────────────►│                 │
└─────────────────┘             │  Calendar Agent  │
                                └──────────────────┘

User: "What time is everyone available tomorrow for Table Tennis?"

Host Agent:
1. 🔍 Discovers remote agents via Agent Cards
2. 📤 Sends A2A messages to all 3 agents in parallel
3. 📨 Collects availability responses
4. 🏓 Checks court availability using local tools
5. ⏰ Suggests optimal time slot
6. ✅ Books court when user confirms

Response: "Everyone is available tomorrow at 8 PM, and I've booked Court 1!"
```

## 📚 Step-by-Step Learning Goals

| Step   | Focus                    | Key Concepts                        | Framework                | Time     | Testing              |
| ------ | ------------------------ | ----------------------------------- | ------------------------ | -------- | -------------------- |
| **00** | Protocol Transport Spec | HTTPS, JSON-RPC 2.0, gRPC specs   | Specification Study      | 1hr      | Spec comprehension   |
| **01** | A2A Fundamentals         | Agent cards, skills, ecosystem      | Static JSON + Python    | 2hrs     | Browser + curl       |
| **02** | Agent Executor           | execute(), cancel(), RequestContext | Python A2A               | 2hrs     | curl + test script   |
| **03** | Client Messaging         | Discovery, messaging, A2A client    | Python A2A               | 3hrs     | curl + test script   |
| **04** | Streaming & Tasks        | SSE, status updates, artifacts      | Python A2A               | 3hrs     | curl + browser       |
| **05** | **Multi-Agent Systems**  | **Host + 3 remotes, orchestration** | **ADK/CrewAI/LangGraph** | **6hrs** | **Multi-agent demo** |
| **06** | Push Notifications       | Webhooks, async, disconnected       | Python A2A               | 3hrs     | Webhook test         |
| **07** | Multi-Turn Conversations | contextId, referenceTaskIds, memory | Python A2A               | 3hrs     | Conversation test    |
| **08** | Authentication           | OAuth2, JWT, API keys, JWKS         | Python A2A               | 4hrs     | Secure client test   |
| **09** | **MCP-A2A Bridge**       | **Unified MCP+A2A protocols**       | **Python A2A + MCP**     | **4hrs** | **Protocol bridge**  |
| **10** | gRPC + Production        | Dual transport, monitoring, CI/CD   | Python A2A + gRPC        | 6hrs     | Production deploy    |
| **11** | Multiple Cards           | Advanced agent card patterns        | Python A2A               | 2hrs     | Card browser test    |
| **12** | Latency Routing          | Health checks, fastest selection    | Python A2A               | 3hrs     | Performance test     |
| **13** | Security Hardening       | TLS/mTLS, signed cards, replay      | Python A2A               | 4hrs     | Security audit       |

## 🎯 Learning Outcomes by Phase

### **After Phase 0 (Step 0)**: A2A Transport Specification Foundation

- ✅ Understand A2A transport layer specifications and HTTPS requirements
- ✅ Master JSON-RPC 2.0, gRPC, and HTTP+JSON transport protocols
- ✅ Comprehend message format standards across transport layers
- ✅ Plan transport selection strategy for A2A-compliant implementations

### **After Phase 1 (Step 1)**: A2A Fundamentals

- ✅ Understand complete A2A discovery system
- ✅ Design agent cards with skills and capabilities
- ✅ Navigate multi-agent ecosystems
- ✅ Implement visual browser examples

### **After Phase 2 (Steps 2-4)**: Protocol Mastery

- ✅ Build A2A-compliant agents from scratch
- ✅ Handle all core A2A methods (message/send, message/stream, tasks/*)
- ✅ Implement client discovery and messaging patterns
- ✅ Master streaming and task management

### **After Phase 3 (Step 5)**: Multi-Agent Systems ⭐

- ✅ **Complete working multi-agent demo**
- ✅ **Cross-framework integration** (ADK + CrewAI + LangGraph)
- ✅ **Real-world orchestration** patterns
- ✅ **Framework independence** proven

### **After Phase 4 (Steps 6-13)**: Production Ready + Protocol Convergence

- ✅ Enterprise security and authentication
- ✅ Multi-turn conversation capabilities
- ✅ Performance optimization and monitoring
- ✅ Production deployment with CI/CD
- ✅ Advanced agent card patterns
- ✅ **MCP-A2A protocol bridging and convergence**
- ✅ **Unified context-collaboration agent architectures**
- ✅ Security hardening and threat protection
- ✅ Troubleshooting and best practices

## 💡 Why This Approach Works

### **1. Comprehensive Foundation Strategy**

- **Traditional**: Learn protocol → Learn tools → Maybe build multi-agent
- **Our approach**: **Complete fundamentals** → Build communication → **Multi-agent immediately** → Add enterprise features

### **2. Framework Agnostic Proof**

Step 5 demonstrates A2A's core value:

### **3. Comprehensive Foundation**

- Step 0: Transport theory foundation before any implementation
- Step 1: Complete A2A fundamentals in one cohesive lesson
- No complex setup required initially
- See full discovery ecosystem before protocol complexity

### **4. Progressive Complexity with Protocol Convergence**

- **Traditional**: Learn protocol → Learn tools → Maybe build multi-agent
- **Our approach**: **A2A transport specs** → **Complete fundamentals** → **Build communication** → **Multi-agent immediately** → **Add enterprise features** → **Protocol convergence**

### **5. Future-Ready Architecture**

- Step 0: A2A transport specification foundation before implementation
- Step 1: Complete A2A fundamentals in one cohesive lesson
- Step 7: Multi-turn conversations with context persistence
- Step 9: **MCP-A2A bridge** representing the evolution of agent protocols
- Step 13: Advanced security hardening as final defense layer
- No complex setup required initially
- See full discovery ecosystem before protocol complexity

### **6. v3.0+ Feature Complete**

- gRPC dual transport for performance
- Multi-turn conversation capabilities
- Signed agent cards for security
- Latency-aware routing for optimization
- **MCP-A2A protocol convergence**
- **Unified context-collaboration architectures**
- Advanced security hardening
- Enterprise deployment patterns

---

For more details, see the [A2A specification](https://google-a2a.github.io/A2A/specification/).

[1]: https://www.datacamp.com/blog/a2a-agent2agent?utm_source=chatgpt.com "Agent2Agent (A2A): Definition, Examples, MCP Comparison"
[2]: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com "Announcing the Agent2Agent Protocol (A2A)"
[3]: https://www.googlecloudcommunity.com/gc/Community-Blogs/Understanding-A2A-The-Protocol-for-Agent-Collaboration/ba-p/906323?utm_source=chatgpt.com "Understanding A2A — The Protocol for Agent Collaboration"
[4]: https://www.blott.studio/blog/post/how-the-agent2agent-protocol-a2a-actually-works-a-technical-breakdown?utm_source=chatgpt.com "How the Agent2Agent Protocol (A2A) Actually Works - Blott Studio"
[5]: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com "Announcing the Agent2Agent Protocol (A2A)"
[6]: https://medium.com/design-bootcamp/breaking-down-ai-silos-how-agent2agent-enables-agent-collaboration-d4951b0a2293?utm_source=chatgpt.com "Breaking down AI silos: how Agent2Agent enables agent collaboration"

---
