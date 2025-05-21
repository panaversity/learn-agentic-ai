# JSON-RPC: The Payload Format for Model Context Protocol (MCP)

JSON-RPC is a lightweight, stateless remote procedure call (RPC) protocol encoded in JSON. Within the Model Context Protocol (MCP), **JSON-RPC 2.0 is the mandatory payload format for all messages exchanged between MCP clients and servers.** This applies regardless of the underlying transport mechanism being used (e.g., stdio, the classic SSE transport, or the newer Streamable HTTP transport).

Its simplicity, human-readability (due to JSON), and language agnosticism make it an excellent choice for defining the structure of requests, responses, and notifications in a standardized way for agentic systems.

---

## Role of JSON-RPC in MCP

In MCP:

1.  **Requests**: Clients send JSON-RPC request objects to servers to invoke methods (e.g., list available tools, call a specific tool).
    - A `method` string (e.g., `tools/list`, `tools/call`).
    - A `params` object or array containing arguments for the method.
    - An `id` (string, number, or null) that is used to correlate responses with requests. If `id` is omitted or null, it signifies a notification.
2.  **Responses**: Servers send JSON-RPC response objects back to clients after processing a request.
    - A `result` field containing the outcome if the method call was successful.
    - An `error` object if the method call failed.
    - The same `id` as the corresponding request object.
3.  **Notifications**: Either party (client or server) can send JSON-RPC notification objects. These are requests without an `id` field, meaning no response is expected.
    - Example: Server sending a `notifications/tools/list_changed` or `notifications/message` to the client.

All these objects are serialized as JSON strings when sent over the chosen MCP transport.

---

## Standard JSON-RPC 2.0 Structure

### Request Object

```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": [42, 23],
  "id": 1
}
```

Or with named parameters:

```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": { "subtrahend": 23, "minuend": 42 },
  "id": 3
}
```

### Notification Object (Request without `id`)

```json
{
  "jsonrpc": "2.0",
  "method": "update",
  "params": [1, 2, 3, 4, 5]
}
```

### Response Object (Success)

```json
{
  "jsonrpc": "2.0",
  "result": 19,
  "id": 1
}
```

### Response Object (Error)

```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32601, "message": "Method not found" },
  "id": "1"
}
```

Common JSON-RPC error codes include:

- `-32700 Parse error`: Invalid JSON was received by the server.
- `-32600 Invalid Request`: The JSON sent is not a valid Request object.
- `-32601 Method not found`: The method does not exist / is not available.
- `-32602 Invalid params`: Invalid method parameter(s).
- `-32603 Internal error`: Internal JSON-RPC error.
- `-32000 to -32099 Server error`: Reserved for implementation-defined server-errors.

---

## Common MCP JSON-RPC Examples

Below are conceptual examples of JSON-RPC messages as they might be used in MCP.

### 1. List Tools (Client Request)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": "client-req-001"
}
```

### 2. List Tools (Server Response)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "calculator/add",
        "description": "Adds two numbers.",
        "inputSchema": {
          "type": "object",
          "properties": { "a": { "type": "number" }, "b": { "type": "number" } }
        }
      },
      {
        "name": "weather/get_forecast",
        "description": "Gets the weather forecast for a location.",
        "inputSchema": {
          "type": "object",
          "properties": { "location": { "type": "string" } }
        }
      }
    ]
  },
  "id": "client-req-001"
}
```

### 3. Call Tool (Client Request)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "calculator/add",
    "arguments": { "a": 5, "b": 7 }
  },
  "id": "client-req-002"
}
```

### 4. Call Tool (Server Response - Success)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{ "type": "text", "text": "The sum is 12." }]
  },
  "id": "client-req-002"
}
```

### 5. Tool List Changed (Server Notification)

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
  // No "id" field signifies a notification
}
```

### 6. Logging Message (Server Notification)

As seen in the Medium article ([MCP Server and Client with SSE & The New Streamable HTTP!](https://medium.com/@itsuki.enjoy/mcp-server-and-client-with-sse-the-new-streamable-http-d860850d9d9d)) on MCP with SSE:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/message",
  "params": { "level": "info", "data": "First greet to itsuki" }
}
```

---

## Working with JSON-RPC Payloads in Python

While specific MCP SDKs handle the creation and parsing of these JSON-RPC messages, you can work with them directly using Python's built-in `json` library for serialization/deserialization and a library like `requests` (for client-side HTTP) or `FastAPI` (for server-side HTTP) to send/receive them.

The `json-rpc` library (and `jsonrpcserver`) can also be helpful for stricter validation and dispatching on the server side if you are building an MCP server component from scratch.

### Example: Creating and Sending an MCP-like JSON-RPC Request (Client with `requests`)

