# Streamable HTTP: General Concepts and Model Context Protocol (MCP) Transport

"Streamable HTTP" encompasses a range of techniques and protocol features that allow data to be transmitted over an HTTP connection as a continuous, chunked, or event-driven flow, rather than solely through traditional monolithic request-response cycles. This capability is fundamental for modern applications requiring real-time updates, efficient handling of large datasets, interactive communication, and responsive agentic systems like those envisioned in the Dapr Agentic Cloud Ascent (DACA) framework.

This document first covers general concepts of HTTP streaming. It then delves into the **official Streamable HTTP transport for the Model Context Protocol (MCP) as per the 2025-03-26 specification**, which has replaced older MCP transport mechanisms. Finally, it explores the application of these streaming principles to generic Agent-to-Agent (A2A) communication.

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


```bash
uv init sth
cd sth
uv add "fastapi[standard]"
```

### Example: Generic Streaming Server (FastAPI with Chunked Encoding / Implicit Streaming)

This server demonstrates basic HTTP streaming using FastAPI. It yields data chunks over time, which are sent to the client as they become available using chunked transfer encoding.

**File:** `generic_stream_server.py`

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time
import uvicorn # For running the FastAPI app

app_generic_stream = FastAPI(title="Generic Streaming Server")

async def generic_data_streamer():
    # This generator function implicitly enables chunked transfer encoding
    # if the response length isn't set beforehand.
    for i in range(5):
        data_chunk = f"Timestamp: {time.time()} - Data item {i}\n"
        yield data_chunk # Data is sent as it's yielded
        print(f"Server yielded: {data_chunk.strip()}")
        await asyncio.sleep(1) # Simulate time taken to generate/fetch data
    final_message = f"Timestamp: {time.time()} - End of generic stream.\n"
    yield final_message
    print(f"Server yielded: {final_message.strip()}")

