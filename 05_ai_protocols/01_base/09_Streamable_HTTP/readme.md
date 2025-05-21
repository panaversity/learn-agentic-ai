# Streamable HTTP: General Concepts and MCP Transport

"Streamable HTTP" refers to a collection of techniques and protocols that enable data to be sent over an HTTP connection as a continuous or chunked flow, rather than as a single, monolithic response or request. This is essential for applications requiring real-time updates, efficient handling of large data, or interactive communication.

First, we will cover the general concepts of HTTP streaming, and then we will delve into a specific, newer transport mechanism within the Model Context Protocol (MCP) also referred to as "Streamable HTTP."

---

## General Concepts of Streamable HTTP

HTTP, in its basic form, follows a request-response model. However, many modern applications require more dynamic data exchange. Streamable HTTP techniques address this need.

### Common Mechanisms and Techniques:

1.  **Chunked Transfer Encoding**:

    - A standard feature in HTTP/1.1.
    - Allows the server to send data to the client in a series of "chunks" as it becomes available. The `Transfer-Encoding: chunked` header is used.
    - The connection remains open until the server sends a final zero-length chunk.
    - Useful for responses where the total content length is not known in advance.

2.  **Server-Sent Events (SSE)**:

    - A W3C standard that allows a server to push data to a client unidirectionally (server-to-client) over a single, long-lived HTTP connection.
    - Uses a specific `text/event-stream` content type.
    - Clients (typically browsers with `EventSource` API, or custom clients) subscribe to an event stream from a server URL.
    - SSE is itself a form of streamable HTTP, specialized for server-to-client push.

3.  **Long Polling (Related Concept)**:

    - A technique where the client sends a request to the server, and the server holds the connection open until it has new data to send, or a timeout occurs.
    - If data is sent, the client processes it and immediately sends another request. If it times out, the client immediately reconnects.
    - Simulates a server push but involves repeated client requests. Less efficient than true streaming.

4.  **HTTP/2 and HTTP/3 Streaming Capabilities**:
    - HTTP/2 introduced multiplexing, allowing multiple requests and responses to be interleaved over a single TCP connection without head-of-line blocking at the HTTP level. Its binary framing and flow control mechanisms are inherently well-suited for streaming.
    - HTTP/3, built on QUIC (UDP), further enhances these capabilities, mitigating TCP head-of-line blocking.

### General Use Cases:

- **Live Data Feeds**: Stock tickers, social media updates, sports scores.
- **Real-Time Notifications**: Alerts, application status updates.
- **Large File Downloads/Uploads**: Streaming data chunks can improve perceived performance and reduce memory footprint.
- **Logging and Monitoring**: Streaming logs from applications to a central collector.

### Example: Generic Streaming Server (FastAPI with Chunked Encoding)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time

app = FastAPI()

async def generic_data_streamer():
    for i in range(10):
        yield f"Data item {i}\n" # Data is sent as it's yielded
        await asyncio.sleep(0.5)
    yield "End of stream.\n"

@app.get("/generic-stream")
async def stream_data():
    # FastAPI by default uses chunked transfer encoding for StreamingResponse
    # if content length is not known.
    return StreamingResponse(generic_data_streamer(), media_type="text/plain")

# To run: uvicorn generic_stream_server:app --reload
# Access via: http://127.0.0.1:8000/generic-stream
```

### Example: Generic Streaming Client (httpx)

```python
import httpx
import asyncio

async def consume_generic_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://127.0.0.1:8000/generic-stream") as response:
            print(f"Generic Stream Response Status: {response.status_code}")
            async for chunk in response.aiter_text(): # or aiter_bytes()
                print(f"Received chunk: {chunk.strip()}")

if __name__ == "__main__":
    asyncio.run(consume_generic_stream())
