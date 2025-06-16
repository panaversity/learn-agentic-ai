# Stream Resumption

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
