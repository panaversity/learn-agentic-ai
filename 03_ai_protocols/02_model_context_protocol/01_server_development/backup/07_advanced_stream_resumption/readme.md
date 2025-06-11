# 07: Advanced - Stream Resumption

**Objective:** Understand and implement **Stream Resumption** to create a reliable client that doesn't miss messages even if its connection drops.

What happens if an AI agent is connected on a flaky Wi-Fi or cellular network? The connection might drop for a few seconds. If the server sent a critical notification during that time, a simple client would miss it forever.

Stream Resumption is the MCP feature designed to solve this exact problem. It provides a standard way for a client to tell the server, "I got disconnected, please resend any messages I missed."

## Key Concepts for Students

- **Event IDs:** The server is responsible for giving every single message it sends on a stream a unique ID. It sends this in the SSE message itself (e.g., `id: 123`).
- **`Last-Event-ID` Header:** This is the key to the client's side of the process.
    1.  As the client receives messages from the server, it must keep track of the ID of the very last message it successfully received.
    2.  If the connection drops, the client will attempt to reconnect.
    3.  On the reconnection `GET` request, the client includes a new HTTP header: `Last-Event-ID: 123`, where `123` is the ID of the last message it got.
- **Server-Side Replay:** The server must have a short-term memory (a "replay buffer") of the recent messages it has sent to each session. When it sees a `Last-Event-ID` header, it will look in its buffer and resend any messages that came *after* that ID.

## Project Structure

```
07_advanced_stream_resumption/
├── server.py     # A server that tracks sessions, buffers sent messages, and handles the Last-Event-ID header.
└── client.py     # A client that stores the last event ID and simulates a disconnection/reconnection.
```

## How It Will Work

1.  We will have a tool called `send_burst` that rapidly sends several numbered messages to the client.
2.  Our client will connect and start listening, but we will program it to automatically disconnect after receiving just the first few messages.
3.  The client will then wait a second and automatically reconnect.
4.  On its reconnection request, it will include the `Last-Event-ID` header.
5.  The server will receive this, check its buffer, and resend only the messages the client missed. The client will then receive the rest of the messages, proving the resumption was successful. 