# To run: python generic_stream_client.py (ensure server is running)
```

---

## Streamable HTTP (within Model Context Protocol - MCP)

In the context of the Model Context Protocol (MCP), "Streamable HTTP" refers to a newer, evolving transport mechanism designed to streamline real-time communication between MCP clients and servers. It aims to improve upon the older Server-Sent Events (SSE) based transport by simplifying endpoints and leveraging HTTP capabilities more directly. This approach is crucial for agentic systems requiring efficient, low-latency data exchange for tasks like tool calls and notifications.

Based on discussions and developments in the MCP community (e.g., [GitHub Issue #220 on MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk/issues/220)), this MCP-specific transport exhibits distinct characteristics:

### Key Characteristics of MCP's Streamable HTTP Transport

1.  **Single `/message` Endpoint**: Unlike the older MCP SSE transport that used separate endpoints for connection (`GET`) and messaging (`POST`), the Streamable HTTP transport typically consolidates these. All client-to-server messages (JSON-RPC payloads) are routed through the `/message` endpoint, usually via `POST` requests.
2.  **Server-Upgraded SSE for Notifications & Server-Initiated Requests**: The stream from the server to the client (for notifications or other server-initiated messages) is established typically by the client making an initial `GET` request to the `/message` endpoint. The server then "upgrades" this connection to an SSE stream (`text/event-stream`).
3.  **Client-Initiated Streams**: Clients initiate the SSE stream by sending an empty `GET` request to the `/message` endpoint.
4.  **Session IDs for State Management**: Session IDs are used to manage the state of individual connections, allowing a server to handle multiple clients and streams concurrently.
5.  **JSON-RPC Payloads**: As with other MCP transports, the actual data exchanged (both client-to-server and server-to-client over the SSE stream) consists of JSON-RPC messages.

This design aims to simplify the server implementation and align more closely with standard HTTP practices while still providing robust streaming capabilities for MCP.

### Conceptual Python Implementation for MCP Streamable HTTP

While a dedicated Python library for this specific "MCP Streamable HTTP" transport might not be as established as for the TypeScript SDK, one can implement the server and client logic using standard Python HTTP libraries like `FastAPI` (server-side) and `httpx` (client-side).

The core idea is to handle POST requests for client messages and GET requests to establish an SSE stream on the same `/message` endpoint.

#### Example: Conceptual MCP Streamable HTTP Server (FastAPI)

This example outlines how a FastAPI server might be structured for MCP's Streamable HTTP. Error handling, robust session management, and full MCP message processing would need to be more comprehensive in a production system.

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
import uuid # For session IDs

app_mcp_server = FastAPI(title="MCP Streamable HTTP Server")

# In-memory store for active client streams (simplified session management)
active_mcp_streams = {}

async def mcp_specific_event_stream(session_id: str):
    # Simulate sending MCP notifications or server-initiated messages
    # In a real MCP server, these would be actual JSON-RPC messages
    try:
        count = 0
        while True:
            if session_id not in active_mcp_streams:
                print(f"MCP Session {session_id} closed by server logic.")
                break

            message_data = {
                "jsonrpc": "2.0",
                "method": "notifications/message", # Example MCP notification
                "params": {"level": "info", "data": f"MCP Server message {count} to {session_id}"}
            }
            yield f"data: {json.dumps(message_data)}\n\n" # SSE format
            count += 1
            await asyncio.sleep(2) # Send a message every 2 seconds
    except asyncio.CancelledError:
        print(f"MCP Stream for session {session_id} was cancelled.")
    finally:
        if session_id in active_mcp_streams:
            del active_mcp_streams[session_id]
        print(f"Closed MCP stream for session {session_id}")

@app_mcp_server.get("/message") # MCP Streamable HTTP: GET to /message for SSE stream
async def get_mcp_stream_endpoint(request: Request): # Renamed function
    session_id = str(uuid.uuid4())
    print(f"MCP Client connected, starting SSE stream for session_id: {session_id}")
    active_mcp_streams[session_id] = True # Mark stream as active
    return StreamingResponse(mcp_specific_event_stream(session_id), media_type="text/event-stream")

@app_mcp_server.post("/message") # MCP Streamable HTTP: POST to /message for client JSON-RPC messages
async def post_mcp_message_endpoint(request: Request): # Renamed function
    try:
        # Session ID might be passed in headers or as a query parameter for POST
        # For simplicity, not strictly enforced here for POST in this example
        mcp_json_rpc_payload = await request.json()
        print(f"Received MCP JSON-RPC message: {mcp_json_rpc_payload}")

        # Process the MCP message (e.g., tool call)
        response_payload = {
            "jsonrpc": "2.0",
            "id": mcp_json_rpc_payload.get("id"),
            "result": {"message": "MCP Payload received and processed (simulated)"}
        }
        return response_payload
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload for MCP")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run this (save as mcp_streamable_http_server.py):
# uvicorn mcp_streamable_http_server:app_mcp_server --reload --port 8001
# (Using a different port to avoid conflict with generic server if run together)
```

#### Example: Conceptual MCP Streamable HTTP Client (httpx)

This client demonstrates initiating the MCP-specific SSE stream and sending a POST message.

