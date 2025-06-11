# 06: Advanced - Session Management

**Objective:** Understand and implement stateful **Session Management** as defined by the MCP specification.

In all previous tutorials, our server was "stateless." It had no memory. Every request was a brand new interaction. This is simple, but limited. What if we want a server that remembers a user's conversation history, or keeps a running count of how many times they've called a tool?

This is where session management comes in. It's the mechanism that allows a server to identify and maintain a unique context for each connected client.

## Key Concepts for Students

- **Stateful Server:** Unlike our previous examples, this server will have a memory. We will create a simple Python dictionary to store data for each session.
- **`Mcp-Session-Id` Header:** This is the key to the whole process.
    1.  When a client connects for the first time, the server will generate a unique ID (a UUID) for it.
    2.  The server sends this ID back to the client in an HTTP header called `Mcp-Session-Id`.
    3.  The client **must** then store this ID and include it in the `Mcp-Session-Id` header of every subsequent request it makes.
- **Session Context:** By using the session ID as a key into its memory (our dictionary), the server can retrieve the correct context for any incoming request. This allows it to "remember" what happened in previous requests from that specific client.

## Project Structure

```
06_advanced_session_management/
├── server.py     # A stateful server that creates and manages sessions.
└── client.py     # A client that correctly handles receiving and sending the session ID.
```

## How It Will Work

1.  The client will send its first request without a session ID.
2.  The server will see there's no ID, create a new session in its memory, generate a UUID, and send it back in a response header.
3.  The client will extract the `Mcp-Session-Id` from the response headers.
4.  For all future requests, the client will add the `Mcp-Session-Id` to its request headers.
5.  We will have a tool called `increment_counter`. Each time a client calls it, the server will use the session ID to find that client's specific counter in its memory and increment it, proving that the state is being maintained correctly across multiple requests. 