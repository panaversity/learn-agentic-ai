# MCP Streamable HTTP Transport

_(Based on the [MCP Specification 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26) and [GitHub PR #206](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/206))_

The Streamable HTTP transport is a key component of the Model Context Protocol (MCP) for communication with **remote servers**. It was introduced as part of the 2025-03-26 specification revision. This transport addresses several limitations of the older approach while retaining its advantages, making remote MCP interactions more robust, flexible, and compatible with modern web infrastructure.

## Key Features and Design

Comparing to the previous HTTP+SSE transport:

1.  **Single Endpoint for Messages:**

    - The dedicated `/sse` endpoint is removed.
    - All Client-to-Server messages are sent via a single primary endpoint, typically `/message` (or a similarly named configurable endpoint).

2.  **Optional SSE Upgrade for Server-to-Client Streaming:**

    - Any Client-to-Server HTTP request (e.g., a POST to `/message`) can be "upgraded" by the Server to use Server-Sent Events (SSE) for the response stream.
    - This allows the Server to send multiple asynchronous messages (Notifications or even further Requests, as per MCP's bidirectional nature) back to the Client over that single established HTTP connection if needed.
    - If the Server doesn't need to stream multiple messages back for a particular request, it can simply return a standard HTTP response body (containing a single JSON-RPC response).

3.  **Client-Initiated SSE Stream:**

    - A Client can initiate an SSE stream by sending an empty GET request to the `/message` endpoint. This is useful for establishing a channel to receive asynchronous notifications from the server when the client doesn't have an immediate request to send.

4.  **Server-Managed Session IDs for State:**

    - Servers can choose to establish a session ID (typically during or after the `initialize` handshake) to maintain state across multiple requests from the same client.
    - If a session ID is used, the Client **MUST** include this session ID in subsequent requests (e.g., as an HTTP header).
    - This allows stateful servers to correlate requests with ongoing sessions, useful for features like resource subscriptions or complex, multi-step interactions.

5.  **Enables Operationally Stateless Servers:**
    - A major benefit is that this transport **allows servers to be implemented in a fully stateless manner if desired**.
    - A server can process each incoming request (including `initialize`) independently without needing to store any session state between requests if its functionality doesn't require it.
    - This significantly simplifies server deployment, especially on serverless platforms or behind standard load balancers, and eliminates the strict requirement for high-availability long-lived connections for all server types.

## Motivations for the Change

The previous HTTP+SSE transport had limitations:

- **No Resumability:** Difficult to resume sessions if connections dropped.
- **Server Burden:** Required servers to maintain long-lived connections with high availability, which could be resource-intensive.
- **Limited Server-to-Client Delivery:** Server messages (like notifications) could only be delivered over the dedicated SSE stream.

## Benefits of Streamable HTTP Transport

- **Stateless Servers Possible:** As highlighted, this is a key advantage, reducing server operational complexity and the need for persistent connections for all use cases.
- **Plain HTTP Implementation:** MCP interactions can be implemented on a standard HTTP server without necessarily requiring SSE infrastructure for all operations. SSE is an optional upgrade for streaming needs.
- **Infrastructure Compatibility:** Being "just HTTP" for many interactions ensures better compatibility with existing middleware, proxies, load balancers, and general web infrastructure.
- **Backwards Compatibility (Intent):** Designed as an incremental evolution, aiming to allow for a smoother transition from the older transport.
- **Flexible Upgrade Path:** Servers can decide on a per-request basis whether to use SSE for streaming responses or just return a simple HTTP response.

## Example Use Cases (Illustrating Flexibility)

### 1. Fully Stateless Server (e.g., Simple Tool Provider)

- **`initialize` Request:** Server acknowledges the `initialize` request (fulfilling the protocol step) but doesn't store any session ID or state from it.
- **`tool/list` Request:** Server responds with a single JSON-RPC response containing the list of tools directly in the HTTP response body.
- **`tool/execute` Request:** Server executes the tool, waits for completion, and sends a single JSON-RPC `tool/execute` response in the HTTP response body.

### 2. Stateless Server with Ad-hoc Streaming (e.g., Tool with Progress)

- **`tool/execute` Request:** When the server receives the POST request, it indicates in its HTTP response headers that the response will be an SSE stream.
- The server begins executing the tool.
- It sends multiple `mcp/progress` notifications over the SSE stream while the tool is running.
- When the tool execution completes, the server sends the final JSON-RPC `tool/execute` response (as an SSE event) and then closes the SSE stream.

### 3. Stateful Server (e.g., For Subscriptions or Complex Interactions)

- **`initialize` Request:** Server processes the request, generates a unique session ID, and includes it in its response to the client.
- **Subsequent Client Requests:** The client includes this session ID in the headers of all subsequent HTTP requests to the `/message` endpoint.
- **Server Operation:** The server uses the session ID to retrieve the relevant session context (e.g., active subscriptions, user permissions for that session). This allows for sticky routing in a scaled deployment or for fetching session data from a distributed cache (like Redis).
- Server-to-Client messages (like subscription updates) can be sent over an SSE stream established for that session.

## Why Not WebSocket?

The MCP team considered WebSocket as the primary remote transport but decided against it (for the initial standard) due to:

- **Overhead for Simple RPC:** For simple, stateless tool calls, requiring a WebSocket connection would add unnecessary operational and network overhead.
- **Browser Limitations:** Difficulty in attaching custom headers (like `Authorization`) to WebSocket connections from a browser, and inability for third-party libraries to reimplement WebSocket from scratch in the browser (unlike SSE, which can be polyfilled).
- **Upgrade Complexity:** Only GET requests can be transparently upgraded to WebSocket. Upgrading other methods like POST would require a more complex multi-step process, adding latency.

While WebSocket might be an option in the future, Streamable HTTP was chosen to balance flexibility, compatibility, and ease of implementation for a wide range of server types.

This Streamable HTTP transport is fundamental to making MCP a practical and scalable solution for integrating AI applications with remote tools and data sources.
