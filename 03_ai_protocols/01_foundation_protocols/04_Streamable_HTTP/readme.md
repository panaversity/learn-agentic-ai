# Streamable HTTP: General Concepts and Model Context Protocol (MCP) Transport

**Streamable HTTP** lets you send data over HTTP connections in real-time chunks instead of waiting for complete responses. Think of it like streaming a video (data flows continuously) versus downloading a file (wait for everything). This is essential for modern AI applications that need:

- **Real-time AI responses** (like ChatGPT's typing effect)
- **Large data processing** (handling big datasets without memory issues)  
- **Live agent communication** (AI agents talking to each other instantly)
- **Interactive AI systems** (responsive chatbots, live dashboards)

This streaming approach is core to building scalable AI systems like those in the DACA (Dapr Agentic Cloud Ascent) framework, where thousands of AI agents need to communicate efficiently.

Here we will first covers general concepts of HTTP streaming. It then understand the **official Streamable HTTP transport for the Model Context Protocol (MCP) as per the 2025-03-26 specification**, which has replaced older MCP transport mechanisms. Finally, you will explore the application of these streaming principles to generic Agent-to-Agent (A2A) communication.

---

## General Concepts of Streamable HTTP

While HTTP traditionally operates on a request-response model, many modern use cases demand more dynamic and continuous data exchange. Streamable HTTP techniques address this by enabling data to flow over an HTTP connection as it becomes available or as events occur.

### Common Mechanisms and Techniques:

1.  **Chunked Transfer Encoding**:

    - A standard feature in HTTP/1.1 (and used by HTTP/2 and HTTP/3 under the hood for framing).
    - Allows the server (or client, for request bodies) to send data in a series of "chunks" without needing to know the total content length in advance. The `Transfer-Encoding: chunked` header signals this.
    - The connection remains open, with each chunk prefixed by its size, until a final zero-length chunk is sent to terminate the body.
    - **Impact**: Essential for streaming responses of unknown length (e.g., live log feeds, generating large reports) and for streaming large request bodies (e.g., file uploads) without high memory usage.

2.  **Server-Sent Events (SSE)**:

    - A W3C standard specifically designed for servers to push data unidirectionally (server-to-client) over a single, long-lived HTTP connection.
    - Uses a `text/event-stream` content type and a simple, human-readable event format.
    - Clients (browsers via `EventSource` API, or custom clients) subscribe to an event stream from a server URL.
    - **Impact**: Ideal for real-time notifications, live updates, and scenarios where the server initiates communication after an initial client connection.
    - _SSE is itself a specialized form of streamable HTTP, focusing on server-to-client event push._

3.  **HTTP/2 and HTTP/3 Streaming Capabilities**:

    - **HTTP/2**: Introduced true multiplexing, allowing multiple logical streams (requests and responses) to be interleaved over a single TCP connection without head-of-line blocking at the HTTP application layer. Its binary framing and flow control are inherently suited for streaming.
    - **HTTP/3**: Built on QUIC (which uses UDP), HTTP/3 further enhances streaming by eliminating TCP head-of-line blocking at the transport layer. Each QUIC stream is independent, so packet loss in one stream doesn't stall others.
    - **Impact**: Both HTTP/2 and HTTP/3 provide highly efficient and robust foundations for various streaming patterns, including request streaming, response streaming, and effective bidirectional streaming (though HTTP itself is still fundamentally request-response oriented, these protocols allow for more fluid and concurrent exchanges that feel like streams).

4.  **Long Polling (Simulated Streaming - Less Efficient)**:
    - A technique where the client sends a request, and the server holds it open until new data is available or a timeout occurs. Upon response (or timeout), the client immediately issues a new request.
    - **Impact**: Simulates server push but incurs higher latency and overhead than true streaming mechanisms like SSE or WebSockets. Generally used as a fallback.

### General Use Cases for HTTP Streaming:

- **Live Data Feeds**: Stock tickers, social media updates, news feeds, sports scores.
- **Real-Time Notifications**: Application alerts, status updates, chat messages (though SSE is one-way).
- **Large File Downloads/Uploads**: Streaming data chunks improves perceived performance, reduces memory footprint, and allows for progress indicators.
- **Logging and Monitoring**: Streaming application logs or metrics to a central collector in real time.
- **API Design**: APIs can stream large JSON responses or sequences of JSON objects.

## Tutorial: Using HTTP GET and POST in MCP Streamable HTTP

The **Model Context Protocol (MCP)** specification (revision 2025-03-26) defines **Streamable HTTP** as a transport mechanism for client-server communication using JSON-RPC messages over a single HTTP endpoint (e.g., `https://example.com/mcp`). This tutorial explains how to use the **HTTP POST** and **HTTP GET** methods to send and receive JSON-RPC messages, including how to handle **Server-Sent Events (SSE)** for streaming. It is designed for students learning about web protocols, APIs, or real-time communication.

---

## 1. Overview of MCP Streamable HTTP
MCP Streamable HTTP allows clients and servers to exchange JSON-RPC messages (requests, responses, and notifications) over a single HTTP endpoint. The key methods are:
- **POST**: Used by clients to send JSON-RPC messages (requests, notifications, or responses) to the server.
- **GET**: Used by clients to open an SSE stream, allowing the server to push JSON-RPC requests and notifications to the client.

The single endpoint (e.g., `/mcp`) simplifies communication compared to older approaches that used separate endpoints for initialization and messaging. All JSON-RPC messages must be **UTF-8 encoded**, and the transport supports session management, resumability, and security measures.

---

## 2. Using HTTP POST in MCP Streamable HTTP

### Purpose
The HTTP POST method is the primary way for a client to send JSON-RPC messages to the server. These messages can include:
- **Requests**: Messages expecting a response (e.g., `{"jsonrpc": "2.0", "method": "getData", "id": 1}`).
- **Notifications**: Messages not expecting a response (e.g., `{"jsonrpc": "2.0", "method": "notify", "params": {...}}`).
- **Responses**: Replies to server requests (e.g., `{"jsonrpc": "2.0", "result": {...}, "id": 1}`).
- **Batches**: Arrays containing multiple requests, notifications, or responses.

### How It Works
1. **Client Sends a POST Request**:
   - The client sends a POST request to the MCP endpoint (e.g., `https://example.com/mcp`).
   - The request body contains a single JSON-RPC message or a batch (array) of messages.
   - Required headers:
     - `Accept: application/json, text/event-stream`: Indicates the client can handle a JSON response or an SSE stream.
     - `Mcp-Session-Id: [session-id]`: If the server provided a session ID during initialization, include it in all subsequent POST requests.
   - The body must be UTF-8 encoded.

2. **Server Response**:
   - **If the POST contains only responses or notifications**:
     - If accepted, the server returns **HTTP 202 Accepted** with no body.
     - If not accepted, the server returns an HTTP error (e.g., **400 Bad Request**) with an optional JSON-RPC error response (no `id`).
   - **If the POST contains requests**:
     - The server responds with either:
       - `Content-Type: application/json`: A single JSON object with responses (potentially batched).
       - `Content-Type: text/event-stream`: An SSE stream containing one JSON-RPC response per request, which may be batched. The server may also send JSON-RPC requests or notifications related to the client’s request before sending responses.
     - The server should not close the SSE stream until all responses are sent, unless the session expires.
   - **Disconnection Handling**: If an SSE stream disconnects, it’s not considered a cancellation. To cancel, the client must send an explicit `CancelledNotification`.

3. **Session Management**:
   - If the server provides an `Mcp-Session-Id` during initialization (e.g., in the response to an `InitializeRequest`), the client must include it in the `Mcp-Session-Id` header of all subsequent POST requests.
   - Missing a required `Mcp-Session-Id` results in a **400 Bad Request** response.

4. **Security**:
   - Servers must validate the `Origin` header to prevent DNS rebinding attacks.
   - Servers should use authentication and bind to localhost (127.0.0.1) for local deployments.

### Example: Sending a POST Request
**Scenario**: A client sends a batch of two JSON-RPC requests and one notification to the server.

**Request**:
```http
POST /mcp HTTP/1.1
Host: example.com
Accept: application/json, text/event-stream
Mcp-Session-Id: 123e4567-e89b-12d3-a456-426614174000
Content-Type: application/json

[
  {"jsonrpc": "2.0", "method": "getUser", "params": {"id": 42}, "id": 1},
  {"jsonrpc": "2.0", "method": "updateStatus", "params": {"status": "active"}, "id": 2},
  {"jsonrpc": "2.0", "method": "notifyEvent", "params": {"event": "login"}}
]
```

**Possible Server Responses**:
- **Option 1 (JSON Response)**:
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json

  [
    {"jsonrpc": "2.0", "result": {"name": "Alice"}, "id": 1},
    {"jsonrpc": "2.0", "result": "success", "id": 2}
  ]
  ```
- **Option 2 (SSE Stream)**:
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/event-stream

  data: {"jsonrpc": "2.0", "method": "notifyUpdate", "params": {"update": "status_changed"}}
  data: {"jsonrpc": "2.0", "result": {"name": "Alice"}, "id": 1}
  data: {"jsonrpc": "2.0", "result": "success", "id": 2}
  ```

**Example: POST with Only Notifications**:
**Request**:
```http
POST /mcp HTTP/1.1
Host: example.com
Accept: application/json, text/event-stream
Mcp-Session-Id: 123e4567-e89b-12d3-a456-426614174000
Content-Type: application/json

[{"jsonrpc": "2.0", "method": "notifyEvent", "params": {"event": "logout"}}]
```

**Response** (if accepted):
```http
HTTP/1.1 202 Accepted
```

### Key Points
- POST is used for client-to-server communication, sending JSON-RPC messages.
- The server can respond with a single JSON object or an SSE stream for requests, or a 202 Accepted for notifications/responses.
- Always include the `Mcp-Session-Id` if provided by the server to maintain session continuity.

---

## 3. Using HTTP GET in MCP Streamable HTTP

### Purpose
The HTTP GET method is used by clients to open a **Server-Sent Events (SSE)** stream, allowing the server to push JSON-RPC requests and notifications to the client without the client initiating a request. This is useful for scenarios like real-time updates or server-driven workflows.

### How It Works
1. **Client Sends a GET Request**:
   - The client sends a GET request to the MCP endpoint (e.g., `https://example.com/mcp`).
   - Required headers:
     - `Accept: text/event-stream`: Indicates the client expects an SSE stream.
     - `Mcp-Session-Id: [session-id]`: If the server provided a session ID, include it.
     - `Last-Event-ID: [event-id]`: If resuming a disconnected stream, include the ID of the last received event.
   - No request body is sent, as GET requests typically do not include a body.

2. **Server Response**:
   - The server responds in one of two ways:
     - `Content-Type: text/event-stream`: Initiates an SSE stream, allowing the server to send JSON-RPC requests and notifications (potentially batched), which should be unrelated to concurrent client requests.
     - **HTTP 405 Method Not Allowed**: Indicates the server does not support SSE at this endpoint.
   - The server must not send JSON-RPC responses unless resuming a stream associated with a prior client request (e.g., using `Last-Event-ID`).

3. **Stream Behavior**:
   - The server can send JSON-RPC requests (e.g., asking the client to perform an action) or notifications (e.g., informing the client of an event).
   - The server or client may close the SSE stream at any time.
   - Clients can maintain multiple simultaneous SSE streams, but the server must send each message on only one stream (no broadcasting).

4. **Resumability**:
   - If the SSE stream disconnects, the client can resume by sending a new GET request with the `Last-Event-ID` header, indicating the last event received.
   - The server may replay messages sent after the last event ID on that stream.

5. **Security**:
   - Servers must validate the `Origin` header to prevent DNS rebinding attacks.
   - Authentication and localhost binding (127.0.0.1) are recommended for local servers.

### Example: Opening an SSE Stream with GET
**Scenario**: A client wants to receive server-initiated updates (e.g., notifications about new messages).

**Request**:
```http
GET /mcp HTTP/1.1
Host: example.com
Accept: text/event-stream
Mcp-Session-Id: 123e4567-e89b-12d3-a456-426614174000
```

**Server Response** (if SSE is supported):
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

id: 1
data: {"jsonrpc": "2.0", "method": "notifyMessage", "params": {"message": "New update available"}}

id: 2
data: {"jsonrpc": "2.0", "method": "requestAction", "params": {"action": "refresh"}, "id": 101}
```

**Resuming After Disconnection**:
If the connection drops after receiving event `id: 1`, the client sends:
```http
GET /mcp HTTP/1.1
Host: example.com
Accept: text/event-stream
Mcp-Session-Id: 123e4567-e89b-12d3-a456-426614174000
Last-Event-ID: 1
```

The server may replay events starting after `id: 1`.

**Response if SSE is Not Supported**:
```http
HTTP/1.1 405 Method Not Allowed
```

### Key Points
- GET is used to open an SSE stream for server-to-client communication, typically for server-initiated requests or notifications.
- The client must be prepared to handle SSE events or a 405 error.
- Use `Last-Event-ID` to resume disconnected streams.

---

## 4. Comparing POST and GET
| **Aspect**                | **POST**                                              | **GET**                                              |
|---------------------------|------------------------------------------------------|-----------------------------------------------------|
| **Purpose**               | Send JSON-RPC messages (requests, notifications, responses) to the server | Open an SSE stream for server-to-client JSON-RPC requests and notifications |
| **Headers**               | `Accept: application/json, text/event-stream`, `Mcp-Session-Id` (if provided) | `Accept: text/event-stream`, `Mcp-Session-Id` (if provided), `Last-Event-ID` (for resuming) |
| **Body**                  | JSON-RPC message(s) (single or batched)              | None                                                |
| **Server Response**       | 202 Accepted (for notifications/responses), JSON, or SSE | SSE stream or 405 Method Not Allowed                |
| **Use Case**              | Client-initiated actions (e.g., fetch data, send updates) | Server-initiated updates (e.g., real-time notifications) |

---

## 5. Practical Tips for Implementation
- **For Clients**:
  - Always include the `Accept` header to specify supported response types.
  - Store the `Mcp-Session-Id` from the server’s initialization response and include it in all subsequent POST and GET requests.
  - Handle both JSON and SSE responses for POST requests, and be prepared for 405 errors on GET requests.
  - Implement reconnection logic for SSE streams using `Last-Event-ID` to avoid missing messages.

- **For Servers**:
  - Validate the `Origin` header to enhance security.
  - Support both `application/json` and `text/event-stream` responses for POST requests with JSON-RPC requests.
  - Assign unique, secure `Mcp-Session-Id` values (e.g., UUIDs) for session management.
  - Use event IDs in SSE streams to enable resumability.

---

## 6. Common Pitfalls to Avoid
- **Forgetting Headers**: Omitting `Accept` or `Mcp-Session-Id` headers can lead to errors (e.g., 400 Bad Request).
- **Misinterpreting Disconnections**: Don’t treat SSE stream disconnections as cancellations; use explicit `CancelledNotification` for cancellations.
- **Ignoring Security**: Failing to validate the `Origin` header or implement authentication can expose servers to attacks.
- **Incorrect Response Handling**: Clients must be ready to parse both JSON and SSE responses for POST requests.

---

## 7. Conclusion
The MCP Streamable HTTP transport simplifies client-server communication by using a single endpoint for both POST and GET methods. **POST** enables clients to send JSON-RPC messages, while **GET** allows servers to push updates via SSE streams. Understanding how to structure requests, handle responses, and manage sessions is key to building robust MCP-based applications. Practice with the examples above to get comfortable with these methods!

**Citation**: Based on the MCP specification (revision 2025-03-26), specifically the "Sending Messages to the Server," "Listening for Messages from the Server," and "Session Management" sections under Streamable HTTP, as provided in the document and available at [modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

## MCP Streamable HTTP Transport (2025-03-26 Specification)

The Model Context Protocol (MCP) defines **Streamable HTTP** as its standard HTTP-based transport mechanism, replacing the older "HTTP+SSE transport" from the 2024-11-05 protocol version. This transport is designed for flexibility, allowing for basic request-response interactions as well as more complex streaming scenarios using Server-Sent Events (SSE) for server-to-client messages.

### Why MCP Streamable HTTP Transport Replaced the Older HTTP+SSE Transport?

The MCP 2025-03-26 Streamable HTTP transport was chosen over simpler or older models (like the previous two-endpoint HTTP+SSE) for several reasons:

- **Consolidation and Simplicity**: A single endpoint (`/mcp`) simplifies discovery and interaction for clients compared to managing separate URIs for connection and messaging.

- **Flexibility in Server Responses**: Allowing the server to respond to a client `POST` with either a direct `application/json` object or a `text/event-stream` provides flexibility. Simple requests can get immediate synchronous responses, while complex ones involving multiple steps or server-side processing can leverage SSE for streaming results, notifications, or even server-initiated requests related to the original client `POST`.

- **Clearer Intent for Server-Initiated Streams**: A dedicated client `GET` request to the MCP endpoint has the clear intent of establishing a channel for the server to push messages, independent of any specific client request.

- **Alignment with HTTP Best Practices**: Using standard HTTP methods (`GET`, `POST`, `DELETE`) on a single resource URI (`/mcp`) aligns well with RESTful principles and how modern HTTP APIs are often designed.

- **Standardized Session Management**: Incorporating session management via the `Mcp-Session-Id` header provides a standard way to handle stateful interactions over stateless HTTP.

- **Improved Resilience Features**: Explicitly defining resumability using SSE's `id` and `Last-Event-ID` mechanism enhances robustness.

- **Addressing Limitations of Older Transports**: This model avoids the coordination complexity of the previous two-endpoint HTTP+SSE transport, where clients had to discover the messaging endpoint from an initial SSE event.

---


### Key Characteristics

1.  **Single MCP Endpoint**:
    - The server **MUST** provide a single HTTP endpoint path (e.g., `/mcp`) that supports both `POST` and `GET` methods.
2.  **Sending Messages to the Server (Client `POST`)**:
    - Client sends JSON-RPC messages (single or batch of requests, notifications, or responses) via HTTP `POST` to the MCP endpoint.
    - Client **MUST** include an `Accept` header listing `application/json` and `text/event-stream`.
    - **Server Response to POST**:
      - If client input contains only JSON-RPC _responses_ or _notifications_: Server **MUST** return HTTP `202 Accepted` (no body) if accepted, or an HTTP error otherwise.
      - If client input contains any JSON-RPC _requests_: Server **MUST** return either `Content-Type: application/json` (for a single JSON object response) or `Content-Type: text/event-stream` (to initiate an SSE stream for responses and other messages). The client **MUST** support both.
      - If SSE stream is initiated by server in response to POST:
        - Stream **SHOULD** eventually include one JSON-RPC response per client request.
        - Server **MAY** send related JSON-RPC requests/notifications before the final response(s).
        - Server **SHOULD NOT** close stream before all responses are sent (unless session expires).
        - Server **SHOULD** close stream after all responses.
3.  **Listening for Messages from the Server (Client `GET`)**:
    - Client **MAY** issue an HTTP `GET` to the MCP endpoint to open an SSE stream for server-initiated messages (unrelated to a specific client POST).
    - Client **MUST** include `Accept: text/event-stream`.
    - Server **MUST** return `Content-Type: text/event-stream` or HTTP `405 Method Not Allowed`.
    - If SSE stream initiated by server in response to GET:
      - Server **MAY** send JSON-RPC requests/notifications.
      - Server **MUST NOT** send JSON-RPC responses unless resuming a stream.
      - Server or client **MAY** close stream at any time.
4.  **Session Management**:
    - Server **MAY** assign a session ID via `Mcp-Session-Id` header in the HTTP response to the `InitializeRequest`.
    - Client **MUST** include this `Mcp-Session-Id` header in all subsequent requests for that session.
    - Server **MAY** terminate sessions (responds `404 Not Found` to requests with an old session ID).
    - Client **SHOULD** `DELETE` the MCP endpoint with `Mcp-Session-Id` to terminate a session.
5.  **Resumability (SSE `id` and `Last-Event-ID`)**:
    - Server **MAY** attach an `id` to SSE events for resumability.
    - Client **SHOULD** use `Last-Event-ID` header on `GET` to resume a broken stream. Server **MAY** replay messages.
6.  **JSON-RPC Payloads**: All MCP messages are JSON-RPC 2.0, UTF-8 encoded.

_(Reference: [MCP Specification - Transports (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http))_.

## Further Reading & References

- **MCP Specification**:
  - [MCP Transports (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) (Definitive source for MCP Streamable HTTP)
- **General HTTP Streaming & Concepts**:
  - [MDN Web Docs: Transfer-Encoding (Chunked)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
  - [MDN Web Docs: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) ([Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events))
  - [W3Schools: HTML Server-Sent Events](https://www.w3schools.com/HTML/html5_serversentevents.asp)
  - [Wikipedia: Server-sent_events](https://en.wikipedia.org/wiki/Server-sent_events)
  - [dev.to: How Server-Sent Events (SSE) Work by Zachary Lee](https://dev.to/zacharylee/how-server-sent-events-sse-work-450a)
  - [Medium: Server-Sent Events with Python FastAPI by Nandagopal K](https://medium.com/@nandagopal05/server-sent-events-with-python-fastapi-f1960e0c8e4b)
  - [FastAPI Advanced: StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
  - [httpx Advanced: Streaming Responses](https://www.python-httpx.org/advanced/#streaming-responses/)
- **HTTP/2 and HTTP/3 (Underlying Enablers)**:
  - [Cloudflare: What is HTTP/2?](https://www.cloudflare.com/learning/performance/http2-vs-http1.1/)
  - [Cloudflare: What is HTTP/3?](https://www.cloudflare.com/learning/performance/what-is-http3/)
