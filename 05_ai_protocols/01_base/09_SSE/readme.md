# Server-Sent Events (SSE): A Guide to Real-Time Web Communication

Server-Sent Events (SSE) is a simple, efficient, and standard W3C technology that enables servers to push real-time updates to clients over a single, long-lived HTTP connection. Unlike WebSockets, SSE is primarily a one-way communication channel from server to client, making it well-suited for scenarios where the server needs to send continuous data streams or notifications without complex client-side requests.

This document explores the fundamentals of SSE as a general web technology, its core concepts, how to implement it in Python using FastAPI and `httpx`, and its potential applications, particularly in agentic systems like those envisioned by DACA.

---

## Understanding Server-Sent Events (SSE)

SSE allows a web page (or any HTTP client) to get automatic updates from a server via an HTTP connection. Once the connection is established, the server can send data to the client whenever new information is available.

_(References: [MDN Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events), [Wikipedia: Server-sent_events](https://en.wikipedia.org/wiki/Server-sent_events), [W3Schools: HTML Server-Sent Events](https://www.w3schools.com/HTML/html5_serversentevents.asp), [dev.to: How SSE Works](https://dev.to/zacharylee/how-server-sent-events-sse-work-450a))_

### How SSE Works

1.  **Client Initiates Connection**: The client (e.g., a browser using the `EventSource` API or a custom HTTP client like Python's `httpx`) makes a standard HTTP `GET` request to a specific endpoint on the server.
2.  **Server Establishes Persistent Connection**: The server accepts the connection and keeps it open. It responds with a `Content-Type` of `text/event-stream`.
3.  **Server Pushes Events**: The server sends data in a specific plain text format (UTF-8). Each event is a block of text, typically ending with a double newline (`\\n\\n`).
4.  **Client Processes Events**: The client receives these events and processes them. Browser-based `EventSource` APIs automatically handle parsing and reconnection. Custom clients need to implement this logic.

### Key Features

- **Unidirectional (Primarily)**: Data flows from server to client over the SSE connection. Client-to-server communication typically uses separate HTTP requests (e.g., `POST` to a different endpoint).
- **HTTP-Based**: Uses standard HTTP, making it compatible with existing web infrastructure.
- **Automatic Reconnection**: Browser-based `EventSource` clients automatically attempt to reconnect if the connection is lost, using the `retry` field if provided by the server. Custom clients must implement their own reconnection logic.
- **Event Types**: Events can be named, allowing clients to listen for and react to specific types of messages.
- **Text-Based**: Designed for UTF-8 encoded text. Binary data needs encoding (e.g., Base64).

---

## Event Stream Format

The event stream is a simple stream of text data. Messages are generally separated by a double newline.

### MIME Type

The server **MUST** send the `Content-Type: text/event-stream` header.

### Message Structure

Each message can consist of one or more field-value pairs, with each field on a new line:

- `event`: (Optional) A string identifying the type of event. If specified, clients can listen for this specific event type (e.g., `event: user_login`). If omitted, it's a generic `message` event.
- `data`: (Required for most events) The data payload for the event. If a message has multiple `data:` lines, they are concatenated by the client with a newline character in between to form a single data string.
- `id`: (Optional) A unique ID for the event. If the client reconnects, it will send the `Last-Event-ID` HTTP header with the value of the last received ID, allowing the server to potentially resume the stream.
- `retry`: (Optional) An integer specifying the reconnection time in milliseconds for the client.

### Comments

Lines starting with a colon (`:`) are comments and are ignored by the client. They can act as keep-alive pings.

```
: This is a comment

event: user_update
data: {"username": "jane_doe", "status": "active"}
id: event-001

data: This is a multi-line
data: message payload.
id: event-002

retry: 10000
```

A complete event is typically terminated by an empty line (a double newline).

Custom HTTP clients in languages like Python (`httpx`, `requests` with streaming) can also consume SSE streams by handling the `text/event-stream` response and parsing the data line by line.

---

## Python Implementation: SSE Server and Client

The following examples demonstrate a practical SSE setup using Python with FastAPI for the server and `httpx` for the client. This system allows the server to push events and also enables the client to send messages to the server via a separate `POST` request, with the server then acknowledging or responding via SSE.

### Example 1: Runnable Python SSE Server (FastAPI)

This server provides an endpoint (`/sse_stream`) for clients to establish an SSE connection. It assigns a session ID and can push various event types. It also has a `/send_message` endpoint where clients can `POST` data; the server then pushes a "message_receipt" event back to the client via its SSE stream.

```
uv init python_sse
cd python_sse
uv add "fastapi[standard]"
```

**File:** `09_SSE/python_sse/python_sse_server.py`

```python
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import StreamingResponse
from collections import defaultdict
import asyncio
import json
import uuid
import time
import uvicorn
import random

app = FastAPI(title="Simplified SSE Server with Mock AI Agent")

# Store sessions: {session_id: {"queue": asyncio.Queue(), "last_active": float}}
sessions = defaultdict(lambda: {"queue": asyncio.Queue(), "last_active": time.time()})
SESSION_TIMEOUT = 180  # Seconds
MOCK_MESSAGES = [
    "Classifying image X: 80% confidence...",
    "Training model on dataset Y: 50% complete...",
    "Generating response for query Z...",
    "Optimizing parameters for task Q...",
    "Idle: awaiting new tasks..."
]
MOCK_STATUSES = ["processing", "completed", "pending"]

async def sse_stream(session_id: str, request: Request):
    """Generate SSE events for a client session, including mock AI agent messages."""
    async def event_generator():
        # Send connection confirmation
        yield {"event": "connection_confirmation", "data": {"sessionId": session_id, "message": "Connected"}}
        sessions[session_id]["last_active"] = time.time()

        while not await request.is_disconnected():
            try:
                # Wait for queued messages or timeout for mock data
                event = await asyncio.wait_for(sessions[session_id]["queue"].get(), timeout=3.0)
                yield event
                sessions[session_id]["queue"].task_done()
                sessions[session_id]["last_active"] = time.time()
            except asyncio.TimeoutError:
                # Send mock AI agent message
                yield {
                    "event": "ai_agent_message",
                    "data": {
                        "message": random.choice(MOCK_MESSAGES),
                        "agent_id": f"Agent-{random.randint(1, 100):03d}",
                        "timestamp": time.time(),
                        "status": random.choice(MOCK_STATUSES)
                    }
                }
                # Send keep-alive comment
                yield {"event": None, "data": None}
                sessions[session_id]["last_active"] = time.time()

    async def format_sse():
        async for event in event_generator():
            if event["event"] is None:
                yield ":keep-alive\n\n"
            else:
                event_type = event["event"]
                data = json.dumps(event["data"])
                yield f"event: {event_type}\ndata: {data}\n\n"

    if session_id not in sessions:
        sessions[session_id] = {"queue": asyncio.Queue(), "last_active": time.time()}

    return StreamingResponse(
        format_sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/sse_stream")
async def sse_endpoint(request: Request, session_id: str = Query(default_factory=lambda: str(uuid.uuid4()))):
    """SSE endpoint for clients to receive events."""
    return await sse_stream(session_id, request)

@app.post("/send_message")
async def send_message(session_id: str = Query(...), message: str = Query(...)):
    """Receive client message and push SSE confirmation."""
    if session_id not in sessions:
        return Response(content=json.dumps({"error": "Invalid session ID"}), status_code=404)

    await sessions[session_id]["queue"].put({
        "event": "message_receipt",
        "data": {"original_message": message, "timestamp": time.time(), "confirmation": f"Received for {session_id}"}
    })
    sessions[session_id]["last_active"] = time.time()
    return {"status": "Message queued"}

async def cleanup_sessions():
    """Remove inactive sessions periodically."""
    while True:
        await asyncio.sleep(60)
        now = time.time()
        for sid in list(sessions):
            if now - sessions[sid]["last_active"] > SESSION_TIMEOUT:
                del sessions[sid]

@app.on_event("startup")
async def startup():
    asyncio.create_task(cleanup_sessions())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
```

**To run this server:**

3.  Run from your terminal: `uv run python python_sse_server.py`

### Example 2: Runnable Python SSE Client (httpx)

This client connects to the server's `/sse_stream` endpoint. It first receives a `connection_confirmation` event containing its session ID. Then, it can send messages to the server's `/send_message` `POST` endpoint and will receive `message_receipt` events via its active SSE stream. It will also receive periodic mock AI agent messages.

**File:** `09_SSE/python_sse/python_sse_client.py`

```python
from dataclasses import dataclass
import httpx
import asyncio
import json
import time

DEFAULT_SSE_URL = "http://127.0.0.1:8001/sse_stream"
DEFAULT_POST_URL = "http://127.0.0.1:8001/send_message"

async def parse_sse_stream(response: httpx.Response):
    """Parse SSE stream into event dictionaries."""
    current_event = {}
    async for line in response.aiter_lines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(":"):
            yield {"event": "keep_alive", "data": None}
            continue
        if line.startswith("event:"):
            current_event["event"] = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data = json.loads(line[len("data:"):].strip())
            current_event["data"] = data
            yield current_event
            current_event = {}

@dataclass
class SSEClient:
    sse_url: str
    post_url: str
    session_id: str | None = None
    client: httpx.AsyncClient = None
    listening: bool = False

    @classmethod
    def create(cls, sse_url: str = DEFAULT_SSE_URL, post_url: str = DEFAULT_POST_URL) -> 'SSEClient':
        """Create an SSEClient with default or custom URLs and initialize HTTP client."""
        return cls(
            sse_url=sse_url,
            post_url=post_url,
            client=httpx.AsyncClient(timeout=None)
        )

    async def start(self):
        """Start listening to SSE stream."""
        self.listening = True
        try:
            async with self.client.stream("GET", self.sse_url) as response:
                response.raise_for_status()
                async for event in parse_sse_stream(response):
                    if not self.listening:
                        break
                    if event.get("event") == "connection_confirmation":
                        self.session_id = event["data"]["sessionId"]
                        print(f"Received SSE event: Connected, Session ID: {self.session_id}")
                    elif event.get("event") == "message_receipt":
                        print(f"Received SSE event: Server confirmed: {event['data']['confirmation']}")
                    elif event.get("event") == "ai_agent_message":
                        timestamp = time.strftime("%H:%M:%S", time.localtime(event['data']['timestamp']))
                        print(f"Received SSE event: AI Agent [{event['data']['agent_id']}]: {event['data']['message']} (Status: {event['data']['status']}, Time: {timestamp})")
                    elif event.get("event") == "keep_alive":
                        print("Received SSE keep-alive")
        except httpx.HTTPError as e:
            if not self.listening:
                print("SSE stream closed gracefully.")
            else:
                print(f"SSE connection error: {e}")
                self.listening = False

    async def send_message(self, message: str) -> bool:
        """Send message to server via POST."""
        if not self.session_id:
            print("No session ID. Connect first.")
            return False
        try:
            response = await self.client.post(
                f"{self.post_url}?session_id={self.session_id}&message={message}"
            )
            response.raise_for_status()
            print(f"Sent POST message: {response.json()['status']}")
            return True
        except httpx.HTTPError as e:
            print(f"Failed to send POST message: {e}")
            return False

    async def stop(self):
        """Stop listening and clean up."""
        self.listening = False
        await asyncio.sleep(0.1)  # Allow stream loop to exit
        await self.client.aclose()
        print("Client stopped.")

async def main():
    client = SSEClient.create()
    print("Starting SSE client...")
    task = asyncio.create_task(client.start())
    await asyncio.sleep(1)  # Wait for connection
    if client.session_id:
        await client.send_message("Hello, server!")
        await asyncio.sleep(10)  # Run longer to observe AI agent messages
    await client.stop()
    await task

if __name__ == "__main__":
    asyncio.run(main())
```

**To run this client:**

Run from your terminal: `uv run python python_sse_client.py`

---

## General Strengths of SSE

- **Simplicity**: Easier to implement for server-to-client push compared to WebSockets, especially when full bidirectionality isn't needed on the same channel.
- **HTTP-Based**: Works over standard HTTP/1.1 or HTTP/2, avoiding complex firewall configurations sometimes needed for `ws://`.
- **Automatic Reconnection (Browsers)**: `EventSource` API handles dropped connections gracefully. Custom clients need to implement this.
- **Standardized**: A W3C standard with good browser support.
- **Efficiency**: Can be more efficient than polling for server-to-client updates.

---

## General Weaknesses and Considerations of SSE

- **Unidirectional Stream**: The SSE connection itself is for server-to-client data. Client-to-server messages require a separate mechanism (e.g., HTTP POST, as shown in the example).
- **Maximum Connections Limit (HTTP/1.1)**: Browsers typically limit concurrent open HTTP/1.1 connections per domain (around 6). This can be an issue for apps with many SSE streams. HTTP/2 multiplexing largely mitigates this.
- **Proxy/Firewall Buffering**: Some intermediaries might buffer `text/event-stream` responses, delaying or breaking the stream.
- **No Native Binary Support**: SSE is for UTF-8 text. Binary data must be encoded (e.g., Base64).

---

## Server-Sent Events in Generic Agent-to-Agent (A2A) Communication

SSE is a viable technology for certain types of Agent-to-Agent (A2A) communication, especially for unidirectional information push.

### Potential Roles & Use Cases in A2A:

1.  **Notification Streams**: Agent A exposes an SSE endpoint. Agents B and C subscribe to receive real-time notifications or status updates from Agent A (e.g., a monitoring agent streaming health metrics).
2.  **One-Way Data Feeds**: An agent continuously produces data (e.g., market data agent) that other agents consume.
3.  **Log Streaming**: An agent streams its operational logs via SSE to a logging agent or diagnostics UI.

### Complementing SSE for A2A:

Since SSE is server-to-client, if Agent B (client) needs to send commands or data back to Agent A (server), a separate HTTP channel (like a `POST` endpoint on Agent A) is typically used, as demonstrated in the Python examples. Agent A can then correlate the `POST` request (e.g., using a session ID) and push related updates or responses back via the client's SSE stream.

---

## Selection Criteria for SSE in DACA

Within the Dapr Agentic Cloud Ascent (DACA) framework, SSE is a useful tool for specific communication patterns:

**When to Consider SSE for A2A or other DACA components:**

1.  **Primarily Server-to-Client Push Needed**: If the core requirement is for an agent (server) to push updates to other agents or UIs (clients).
2.  **Simplicity for Unidirectional Push**: When a lightweight mechanism is preferred.
3.  **Leveraging HTTP Infrastructure**: Beneficial when working within standard HTTP environments.
4.  **Broadcasting Events**: Ideal for one-to-many event dissemination.

**Considerations for DACA:**

- **Scalability**: Dapr can manage the scalability of agent services exposing SSE endpoints.
- **Resilience**: For custom clients (`httpx`), implement robust reconnection logic.
- **Not for Full Duplex over Single Channel**: For rich, bidirectional, request-response over a single persistent channel where either side can initiate freely, WebSockets or HTTP/2+ patterns might be more direct.
- **Security**: Secure with mTLS (via Dapr) and application-level authentication/authorization.

**In summary for DACA**: SSE is a valuable, simple technology for one-way data push. It's a good choice for A2A notification streams, live data feeds, or any DACA scenario where an agent needs to efficiently push updates to consumers over HTTP, often complemented by a separate client-to-server POST channel for commands or client data submission.

---

## Further Reading & References

- **General SSE**:
  - [MDN Web Docs: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server_sent_events)
  - [Wikipedia: Server-sent_events](https://en.wikipedia.org/wiki/Server-sent_events)
  - [W3Schools: HTML Server-Sent Events](https://www.w3schools.com/HTML/html5_serversentevents.asp)
  - [dev.to: How Server-Sent Events (SSE) Work by Zachary Lee](https://dev.to/zacharylee/how-server-sent-events-sse-work-450a)
  - [HTML Living Standard: Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- **Python Libraries & Examples**:
  - [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
  - [httpx Streaming Responses](https://www.python-httpx.org/advanced/#streaming-responses)
  - [Medium: Server-Sent Events with Python FastAPI by Nandagopal K](https://medium.com/@nandagopal05/server-sent-events-with-python-fastapi-f1960e0c8e4b)