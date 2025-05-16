# MCP Architecture Deep Dive

_(Based on the [MCP Specification 2025-03-26 Architecture](https://modelcontextprotocol.io/specification/2025-03-26/architecture) and the [Streamable HTTP Transport Merged PR Discussion](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/206))_

The Model Context Protocol (MCP) utilizes a **Client-Host-Server architecture**. Built on JSON-RPC, MCP defines a **session-based protocol** focused on context exchange, capability negotiation, and sampling coordination between Clients and Servers. The introduction of the **Streamable HTTP transport** (part of the 2025-03-26 specification) provides significant flexibility, **allowing MCP Servers (especially HTTP-based ones) to be implemented in a fully stateless manner if desired**, while still enabling stateful operations for servers that require them.

## Core Components

### 1. MCP Host

The Host process acts as the primary container and central coordinator for MCP interactions.

- **Role & Responsibilities:**
  - Creates and manages multiple MCP Client instances.
  - Controls Client connection permissions and their lifecycle (e.g., when a client connects or disconnects from a server).
  - Enforces security policies and manages user consent requirements for accessing servers or data.
  - Handles user authorization decisions related to MCP operations.
  - Coordinates the integration with AI/LLM models, including managing AI "sampling" requests (i.e., requests for the AI to generate text or make decisions).
  - Manages context aggregation from various clients/servers to provide a unified view for the AI model or end-user.
  - Acts as the main interface for the end-user or the AI model.
- **Examples:** AI Assistants (e.g., Claude Desktop), IDEs with AI features (e.g., Zed, Sourcegraph Cody), custom AI-powered applications.

### 2. MCP Clients

Each MCP Client is created by the Host and manages a connection to a single MCP Server.

- **Role & Responsibilities:**
  - Initiates connections and performs the **`initialize` handshake** with Servers, including capability exchange.
  - Routes MCP messages bidirectionally.
  - Manages resource subscriptions and notifications.
  - Maintains security boundaries between Servers.

### 3. MCP Servers

MCP Servers provide context, tools, or capabilities. With the Streamable HTTP transport, their operational statefulness is flexible.

- **Role & Responsibilities:**
  - Respond to the `initialize` handshake.
  - Expose **resources**, **tools**, and **prompt templates**.
  - Can request AI/LLM "sampling" through the Client.
  - Must respect security constraints.
- **Operational Models (enabled by Streamable HTTP Transport):**
  - **Stateless Server:**
    - A server can acknowledge the `initialize` request (fulfilling the protocol step) but choose not to persist any session-specific state if its operations are inherently stateless (e.g., a server offering simple, idempotent tools).
    - Each incoming request (e.g., `tool/execute`) is processed independently.
    - This model eliminates the need for long-lived connections or shared session stores for such servers, simplifying deployment (e.g., on serverless platforms).
  - **Stateless Server with Streaming:**
    - Even a stateless server can leverage streaming for operations like sending progress notifications during a tool call. The server indicates the response will be SSE for that specific operation and closes the stream upon completion.
  - **Stateful Server:**
    - Servers that require session context (e.g., for resource subscriptions, complex multi-step interactions) can establish a session ID during/after initialization.
    - The client includes this session ID in subsequent requests, allowing the server to retrieve and use the session state. This is similar to traditional stateful MCP operations.
- **Deployment:**
  - **Local (Stdio):** Can run as a subprocess.
  - **Remote (Streamable HTTP):** Runs as an independent network service, leveraging the flexibility of the Streamable HTTP transport for stateless or stateful operation.

## Communication Backbone: JSON-RPC 2.0 & Streamable HTTP

- All MCP messages **MUST** adhere to JSON-RPC 2.0.
- For remote communication, the **Streamable HTTP transport** is key. It uses a single `/message` endpoint for client-server messages and allows servers to optionally upgrade responses to SSE for streaming. This transport is designed for robustness, resumability, and compatibility with standard HTTP infrastructure, and it underpins the possibility of stateless server implementations.

## Key MCP Design Principles

The architecture of MCP is guided by several core principles outlined in the specification:

1.  **Servers should be extremely easy to build:**
    - Host applications handle complex orchestration responsibilities.
    - Servers focus on specific, well-defined capabilities.
    - Simple interfaces minimize implementation overhead.
    - Clear separation enables maintainable code.
2.  **Servers should be highly composable:**
    - Each server provides focused functionality in isolation.
    - Multiple servers can be combined seamlessly by a Host.
    - Shared protocol enables interoperability.
    - Modular design supports extensibility.
3.  **Servers should not be able to read the whole conversation, nor "see into" other servers:**
    - Servers receive only necessary contextual information from the Host.
    - Full conversation history stays with the Host.
    - Each server connection maintains isolation.
    - Cross-server interactions are controlled by the Host.
    - The Host process enforces security boundaries.
4.  **Features can be added to servers and clients progressively:**
    - The core protocol provides minimal required functionality.
    - Additional capabilities can be negotiated as needed.
    - Servers and clients evolve independently.
    - The protocol is designed for future extensibility.
    - Backwards compatibility is maintained.

## Capability Negotiation: A Cornerstone

A fundamental aspect of MCP is its capability-based negotiation system.

- During session initialization, Clients and Servers explicitly declare their supported features (e.g., server declares tool support and what tools are available; client declares sampling support).
- This process determines which protocol features and primitives are available for that specific session.
- It ensures both parties have a clear understanding of supported functionality, maintaining protocol extensibility and robustness.
  _(This is detailed further in `03_protocol_lifecycle_and_capabilities.md`)_