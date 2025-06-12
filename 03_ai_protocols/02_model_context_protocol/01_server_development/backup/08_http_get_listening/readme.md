# 05: Listening for Server Events with HTTP GET

**Objective:** Understand how to use `HTTP GET` to create a client that receives real-time, server-initiated messages.

In the previous examples, the client always started the conversation by sending a `POST` request. This module demonstrates the reverse: the server pushing a notification to a client that is actively listening. This is a powerful pattern for building reactive, event-driven AI systems where the AI needs to be told that something new has happened.

## Key Concepts for Students

- **Server-Sent Events (SSE):** This is the web technology that allows a server to send updates to a client over a single, long-lived `HTTP GET` connection. It's a one-way street: server-to-client.
- **The Listening Client (`GET`):** Our client will make a `GET` request to the server and just... wait. The connection stays open, and the client is ready to receive any message the server decides to send.
- **The Triggering Action (`POST`):** To make the server send a message, something has to happen. In our example, the client itself will also make a `POST` request to a special tool (`send_notification`) whose only job is to tell the server to broadcast a message to all listening clients.
- **Concurrency with `asyncio.gather`:** To make this easy to see in one script, we will use Python's `asyncio` library to run two functions at the same time: one function to listen, and one function to trigger the event.

## Project Structure

```
05_http_get_listening/
├── server.py     # The server that manages listeners and sends notifications
└── client.py     # A SINGLE client that both listens AND triggers the event
```

## 1. The Server Code (`server.py`)

The server code is more complex here because it has to be *stateful*—it must keep track of all currently connected listeners. We've added detailed comments to the code to explain how it uses a simple list to manage listeners and a custom `GET` handler to manage the SSE connections.

## 2. The Simplified Client (`client.py`)

This is the key to the simplified example. This one script performs both roles:
1.  The `listen_for_events()` function connects to the server and waits.
2.  The `trigger_event()` function waits 3 seconds, then calls the `send_notification` tool on the server.
3.  The `main()` function runs both of these at the same time using `asyncio.gather`.

## 3. How to Run: A Step-by-Step Guide

You only need two terminals for this much-simpler example.

### **Terminal 1: Start the Server**

1.  **Navigate to the directory:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/05_http_get_listening
    ```
2.  **Install libraries:** (If you haven't already)
    ```bash
    uv add httpx mcp uvicorn
    ```
3.  **Run the server:**
    ```bash
    uvicorn server:mcp_app --host 0.0.0.0 --port 8000
    ```
    You will see the server start. It is now waiting for connections.

### **Terminal 2: Run the Client**

1.  **Navigate to the *same* directory as Terminal 1:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/05_http_get_listening
    ```
2.  **Run the client:**
    ```bash
    python client.py
    ```

## 4. What Happens When You Run

This is where you'll see the cause-and-effect clearly.

**First, in Terminal 2 (Client), you will see:**
```
--- HTTP GET / Server-Sent Events Demonstration ---
[Listener]: Connecting to server to listen for events...
[Trigger]:  Will call 'send_notification' tool in 3 seconds to trigger an event...
```

**Then, in Terminal 1 (Server), you will see it react to the connection:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Server: New listener connected. Total listeners: 1
INFO:     127.0.0.1:xxxxx - "GET /mcp/ HTTP/1.1" 200 OK
```

**After 3 seconds, the client triggers the event. In Terminal 2 (Client), you will see:**
```
[Trigger]:  ===> Event triggered successfully on the server!
```

**The server (Terminal 1) reacts to the `POST` call and broadcasts the message:**
```
Server: Received request to send notification: 'Hello listeners, from the trigger!'
Server: Broadcasting to 1 listeners...
INFO:     127.0.0.1:xxxxx - "POST /mcp/ HTTP/1.1" 200 OK
```

**Finally, the listener on the client (Terminal 2) receives the broadcast and prints it:**
```
[Listener]: <<<=== Received a notification from the server!
{
  "jsonrpc": "2.0",
  "method": "app/notification",
  "params": {
    "type": "broadcast_message",
    "content": "Hello listeners, from the trigger!"
  }
}

--- Demonstration complete ---
```
This shows the full, round-trip, event-driven flow that is possible with MCP's HTTP transport. 