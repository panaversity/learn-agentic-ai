# WebSockets

WebSockets is a protocol that enables full-duplex, bidirectional communication between clients and servers over a single, long-lived connection. It is ideal for real-time, interactive applications such as chat, gaming, and collaborative tools.

---

## Working with WebSockets in Python: websockets

- [`websockets`](https://websockets.readthedocs.io/) is the most popular Python library for building WebSocket clients and servers.

### Installation

```bash
pip install websockets
```

### Example 1: Basic WebSocket Server

```python
import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(message)  # Echo back

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server running on ws://localhost:8765")
asyncio.get_event_loop().run_forever()
```

### Example 2: Basic WebSocket Client

```python
import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, WebSocket!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.get_event_loop().run_until_complete(hello())
```

---

## Conceptual Overview

### What is WebSockets?

WebSockets is a protocol that provides persistent, bidirectional communication between a client (usually a browser) and a server. It is designed for real-time, low-latency applications.

### Key Characteristics

- **Full-Duplex:** Both client and server can send messages at any time.
- **Persistent Connection:** Stays open for the duration of the session.
- **Low Latency:** Ideal for real-time updates and interactivity.
- **Works Over HTTP Ports:** Usually runs on port 80/443, so it works through most firewalls.

### Strengths

- **Real-Time:** Enables instant updates and push notifications.
- **Efficient:** Reduces overhead compared to polling.
- **Widely Supported:** Native in all major browsers and many frameworks.

### Weaknesses

- **Stateful:** Requires managing connection state.
- **Scaling:** Can be more complex to scale than stateless HTTP.

### Use Cases in Agentic and Multi-Modal AI Systems

- **Live Collaboration:** Real-time chat, whiteboards, and dashboards.
- **Agent Coordination:** Fast, event-driven communication between agents.
- **IoT:** Device-to-server and device-to-device messaging.

### Place in the Protocol Stack

- **Layer:** Application Layer (OSI Layer 7)
- **Above:** Web apps, agent frameworks
- **Below:** HTTP/1.1, TCP

### Further Reading

- [websockets Documentation](https://websockets.readthedocs.io/)
- [MDN: WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [RFC 6455: The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
