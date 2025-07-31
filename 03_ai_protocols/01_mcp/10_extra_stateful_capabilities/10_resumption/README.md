# 🔄 10: MCP Connection Resumption

> **Analogy:** Imagine you're on a long phone call, and the signal drops. When you call back, instead of starting the whole conversation over, your friend says, "You cut out right after you said..." and you pick up exactly where you left off. That's MCP Resumption. It lets a client seamlessly continue a session after a network interruption without losing its place.

This lesson demonstrates how to build a fault-tolerant client that can survive a connection drop and resume a long-running operation by using the `Last-Event-ID` header.

## 🎯 What You Will Learn

-   **Server-Side**: How to use an `EventStore` to buffer messages, enabling the server to replay them for a reconnecting client.
-   **Client-Side**: How to persist the session state (session ID and last event ID) and use it to resume a broken connection.
-   **Protocol-Level**: How a client sends the `mcp-session-id` and `Last-Event-ID` headers to initiate a resumption, and how the server uses this information to bring the client up to date.
-   **Interactive Testing**: How to simulate a connection drop and successful resumption using Postman.

## ✨ The "Cross-Stream Replay" Concept

The MCP specification is strict: `The server MUST NOT replay messages that would have been delivered on a different stream.` However, for this educational example, our `InMemoryEventStore` takes a more powerful (but less compliant) approach: it replays messages from **all** streams associated with the session.

This "cross-stream replay" allows the client to resume a tool call even if the final result is delivered on a different logical stream than the initialization. It's a powerful pattern for building resilient systems, and we've included it here to show you what's possible.

## 🚀 How to Run This Example

You can test resumption using either the simplified Python client or the Postman collection.

### 1. Start the Server

First, start the MCP server. It has a tool (`get_forecast`) with an intentional 6-second delay to make it easy to simulate a timeout.

```bash
# In your terminal, from the 10_resumption directory
uv run uvicorn server:mcp_app --reload
```

### 2. Run the Python Client (Two-Step Process)

The Python client simulates a crash and restart. You'll run it twice.

**First Run (Simulates the "Crash"):**

```bash
# This run will connect, start the tool call, and then "crash"
# before the server finishes. It saves its state in `.session_cache`.
uv run client.py
```

You will see it initialize and then exit.

**Second Run (Simulates the "Resumption"):**

```bash
# Run the exact same command again.
# The client will find the .session_cache file, reconnect with the
# old session ID and last event ID, and instantly get the result.
uv run client.py
```

### 3. Use the Postman Collection

For a more hands-on approach, use the included Postman collection.

1.  **Import the Collection**: Import `postman/MCP_Resumption_Tests.postman_collection.json` into Postman.
2.  **Follow the `README.md`**: Open the collection's documentation in Postman (or read `postman/POSTMAN_README.md`) for detailed, step-by-step instructions. The flow is designed to be run in order to simulate the session drop and successful resumption.
