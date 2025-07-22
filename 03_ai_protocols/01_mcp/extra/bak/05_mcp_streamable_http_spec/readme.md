# Tutorial: Using HTTP GET and POST in MCP Streamable HTTP

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