```python
import requests
import json

# Assume server_messaging_url is the MCP server's message endpoint
# (e.g., http://localhost:8000/message for Streamable HTTP,
# or the URI received via an endpoint event for classic SSE)
server_messaging_url = "http://localhost:8000/mcp_message_endpoint" # Placeholder

def call_mcp_tool(tool_name: str, arguments: dict, request_id: str):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": request_id
    }
    headers = {"Content-Type": "application/json"}

    print(f"Sending MCP tool call: {json.dumps(payload)}")
    try:
        response = requests.post(server_messaging_url, json=payload, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        response_data = response.json()
        print(f"Received MCP response: {response_data}")
        return response_data
    except requests.exceptions.HTTPError as errh:
        print(f"  Http Error: {errh}")
        try: print(f"  Response Content: {response.json()}") # Try to print JSON error from server
        except json.JSONDecodeError: print(f"  Response Content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"  Request Error: {err}")
    return None

if __name__ == "__main__":
    # This is a conceptual client call; it requires a running MCP server at server_messaging_url
    # that understands this "tools/call" method.
    # Replace server_messaging_url with the actual one from your MCP server setup.

    # Example usage:
    # result = call_mcp_tool(
    #     tool_name="calculator/add",
    #     arguments={"a": 10, "b": 5},
    #     request_id="my-tool-call-001"
    # )
    # if result and "result" in result:
    #     print(f"Tool call successful. Result: {result['result']}")
    # elif result and "error" in result:
    #     print(f"Tool call failed. Error: {result['error']}")
    print("Conceptual client call. Ensure an MCP server is running and configured.")
```

### Example: Receiving and Parsing an MCP-like JSON-RPC Request (Server with `FastAPI`)

```python
from fastapi import FastAPI, Request, HTTPException
import json # For types, though FastAPI handles auto-parsing

app = FastAPI()

@app.post("/mcp_message_endpoint") # Example MCP message endpoint
async def handle_mcp_message(request: Request):
    try:
        payload = await request.json() # FastAPI automatically parses JSON
    except json.JSONDecodeError: # Should be caught by FastAPI, but as example
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}

    print(f"Received payload: {payload}")

    if payload.get("jsonrpc") != "2.0" or "method" not in payload:
        return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": payload.get("id")}

    method = payload["method"]
    params = payload.get("params", {})
    request_id = payload.get("id")

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments")
        print(f"Server: Processing tool_call for '{tool_name}' with args: {tool_args}")
        # Actual tool call logic would go here
        # ...
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": f"Tool '{tool_name}' called successfully (simulated)."}]},
            "id": request_id
        }
    elif method == "tools/list":
        # Actual tool listing logic
        return {
            "jsonrpc": "2.0",
            "result": {"tools": [{"name": "example/tool", "description": "An example tool."}]},
            "id": request_id
        }
    # Handle other MCP methods...
    else:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}

# To run (save as mcp_payload_server.py):
# uvicorn mcp_payload_server:app --reload
```

---

## Strengths of using JSON-RPC in MCP

- **Simplicity & Readability**: JSON is human-readable and easy to parse, aiding debugging and development.
- **Lightweight**: Minimal overhead compared to more verbose formats like XML (used in SOAP).
- **Interoperability**: Widely supported across programming languages and platforms.
- **Clear Structure for RPC**: Provides a well-defined way to express method calls, parameters, results, and errors.
- **Supports Notifications**: Allows for fire-and-forget messages crucial for asynchronous updates.

## Weaknesses/Considerations

- **Schema and Typing**: JSON itself is schema-less. MCP addresses this by defining expected schemas for tool inputs/outputs and other specific messages, but validation is a layer above JSON-RPC itself.
- **No Built-in Security or Transport Features**: JSON-RPC is only a payload format. Security (authentication, authorization, encryption) and transport reliability must be handled by the underlying MCP transport (stdio, HTTP with TLS, etc.) and the MCP implementation.
- **Error Handling Specificity**: While standard error codes exist, detailed application-specific error information needs to be structured within the `error.data` field or by using the reserved server error code range.

## Use Cases in DACA (Agentic AI Systems)

As the core payload format for MCP, JSON-RPC is fundamental to nearly all interactions within a DACA system that uses MCP:

- **Agent-Tool Communication**: Defining requests to call tools and responses from tools.
- **Agent-Server/-Orchestrator Communication**: Agents listing available tools, receiving configurations, or reporting status.
- **Inter-Agent Communication (if using MCP)**: If agents communicate with each other via MCP, JSON-RPC will format their messages.
- **Event Notifications**: For agents to receive asynchronous updates (e.g., a tool becoming available/unavailable, a long-running task completing).

## Place in the Protocol Stack

- **Layer**: Presentation Layer (OSI Layer 6) in terms of data formatting, used within the Application Layer (OSI Layer 7) protocol (MCP).
- **Above**: Agent logic, tool implementations, MCP framework logic.
- **Below**: MCP Transport Protocols (stdio, SSE, Streamable HTTP), which in turn run over TCP/IP, UDP (for QUIC-based transports if ever used by MCP), etc.

---

## Further Reading

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) (Official Specification)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/) (For how MCP uses JSON-RPC)
- Python Libraries:
  - [`json` module (built-in)](https://docs.python.org/3/library/json.html)
  - [`json-rpc` library](https://pypi.org/project/json-rpc/)
  - [`jsonrpcserver` library](https://jsonrpcserver.readthedocs.io/en/latest/)
- [MCP Server and Client with SSE & The New Streamable HTTP!](https://medium.com/@itsuki.enjoy/mcp-server-and-client-with-sse-the-new-streamable-http-d860850d9d9d) (Illustrates JSON-RPC messages in MCP SSE context).