@app_generic_stream.get("/generic-stream")
async def stream_data_endpoint():
    # FastAPI's StreamingResponse with a generator automatically handles chunked encoding.
    return StreamingResponse(generic_data_streamer(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app_generic_stream, host="127.0.0.1", port=8000, log_level="info")
```

**To run this server:**

Run from your terminal: `uv run python generic_stream_server.py`

### Example: Generic Streaming Client (httpx)

This client connects to the generic streaming server and prints the data chunks as they are received.

**File:** `generic_stream_client.py`

```python
import httpx
import asyncio

async def consume_generic_stream():
    print("--- Generic Client: Attempting to connect to generic stream ---")
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", "http://127.0.0.1:8000/generic-stream") as response:
                print(f"Generic Stream Response Status: {response.status_code}")
                response.raise_for_status()

                buffer = ""
                print("Generic Client: Receiving stream...")
                async for chunk in response.aiter_text(): # Process text chunk by chunk
                    # Buffering can be useful if messages are split across chunks
                    # or if you want to process line by line from a continuous text stream.
                    buffer += chunk
                    while "\n" in buffer: # Process complete lines
                        line, buffer = buffer.split("\n", 1)
                        if line: # Ensure the line is not empty
                            print(f"Client received complete line: {line}")
                if buffer: # Print any remaining data in the buffer (if stream doesn't end with newline)
                    print(f"Client received remaining data: {buffer.strip()}")
            print("--- Generic Client: Stream finished ---")
    except httpx.ConnectError as e:
        print(f"--- Generic Client: Connection Error: {e}. Is the server (generic_stream_server.py) running on port 8000? ---")
    except httpx.RequestError as e:
        print(f"--- Generic Client: Request Error during streaming: {e} ---")
    except Exception as e:
        print(f"--- Generic Client: An unexpected error occurred: {e} ---")

if __name__ == "__main__":
    asyncio.run(consume_generic_stream())
```

**To run this client:**

Run from your terminal: `uv run python generic_stream_client.py`

---

## MCP Streamable HTTP Transport (2025-03-26 Specification)

The Model Context Protocol (MCP) defines **Streamable HTTP** as its standard HTTP-based transport mechanism, replacing the older "HTTP+SSE transport" from the 2024-11-05 protocol version. This transport is designed for flexibility, allowing for basic request-response interactions as well as more complex streaming scenarios using Server-Sent Events (SSE) for server-to-client messages.

_(Reference: [MCP Specification - Transports (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http))_

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

### Why MCP Adopted This Streamable HTTP Transport

The MCP 2025-03-26 Streamable HTTP transport was chosen over simpler or older models (like the previous two-endpoint HTTP+SSE) for several reasons:

- **Consolidation and Simplicity**: A single endpoint (`/mcp`) simplifies discovery and interaction for clients compared to managing separate URIs for connection and messaging.

- **Flexibility in Server Responses**: Allowing the server to respond to a client `POST` with either a direct `application/json` object or a `text/event-stream` provides flexibility. Simple requests can get immediate synchronous responses, while complex ones involving multiple steps or server-side processing can leverage SSE for streaming results, notifications, or even server-initiated requests related to the original client `POST`.

- **Clearer Intent for Server-Initiated Streams**: A dedicated client `GET` request to the MCP endpoint has the clear intent of establishing a channel for the server to push messages, independent of any specific client request.

- **Alignment with HTTP Best Practices**: Using standard HTTP methods (`GET`, `POST`, `DELETE`) on a single resource URI (`/mcp`) aligns well with RESTful principles and how modern HTTP APIs are often designed.

- **Standardized Session Management**: Incorporating session management via the `Mcp-Session-Id` header provides a standard way to handle stateful interactions over stateless HTTP.

- **Improved Resilience Features**: Explicitly defining resumability using SSE's `id` and `Last-Event-ID` mechanism enhances robustness.

- **Addressing Limitations of Older Transports**: This model avoids the coordination complexity of the previous two-endpoint HTTP+SSE transport, where clients had to discover the messaging endpoint from an initial SSE event.

### Conceptual Python Implementation (Aligning with MCP 2025-03-26)

Note: These examples are conceptual and simplified. A production implementation would require more robust error handling, security, and adherence to all MUST/SHOULD clauses of the MCP spec.

### Hands-on Python Implementation: MCP Server (2025-03-26 Specification)

This server implements the core logic of the MCP Streamable HTTP Transport (2025-03-26). It handles `POST` and `GET` requests on a single `/mcp` endpoint, manages sessions, and can respond with direct JSON or initiate an SSE stream.

**File:** `mcp_server_2025.py`

```python
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from dataclasses import dataclass
import asyncio
import json
import uvicorn

app = FastAPI(title="MCP Streamable HTTP Server (2025-03-26)")

@dataclass
class MCPConfig:
    endpoint: str = "/mcp"

    @classmethod
    def create(cls):
        """Create default MCP configuration."""
        return cls()

async def process_chunked_stream(request: Request, request_id: str | None = None):
    """Generate chunked stream with JSON-RPC messages."""
    async def stream_generator():
        if request_id:  # POST-initiated stream
            yield json.dumps({
                "jsonrpc": "2.0",
                "method": "StreamNotification",
                "params": {"status": "started"}
            }) + "\n"
            await asyncio.sleep(1)
            yield json.dumps({
                "jsonrpc": "2.0",
                "method": "StreamNotification",
                "params": {"status": "50% complete"}
            }) + "\n"
            await asyncio.sleep(1)
            yield json.dumps({
                "jsonrpc": "2.0",
                "result": {"status": "completed"},
                "id": request_id
            }) + "\n"
        else:  # GET stream
            while not await request.is_disconnected():
                yield json.dumps({
                    "jsonrpc": "2.0",
                    "method": "ServerNotification",
                    "params": {"message": "Server update"}
                }) + "\n"
                await asyncio.sleep(3)

    return StreamingResponse(
        stream_generator(),
        media_type="application/json",
        headers={"Transfer-Encoding": "chunked", "Connection": "keep-alive"}
    )

@app.get("/mcp")
async def mcp_get(request: Request):
    """Handle GET for server-initiated chunked stream."""
    return await process_chunked_stream(request)

@app.post("/mcp")
async def mcp_post(request: Request):
    """Handle POST for client JSON-RPC messages."""
    if not request.headers.get("content-type", "").startswith("application/json"):
        raise HTTPException(status_code=415, detail="Content-Type: application/json required")
    accept = request.headers.get("accept", "")
    if not accept.startswith("application/json"):
        raise HTTPException(status_code=406, detail="Accept: application/json required")

    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    messages = [body] if isinstance(body, dict) else body
    has_requests = any("id" in msg and "method" in msg for msg in messages)

    if not has_requests:
        for msg in messages:
            if msg.get("method") == "update":
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "method": "ServerAck",
                        "params": {"original": msg}
                    }),
                    status_code=202,
                    media_type="application/json"
                )
        return Response(status_code=202, media_type="application/json")

    for msg in messages:
        if "method" in msg and "id" in msg:
            if msg["method"] == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "result": {"serverCapabilities": ["basic"]},
                    "id": msg["id"]
                }
                return Response(content=json.dumps(response), media_type="application/json")
            elif msg["method"] == "echo":
                response = {
                    "jsonrpc": "2.0",
                    "result": {"echo": msg["params"].get("message", "")},
                    "id": msg["id"]
                }
                return Response(content=json.dumps(response), media_type="application/json")
            elif msg["method"] == "start_streaming":
                return await process_chunked_stream(request, msg["id"])

    return Response(
        content=json.dumps({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}}),
        status_code=400,
        media_type="application/json"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
