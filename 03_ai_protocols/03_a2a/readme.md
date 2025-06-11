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
Agents find each other using **Agent Cards**, JSON files hosted at a well-known URI (e.g., `/.well-known/agent.json`). These cards detail an agent’s capabilities and how to connect.

### 2. Message Exchange
Agents send **Messages** with **Parts** (text, data, or files). The client uses the role `"user"`, and the server uses `"agent"`, even in agent-to-agent communication. For Parts explanation see below.

### 3. Task Management
Tasks are created to handle requests, with states like `working`, `completed`, or `input-required`. Clients can poll task status or receive updates via streaming or notifications.

### 4. Artifacts
Outputs (file, text, data) streamed or returned when complete

---
## Example: Full Agent Card JSON

The **Agent Card** is a JSON document hosted at a well-known URI (e.g., `/.well-known/agent.json`) that enables agent discovery by advertising an agent’s identity, capabilities, and connection details. Below is an example of a complete Agent Card JSON, including all possible fields as defined by the A2A protocol.

### Agent Card Structure
- **`name`**: A human-readable name for the agent.
- **`url`**: The base URL for the agent’s A2A endpoint (e.g., where `message/send` or `message/stream` requests are sent).
- **`capabilities`**: An object describing supported features, such as streaming or push notifications.
- **`skills`**: An array of specific tasks or functions the agent can perform (e.g., "weather_forecast", "document_summary").
- **`defaultInputModes`**: An array of MIME types the agent accepts as input (e.g., `text/plain`, `application/json`).
- **`defaultOutputModes`**: An array of MIME types the agent can produce as output.
- **`authenticationMethods`**: An array of supported authentication schemes (e.g., OAuth2, JWT, API Key).
- **`uiHints`**: Optional rendering preferences for client-side interfaces (e.g., iframe, video player).
- **`version`**: The A2A protocol version supported by the agent.
- **`contact`**: Optional contact information for the agent’s maintainer (e.g., email or website).
- **`description`**: A brief description of the agent’s purpose or functionality.

### Example Agent Card
This example represents a weather forecasting agent with comprehensive capabilities and configuration.

```json
{
  "name": "Weather Forecasting Agent",
  "url": "https://weather-agent.example.com/a2a/v1",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "longRunningTasks": true,
    "humanInLoop": true
  },
  "skills": [
    "weather_forecast",
    "climate_analysis",
    "historical_weather_data"
  ],
  "defaultInputModes": [
    "text/plain",
    "application/json",
    "text/csv"
  ],
  "defaultOutputModes": [
    "application/json",
    "text/plain",
    "text/html"
  ],
  "authenticationMethods": [
    {
      "type": "oauth2",
      "authorizationUrl": "https://auth.example.com/oauth/authorize",
      "tokenUrl": "https://auth.example.com/oauth/token",
      "scopes": ["weather:read", "weather:forecast"]
    },
    {
      "type": "bearer",
      "jwksUrl": "https://weather-agent.example.com/.well-known/jwks.json"
    },
    {
      "type": "apiKey",
      "headerName": "X-Api-Key"
    }
  ],
  "uiHints": {
    "preferredRenderModes": [
      "text",
      "iframe",
      "video"
    ],
    "iframeOptions": {
      "width": "100%",
      "height": "400px",
      "allow": "fullscreen"
    }
  },
  "version": "0.2.2",
  "contact": {
    "email": "support@weather-agent.example.com",
    "website": "https://weather-agent.example.com"
  },
  "description": "A specialized agent for providing real-time weather forecasts, climate analysis, and historical weather data for global locations."
}
```

### Usage
- **Discovery**: A client agent fetches this Agent Card via a GET request to `https://weather-agent.example.com/.well-known/agent.json` to learn how to interact with the weather agent.
- **Interoperability**: The `skills` and `defaultInputModes`/`defaultOutputModes` fields help the client determine if the agent can handle specific tasks (e.g., JSON-based weather forecasts).
- **Security**: The `authenticationMethods` field guides the client on how to authenticate requests (e.g., using OAuth2 or a bearer token).
- **UI Rendering**: The `uiHints` field suggests how outputs should be displayed, such as rendering forecast data in an iframe or as plain text.

