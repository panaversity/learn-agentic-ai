# Google Agent to Agent (A2A) Protocol - Agents Communicating with Agents

A2A is a standardized protocol that allows AI agents to discover each other, securely exchange information, manage tasks, and collaborate without exposing their internal workings. 

It is enabling agents to interoperate with each other, even if they were built by different vendors or in a different framework - this will increase autonomy and multiply productivity gains, while lowering long-term costs.
---

## 1. Why A2A?
- Interoperability & opacity – Agents running on different stacks can cooperate without leaking internal prompts, weights, or tool code.

- Async-first design – Long tasks, human-in-the-loop approvals, and incremental artefact uploads are first-class citizens.

- Enterprise readiness – Spec includes TLS, mTLS, OAuth 2 / JWT, push-notification hardening, and error codes.

- Analysts see A2A (alongside MCP) as a key building block for future multi-agent ecosystems.

---

## 📐 Design Principles
Here’s a polished and integrated **Design Principles** section for your A2A learning guide, drawing directly from official sources:

### 1. **Embrace agentic capabilities**

A2A empowers agents to collaborate in their native, unstructured modalities—whether reasoning, synthesizing, or conversing—**without sharing memory, tools, or internal context**. This enables true multi-agent workflows rather than reducing each agent to a single-function “tool”([datacamp.com][1], [developers.googleblog.com][2]).

---

### 2. **Build on existing standards**

Instead of reinventing the wheel, A2A builds on proven open standards—**HTTP(S)** for transport, **JSON‑RPC 2.0** for structured messaging, and **Server‑Sent Events (SSE)** for real-time streaming. This makes integration with existing IT systems smoother and more maintainable([developers.googleblog.com][2]).

---

### 3. **Secure by default**

Security is foundational in A2A. The protocol includes **enterprise-grade authentication and authorization**, aligning with OpenAPI security schemes (e.g., OAuth2, bearer tokens, JWT). This ensures agents interact over **encrypted, trusted channels** right out of the gate([developers.googleblog.com][2]).

---

### 4. **Support for long-running tasks**

Agent-enabled tasks often span large timeframes—from seconds to hours or even days. A2A is built to support this with real-time insights into task state (“working”, “input‑required”, “completed”), **streaming updates**, and notifications meant for human-in‑the‑loop workflows([developers.googleblog.com][2]).

---

### 5. **Modality agnostic**

The protocol doesn’t limit agents to plain text. Whether it’s **audio, video, images, structured data, or interactive UI components**, A2A supports rich and evolving communication forms, enabling truly versatile multi-agent systems([developers.googleblog.com][2]).

---

## Core Concepts

### 1. Agent Discovery
Agents find each other using **Agent Cards**, JSON files hosted at a well-known URI (e.g., `/.well-known/agent.json`). These cards detail an agent’s capabilities and how to connect.

### 2. Message Exchange
Agents send **Messages** with **Parts** (text, data, or files). The client uses the role `"user"`, and the server uses `"agent"`, even in agent-to-agent communication.

### 3. Task Management
Tasks are created to handle requests, with states like `working`, `completed`, or `input-required`. Clients can poll task status or receive updates via streaming or notifications.

### 4. Artifacts
Outputs (file, text, data) streamed or returned when complete

---

## 🛠️ How A2A Works

A2A enables seamless, secure collaboration between a **Client Agent** (who initiates tasks) and a **Remote Agent** (who executes them). The interaction proceeds through four key capabilities:

### 1. Capability Discovery

Each remote agent exposes an **Agent Card**—a JSON file (typically at `/.well-known/agent.json`) that declares its skills, supported input/output types, UI modalities, and authentication methods. Client agents fetch these cards to find the right specialist agent for a task.([googlecloudcommunity.com][3])

---

### 2. Task Management

Tasks are stateful units of work with a clear lifecycle: `submitted` → `working` → (`input‑required`) → `completed`/`failed`/`canceled`.
Client agents create tasks and monitor progress, while remote agents process them, update status, and eventually produce **artifacts**—the finalized outputs (text, files, media, structured data).([googlecloudcommunity.com][3], [blott.studio][4])

---

### 3. Collaboration and Messaging

Agents exchange structured **messages** via JSON-RPC over HTTP. Messages include multiple **parts**, where each part contains a complete piece of content (e.g., text snippet, image, or widget). This lets agents ask clarifying questions, share context, or pass intermediate results.([developers.googleblog.com][5])

---

### 4. User-Experience Negotiation

Each message part indicates its content type and optional UI hints. This allows agents to adapt outputs to client-side interfaces—whether it’s rendering an iframe, playing a video, showing a form, or simply streaming text. This negotiation ensures outputs are displayed well in the end-user UI.

---

### 🔄 Typical Interaction Flow

