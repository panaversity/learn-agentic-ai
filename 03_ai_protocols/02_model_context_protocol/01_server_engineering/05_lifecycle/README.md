# 05: Connection Lifecycle

**Objective:** Understand the stateful connection lifecycle in MCP, moving beyond simple stateless requests.

For advanced features like notifications, a persistent connection is required. This lesson covers the fundamental handshake: `initialize`, `initialized`, and `shutdown`.

## Key MCP Concepts

-   **Stateful Connection:** Unlike stateless HTTP where each request is independent, a stateful connection involves a session that persists across multiple requests. This is managed via the `MCP-Session-Id` header.
-   **`initialize` (Request):** The very first message a client sends to establish a stateful session. It includes client capabilities and the desired protocol version. The server responds with its capabilities and a unique `session_id`.
-   **`MCP-Session-Id` (Header):** After `initialize`, the client **MUST** include this header with the assigned `session_id` in all subsequent requests for that session.
-   **`initialized` (Notification):** A notification sent from the client to the server *after* `initialize` is complete to confirm that the client is ready to receive notifications.
-   **`shutdown` / `exit`:** The graceful two-part process for ending a session. The client requests a `shutdown`, and after the server acknowledges, the client sends an `exit` notification to terminate the connection.

## Implementation Plan

-   **`server.py`:**
    -   We will use a stateful `FastMCP` server instance (the default).
    -   The library handles the session management automatically. We will add logging to observe lifecycle events.

-   **`client.py`:**
    -   The client will be rewritten to manage the `session_id`.
    -   It will perform the full lifecycle sequence:
        1.  Call `initialize` and store the received `session_id`.
        2.  Send the `initialized` notification.
        3.  Perform an action (like `tools/list`), including the `MCP-Session-Id` header.
        4.  Call `shutdown`.
        5.  Send the `exit` notification.
    -   The client will print its state at each step of the process.

## 🎯 What We're Building

A complete MCP connection lifecycle implementation that demonstrates:

1. **🚀 Initialization Phase** - Capability negotiation and protocol version agreement
2. **⚙️ Operation Phase** - Normal protocol communication  
3. **🛑 Shutdown Phase** - Graceful termination of the connection

This follows the **official MCP 2025-03-26 specification** exactly, ensuring compatibility with all MCP-compliant systems.

## 📋 The Three Phases of MCP Lifecycle

### Phase 1: Initialization 🚀

The initialization phase **MUST** be the first interaction between client and server. During this phase:

- Protocol version compatibility is established
- Capabilities are exchanged and negotiated
- Implementation details are shared

#### Step 1: Initialize Request
The **client** initiates with an `initialize` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "experimental": {},
      "sampling": {}
    },
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

**Key Requirements:**
- The initialize request **MUST NOT** be part of a JSON-RPC batch
- No other requests are possible until initialization completes
- Client **SHOULD NOT** send requests (except pings) before server responds

#### Step 2: Initialize Response
The **server** responds with its capabilities:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "logging": {},
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "weather-server",
      "version": "1.0.0"
    }
  }
}
```

#### Step 3: Initialized Notification
The **client** sends an `initialized` notification to confirm readiness:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

**Important:** Server **SHOULD NOT** send requests (except pings and logging) before receiving this notification.

### Phase 2: Operation ⚙️

During the operation phase, client and server exchange messages according to negotiated capabilities:

- Both parties **MUST** respect the negotiated protocol version
- Only capabilities that were successfully negotiated **SHOULD** be used
- Normal MCP operations (tools, resources, prompts) are now available

### Phase 3: Shutdown 🛑

**Per the MCP Specification**: *"No specific shutdown messages are defined—instead, the underlying transport mechanism should be used to signal connection termination"*

Clean termination of the protocol connection using the underlying transport mechanism:

- **stdio**: Client closes input stream, waits for server exit, sends SIGTERM/SIGKILL if needed  
- **HTTP**: Shutdown indicated by closing HTTP connection(s) - **no JSON-RPC messages needed**

This is **spec-compliant behavior** - the transport layer handles termination, not the protocol layer.

## 🔧 Version Negotiation

### Protocol Version Handling
- Client **MUST** send a supported protocol version (preferably latest: `2025-03-26`)
- Server responds with same version (if supported) or different supported version
- If client doesn't support server's version, it **SHOULD** disconnect

### Version Compatibility
- **`2025-03-26`** - Latest specification with full feature support ✅
- **`2024-11-05`** - Previous version with limited features
- **`draft`** - Development version (not for production)

## 🛠️ Capability Negotiation

### Client Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| `roots` | Filesystem root access | `{ "listChanged": true }`