```

The full source code for this comprehensive server is available in the accompanying `10_Streamable_HTTP/sth/mcp_server_2025.py` file. Please refer to it for the complete implementation details. It is designed to run on `http://127.0.0.1:8002`.

**Key functionalities of the comprehensive server (`mcp_server_2025.py`) include:**

- **Advanced Session Management**: Robust handling of `Mcp-Session-Id`, including creation, validation, tracking last active times, and a background task for cleaning up expired sessions.
- **Single MCP Endpoint (`/mcp`)**:
  - `GET`: For establishing dedicated server-to-client SSE streams, requiring `Accept: text/event-stream` and a valid `Mcp-Session-Id`.
  - `POST`: For client-initiated requests and notifications. Handles `InitializeRequest` to create new sessions. Can return immediate JSON responses or switch to an SSE stream for streaming responses based on the request type (e.g., `StartStreamingRequest`).
  - `DELETE`: To terminate an active MCP session.
- **JSON-RPC Compliance**: Strict adherence to JSON-RPC 2.0 for message formatting.
- **Flexible Response Handling**: Capable of returning direct JSON for simple requests or initiating SSE streams for ongoing interactions or server-pushed events.
- **Stream Multiplexing Logic**: Internally manages multiple SSE streams and client requests within a single session.
- **Error Handling**: Provides detailed HTTP error responses for various conditions (e.g., invalid session, incorrect headers, bad JSON).

**To run this comprehensive MCP server:**

Run from your terminal:
```bash
uv run python mcp_server_2025.py
```
The server will start on `http://127.0.0.1:8002`.

### Hands-on Python Implementation: MCP Client (2025-03-26 Specification)

This client demonstrates the full lifecycle of an MCP session using the Streamable HTTP transport: initializing a session, sending requests that might receive JSON or SSE stream responses, listening on a separate GET stream for server-initiated events, and terminating the session.

**File:** `mcp_client_2025.py`