| Step                        | Description                                                                                    |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| 1. Discovery                | Client fetches the Agent Card to learn capabilities and connection details. ([medium.com][6])  |
| 2. Initiation               | Client sends a task via `message/send` or starts streaming with `message/stream`.              |
| 3. Execution                | Remote agent updates task state, streaming progress via SSE or pushing via webhooks.           |
| 4. Collaboration (Optional) | If input is needed, remote agent flags `input-required`, prompting additional messages.        |
| 5. Completion               | Task transitions to final state; client retrieves artifacts via `tasks/get` or streaming ends. |

---


## Example: Travel Agent and Weather Agent Collaboration

Let’s walk through an example where **Agent A** (a travel planning agent) communicates with **Agent B** (a weather forecasting agent) to get a weather forecast for Paris.

### Step 1: Discover Agent B
Agent A fetches Agent B’s Agent Card to learn its endpoint and capabilities.

**Request**:
```http
GET https://agent-b.example.com/.well-known/agent.json HTTP/1.1
Host: agent-b.example.com
```

**Response**:
```json
{
  "name": "Weather Forecasting Agent",
  "url": "https://agent-b.example.com/a2a/v1",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"]
}
```

- Agent A now knows to send requests to `https://agent-b.example.com/a2a/v1`.

### Step 2: Request a Weather Forecast
Agent A sends a message to Agent B, asking for a forecast and providing structured data.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Provide a weather forecast."
        },
        {
          "kind": "data",
          "data": {
            "location": "Paris",
            "dates": {
              "start": "2023-10-01",
              "end": "2023-10-07"
            }
          }
        }
      ],
      "messageId": "msg-001"
    }
  }
}
```

### Step 3: Agent B Responds with a Task
Agent B processes the request and returns a task with the forecast.

**Response** (immediate completion):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "task-001",
    "contextId": "ctx-001",
    "status": {
      "state": "completed"
    },
    "artifacts": [
      {
        "artifactId": "art-001",
        "parts": [
          {
            "kind": "data",
            "data": {
              "forecast": [
                {"date": "2023-10-01", "temperature": 20, "condition": "sunny"},
                {"date": "2023-10-02", "temperature": 18, "condition": "cloudy"}
              ]
            }
          }
        ]
      }
    ],
    "kind": "task"
  }
}
```

- Agent B returns the forecast in a `data` part, which Agent A can use to plan the trip.

### Alternative: Long-Running Task with Polling
If the forecast takes time, Agent B might return a `working` task:

**Initial Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "task-001",
    "contextId": "ctx-001",
    "status": {
      "state": "working"
    },
    "kind": "task"
  }
}
```

Agent A then polls for updates:

**Polling Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tasks/get",
  "params": {
    "id": "task-001"
  }
}
```

**Final Response** (when completed):
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "id": "task-001",
    "contextId": "ctx-001",
    "status": {
      "state": "completed"
    },
    "artifacts": [
      {
        "artifactId": "art-001",
        "parts": [
          {
            "kind": "data",
            "data": {
              "forecast": [
                {"date": "2023-10-01", "temperature": 20, "condition": "sunny"},
                {"date": "2023-10-02", "temperature": 18, "condition": "cloudy"}
              ]
            }
          }
        ]
      }
    ],
    "kind": "task"
  }
}
```

---

## Why This Matters

This example shows how agents can collaborate: Agent A (travel planner) relies on Agent B (weather forecaster) to provide critical data, demonstrating A2A’s power in enabling specialized agents to work together. The use of structured `data` parts ensures machine-readable communication, ideal for agent-to-agent interactions.

---

## Next Steps

Experiment with A2A by:
- Adding streaming with `message/stream` for real-time updates.
- Using push notifications for asynchronous tasks.
- Creating your own agents and Agent Cards.

For more details, see the [A2A specification](https://google-a2a.github.io/A2A/specification/).

[1]: https://www.datacamp.com/blog/a2a-agent2agent?utm_source=chatgpt.com "Agent2Agent (A2A): Definition, Examples, MCP Comparison"
[2]: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com "Announcing the Agent2Agent Protocol (A2A)"
[3]: https://www.googlecloudcommunity.com/gc/Community-Blogs/Understanding-A2A-The-Protocol-for-Agent-Collaboration/ba-p/906323?utm_source=chatgpt.com "Understanding A2A — The Protocol for Agent Collaboration"
[4]: https://www.blott.studio/blog/post/how-the-agent2agent-protocol-a2a-actually-works-a-technical-breakdown?utm_source=chatgpt.com "How the Agent2Agent Protocol (A2A) Actually Works - Blott Studio"
[5]: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com "Announcing the Agent2Agent Protocol (A2A)"
[6]: https://medium.com/design-bootcamp/breaking-down-ai-silos-how-agent2agent-enables-agent-collaboration-d4951b0a2293?utm_source=chatgpt.com "Breaking down AI silos: how Agent2Agent enables agent collaboration"