This Agent Card ensures that client agents can discover and collaborate with the weather agent efficiently, securely, and with optimal user experience integration.


---

## 🛠️ How A2A Works

A2A enables seamless, secure collaboration between a **Client Agent** (who initiates tasks) and a **Remote Agent** (who executes them). The interaction proceeds through four key capabilities:

### 1. Capability Discovery

Each remote agent exposes an **Agent Card**—a JSON file (typically at `/.well-known/agent.json`) that declares its skills, supported input/output types, UI modalities, and authentication methods. Client agents fetch these cards to find the right specialist agent for a task.

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
| 1. Discovery                | Client fetches the Agent Card to learn capabilities and connection details.   |
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

### What are Parts?

In the Google Agent-to-Agent (A2A) Protocol, **Parts** are components of a **Message** used to structure and transmit content between agents. Here's a clear explanation of "Parts":

- **Parts** are individual pieces of content within a Message, allowing agents to send multiple types of data (e.g., text, structured data, files, or media) in a single conversational turn.
- Each Part is a self-contained unit with a specific **kind** (type) and associated content, enabling flexible and multimodal communication.
- Parts are included in the `parts` array of a Message, which has a `role` (either `"user"` for the client or `"agent"` for the server).

### Key Characteristics of Parts
1. **Modularity**: Parts allow Messages to carry diverse content types, such as text snippets, images, or JSON data, in a single exchange.
2. **Content Type Specification**: Each Part specifies its `kind` (e.g., `"text"`, `"data"`, `"file"`) to indicate the type of content it contains.
3. **UI Hints**: Parts may include optional UI hints to guide how the content should be rendered on the client side (e.g., as text, an iframe, or a video player).
4. **Machine-Readable**: Structured Parts (e.g., `"data"`) ensure content is easily processed by other agents, supporting automation and interoperability.

### Structure of a Part
A Part typically includes:
- **`kind`**: The type of content (e.g., `"text"`, `"data"`, `"file"`).
- **Content**: The actual data, which varies by kind:
  - For `"text"`, a `text` field contains a string.
  - For `"data"`, a `data` field contains structured data (e.g., JSON).
  - For `"file"`, a reference to a file (e.g., a pre-signed URL).
- **Optional Fields**: May include UI hints or metadata for rendering or processing.

### Example from the Document
In the **Travel Agent and Weather Agent Collaboration** example, Agent A sends a Message to Agent B with two Parts:

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

- **First Part**: A `"text"` Part with the instruction "Provide a weather forecast."
- **Second Part**: A `"data"` Part with structured JSON specifying the location ("Paris") and date range for the forecast.

Agent B responds with a Task containing an **Artifact** that includes a Part:

```json
{
  "kind": "data",
  "data": {
    "forecast": [
      {"date": "2023-10-01", "temperature": 20, "condition": "committed"},
      {"date": "2023-10-02", "temperature": 18, "condition": "completed"}
    ]
  }
}
```

- This Part contains the weather forecast as structured JSON data in a `"data"` Part.

### Role in A2A Communication
- **Collaboration**: Parts enable agents to exchange rich, structured information, such as asking clarifying questions or sharing intermediate results.
- **Flexibility**: By supporting multiple Parts in a single Message, agents can handle complex, multimodal tasks (e.g., combining text instructions with images or data).
- **Interoperability**: The use of standardized Part kinds ensures that agents built by different vendors can understand and process the content.
- **User Experience**: UI hints in Parts allow agents to negotiate how content is displayed in the client’s interface, enhancing adaptability.

### Summary
Parts are the building blocks of Messages in the A2A protocol, enabling agents to send diverse, structured, and multimodal content in a single exchange. They are defined by their `kind` and content, support machine-readable formats, and facilitate collaboration by allowing agents to share text, data, files, or media with optional UI rendering guidance.