```python
from dataclasses import dataclass
import httpx
import asyncio
import json
import uuid

MCP_SERVER_URL = "http://127.0.0.1:8002/mcp"

@dataclass
class MCPClient:
    base_url: str
    client: httpx.AsyncClient | None = None
    listening: bool = False

    @classmethod
    def create(cls, base_url: str = MCP_SERVER_URL):
        """Create an MCP client with an HTTP client."""
        return cls(base_url=base_url, client=httpx.AsyncClient(timeout=None))

    async def parse_chunked_stream(self, response: httpx.Response, label: str):
        """Parse chunked stream into JSON-RPC messages."""
        buffer = ""
        async for chunk in response.aiter_text():
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:
                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError:
                        print(f"Client: Invalid JSON in chunk: {line}")
                        continue

    async def start(self):
        """Start listening to GET chunked stream with reconnection."""
        self.listening = True
        retries = 0
        max_retries = 3
        while retries < max_retries and self.listening:
            try:
                headers = {"Accept": "application/json"}
                async with self.client.stream("GET", self.base_url, headers=headers) as response:
                    response.raise_for_status()
                    async for message in self.parse_chunked_stream(response, "GET"):
                        if not self.listening:
                            break
                        print(f"Client: GET Message: {json.dumps(message)}")
                    retries = 0
            except httpx.HTTPError as e:
                if not self.listening:
                    print("Client: Stream closed gracefully")
                    break
                print(f"Client: GET error: {e}")
                retries += 1
                if retries < max_retries:
                    await asyncio.sleep(2 ** retries)
                else:
                    print("Client: Max retries reached")
                    self.listening = False

    async def initialize(self):
        """Initialize MCP connection."""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"clientCapabilities": ["basic"]},
            "id": request_id
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            if response.headers.get("content-type") == "application/json":
                data = response.json()
                if data.get("id") == request_id and "result" in data:
                    print("Client: Initialized")
                    return True
            print("Client: Initialization failed")
            return False
        except httpx.HTTPError as e:
            print(f"Client: Initialization error: {e}")
            return False

    async def send_request(self, method: str, params: dict | None = None):
        """Send a JSON-RPC request."""
        request_id = str(uuid.uuid4())
        payload = {"jsonrpc": "2.0", "method": method, "id": request_id}
        if params:
            payload["params"] = params
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            if method == "start_streaming":
                async with self.client.stream("POST", self.base_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for message in self.parse_chunked_stream(response, f"POST_{request_id}"):
                        print(f"Client: POST Message: {json.dumps(message)}")
                        if message.get("id") == request_id and "result" in message:
                            return message["result"]
                    print("Client: No result received from stream")
                    return None
            else:
                response = await self.client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                print(f"Client: JSON Response: {json.dumps(data)}")
                return data.get("result")
        except httpx.HTTPError as e:
            print(f"Client: Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Client: JSON decode error: {e}")
            return None

    async def send_notification(self, method: str, params: dict | None = None):
        """Send a JSON-RPC notification."""
        payload = {"jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            if response.status_code == 202:
                print(f"Client: Notification {method} accepted")
                return True
            print(f"Client: Notification error: {response.status_code}")
            return False
        except httpx.HTTPError as e:
            print(f"Client: Notification error: {e}")
            return False

    async def close(self):
        """Close the client."""
        self.listening = False
        await self.client.aclose()
        print("Client: Closed")

async def main():
    client = MCPClient.create()
    if not await client.initialize():
        print("Failed to initialize")
        return
    task = asyncio.create_task(client.start())
    await asyncio.sleep(1)
    await client.send_request("echo", {"message": "Hello"})
    await client.send_request("start_streaming", {"details": "Stream data"})
    await client.send_notification("update", {"status": "active"})
    await asyncio.sleep(5)
    await client.close()
    await task

if __name__ == "__main__":
    asyncio.run(main())
```

## Why MCP Streamable HTTP Transport Replaced the Older HTTP+SSE Transport

The MCP 2025-03-26 Streamable HTTP transport was chosen over simpler or older models (like the previous two-endpoint HTTP+SSE) for several reasons:

- **Consolidation and Simplicity**: A single endpoint (`/mcp`) simplifies discovery and interaction for clients compared to managing separate URIs for connection and messaging.

- **Flexibility in Server Responses**: Allowing the server to respond to a client `POST` with either a direct `application/json` object or a `text/event-stream` provides flexibility. Simple requests can get immediate synchronous responses, while complex ones involving multiple steps or server-side processing can leverage SSE for streaming results, notifications, or even server-initiated requests related to the original client `POST`.

- **Clearer Intent for Server-Initiated Streams**: A dedicated client `GET` request to the MCP endpoint has the clear intent of establishing a channel for the server to push messages, independent of any specific client request.

- **Alignment with HTTP Best Practices**: Using standard HTTP methods (`GET`, `POST`, `DELETE`) on a single resource URI (`/mcp`) aligns well with RESTful principles and how modern HTTP APIs are often designed.

- **Standardized Session Management**: Incorporating session management via the `Mcp-Session-Id` header provides a standard way to handle stateful interactions over stateless HTTP.

- **Improved Resilience Features**: Explicitly defining resumability using SSE's `id` and `Last-Event-ID` mechanism enhances robustness.

- **Addressing Limitations of Older Transports**: This model avoids the coordination complexity of the previous two-endpoint HTTP+SSE transport, where clients had to discover the messaging endpoint from an initial SSE event.

---

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