```python
import httpx
import asyncio
import json

MCP_SERVER_URL = "http://127.0.0.1:8001/message" # Assuming server runs on port 8001

async def consume_mcp_specific_stream():
    print("--- MCP Client: Attempting to connect for SSE stream ---")
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", MCP_SERVER_URL) as response:
                print(f"--- MCP Client: SSE Stream Response Status: {response.status_code} ---")
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"): # SSE data line
                        try:
                            mcp_notification = json.loads(line[len("data:"):])
                            print(f"MCP Client received notification: {mcp_notification}")
                        except json.JSONDecodeError:
                            print(f"MCP Client received non-JSON data: {line}")
                    elif line:
                        print(f"MCP Client received SSE line: {line}")
    except httpx.RequestError as e:
        print(f"--- MCP Client: Error connecting or streaming: {e} ---")
    except Exception as e:
        print(f"--- MCP Client: An unexpected error occurred: {e} ---")

async def send_mcp_specific_tool_call():
    print("\n--- MCP Client: Sending tool_call POST message ---")
    tool_call_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "mcp_example_tool", "arguments": {"arg1": "value1"}},
        "id": "mcp-client-req-123"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MCP_SERVER_URL, json=tool_call_payload)
            response.raise_for_status()
            print(f"MCP Client POST response: {response.json()}")
    except httpx.RequestError as e:
        print(f"MCP Client POST error: {e}")

async def mcp_client_main(): # Renamed main function
    stream_task = asyncio.create_task(consume_mcp_specific_stream())
    await asyncio.sleep(2) # Wait for stream to establish
    await send_mcp_specific_tool_call()
    await asyncio.sleep(10) # Keep receiving stream messages
    stream_task.cancel()
    try:
        await stream_task
    except asyncio.CancelledError:
        print("--- MCP Client: Stream task cancelled. ---")

if __name__ == "__main__":
    # To distinguish from generic client if run in same context
    # asyncio.run(mcp_client_main())
    print("MCP Client conceptual code. Run mcp_client_main() to test with MCP server.")
    # Example of how to run it:
    # import asyncio
    # asyncio.run(mcp_client_main())
```

### Differences from Classic MCP SSE Transport

- **Endpoints**: Classic SSE for MCP often uses two endpoints: one (e.g., `/connect` or `/events`) for establishing the SSE stream via `GET`, and another (e.g., `/messages` or `/rpc`) for client-to-server `POST` requests containing JSON-RPC messages. MCP's Streamable HTTP typically uses a single `/message` endpoint for both.
- **Initialization**: In MCP's Streamable HTTP, the client `GET`s `/message` to start the stream. In the older model, the server might send an initial `endpoint` event on the SSE stream itself to tell the client where to `POST` messages.

### Strengths (Potential, for MCP's Streamable HTTP)

- **Simplified Routing**: A single endpoint can simplify server logic and infrastructure configuration for MCP interactions.
- **Alignment with HTTP Semantics**: Leverages standard GET for streaming and POST for actions in a consolidated manner.
- **Reduced Overhead**: Potentially less handshake complexity compared to the older two-endpoint SSE model for MCP.

### Weaknesses/Considerations (for MCP's Streamable HTTP)

- **Maturity and Standardization within MCP**: As a newer approach within MCP, tooling and Python-specific library support might be less mature than for the classic SSE transport or other general streaming protocols like WebSockets.
- **Complexity in Session Management**: Ensuring reliable session management and state synchronization across GET (stream) and POST (message) interactions on a single endpoint requires careful server-side design.
- **Proxy/Firewall Issues**: Like any streaming HTTP, it can be affected by intermediaries that buffer or mishandle long-lived connections or SSE specific headers/content types.

### Use Cases in DACA (for MCP's Streamable HTTP)

Given its design for MCP, this Streamable HTTP transport is directly applicable to DACA for:

- **Real-time Agent Notifications**: Agents receiving updates, alerts, or partial results from tools or other agents.
- **Streaming Tool Outputs**: Tools that produce data over time (e.g., code execution logs, long-running process monitoring) can stream results back to an agent.
- **Interactive Agent Communication**: While the primary stream is server-to-client, the ability for the client to send POST messages to the same endpoint facilitates responsive interactions.
- **Efficient Transport for MCP**: Serves as an efficient HTTP-based transport for the JSON-RPC messages that form the core of MCP communication.

### Place in the Protocol Stack (for MCP's Streamable HTTP)

- **Layer**: Application Layer (OSI Layer 7), specifically as an MCP transport.
- **Above**: MCP SDKs, Agent Frameworks, Agent Business Logic.
- **Below**: HTTP (typically HTTP/1.1 or HTTP/2).

---

## Further Reading & References

- **General HTTP Streaming**:
  - [MDN Web Docs: Chunked transfer encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
  - [MDN Web Docs: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
  - [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
  - [httpx Streaming Responses](https://www.python-httpx.org/advanced/#streaming-responses)
- **MCP Specific Streamable HTTP**:
  - [GitHub Issue: Support for "Streamable HTTP" Transport (MCP TypeScript SDK #220)](https://github.com/modelcontextprotocol/typescript-sdk/issues/220) - Provides key insights into this transport.
  - The official Model Context Protocol specification documents (if updated with details on this transport).
  - [MCP Server and Client with SSE & The New Streamable HTTP!](https://medium.com/@itsuki.enjoy/mcp-server-and-client-with-sse-the-new-streamable-http-d860850d9d9d) (This article primarily discusses the classic SSE transport but hints at newer streamable HTTP concepts in MCP).