---

## Basic interaction – `message/send`

**Client → Server**

```http
POST /agent HTTP/1.1
Content-Type: application/json
Accept: application/json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": 1,
  "params": {
    "message": {
      "role": "user",
      "parts": [{ "type": "text", "text": "Summarise Q2 board deck" }]
    }
  }
}
```

**Server → Client** – single JSON response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "taskId": "t-123",
    "status": { "state": "working" }
  }
}
```

Use `tasks/get` to poll until `status.state` becomes `"completed"`.([google-a2a.github.io][1])

---

## Real-time streaming – `message/stream`

Same request body, but call `message/stream` and set `Accept: text/event-stream`.
Server keeps the connection open and emits events:

```
data: {"jsonrpc":"2.0","id":1,
       "result":{"kind":"status-update","status":{"state":"working"}}}

data: {"jsonrpc":"2.0","id":1,
       "result":{"kind":"artifact-update","artifact":{"mime":"text/markdown","parts":[...]}}}

data: {"jsonrpc":"2.0","id":1,
       "result":{"kind":"status-update","status":{"state":"completed"},"final":true}}
```

*If the socket drops before `final:true`, call `tasks/resubscribe` to continue.

---

## Asynchronous workflows – Push notifications

1. **Client supplies a webhook** in either the initial send/stream call or later via `tasks/pushNotificationConfig/set`.
2. **Server verifies** the URL (challenge-response) and authenticates using JWT, API-Key, or HMAC as requested.([google-a2a.github.io][2])
3. **On major state changes** (e.g., `completed`, `input-required`) the server POSTs a minimal payload to the webhook.
4. Client validates signature/token, then calls `tasks/get` to fetch the full Task object.

Why JWT + JWKS?  – lets servers rotate keys without breaking receivers.([google-a2a.github.io][2], [googlecloudcommunity.com][6])

---

## Task management API surface

| Method              | Purpose              | Typical use                 | Notes                                                           |
| ------------------- | -------------------- | --------------------------- | --------------------------------------------------------------- |
| `tasks/get`         | Poll task state      | Mobile / serverless clients | Returns full `Task`.                |
| `tasks/cancel`      | Attempt cancellation | User abort, quota limit     | May return `TaskNotCancelableError`. |
| `tasks/resubscribe` | Re-join SSE stream   | Network hiccup              | Requires `capabilities.streaming`.   |

Error codes follow JSON-RPC plus A2A-specific codes (`-32001` TaskNotFound, etc.).

---

## Security checklist

| Threat                  | Mitigation                                                                                                            |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Webhook SSRF**        | Allow-list or challenge the client-supplied URL.([google-a2a.github.io][2])                                           |
| **Impersonated Server** | Use TLS + optional mTLS; verify JWT issuer/audience claims. |
| **Replay attacks**      | Include `iat` and `jti` in signed notifications; reject stale timestamps.)                  |
| **Secret rotation**     | Host JWKS endpoint and use `kid` header for key discovery.                                 |

---

## End-to-end stream example (Hello World stream)

1. **Start server** (from samples above).
2. **Send request**:

```bash
curl -N -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d @hello.json http://localhost:8000/agent
```

`hello.json`:

```json
{"jsonrpc":"2.0","method":"message/stream","id":"42",
 "params":{"message":{"role":"user","parts":[{"type":"text","text":"Hello!"}]}}}
```

3. **Watch SSE**: you’ll see `status-update` then `artifact-update` lines until `final:true`, after which the server closes the stream.

---

## How A2A differs from MCP (one-liner)

MCP is **agent ↔ front-end**; A2A is **agent ↔ agent**.  Both reuse JSON-RPC over HTTP and SSE, but A2A layers discovery (Agent Card), task lifecycle, and push-notification workflows specialised for peer-to-peer collaboration.

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




---

