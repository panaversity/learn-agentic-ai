# MCP Streaming Tutorial Client

A **minimal** Python client that demonstrates MCP Streamable HTTP concepts. Learns JSON-RPC over HTTP with Server-Sent Events.

## What This Does

Three MCP concepts:
1. 📤 **POST Request**: Send JSON-RPC request, get response
2. 📢 **POST Notification**: Send JSON-RPC notification (no response expected)  
3. 📡 **GET Stream**: Listen to Server-Sent Events from server

## Quick Start

```bash
# Make sure the server is running first
cd ../server-mini
uv run python main.py

# Then run the client
uv run python client.py
```

## Expected Output

```
🎯 MCP Streaming Tutorial
==============================
📚 Learning: JSON-RPC over HTTP + SSE

📤 Testing POST Request
Sending: {'jsonrpc': '2.0', 'method': 'hello', 'params': {'name': 'Alice'}, 'id': 1}
Response: {'jsonrpc': '2.0', 'result': 'Hello, Alice!', 'id': 1}

📢 Testing POST Notification
Sending: {'jsonrpc': '2.0', 'method': 'ping', 'params': {'timestamp': 'now'}}
Status: 202

📡 Testing GET Stream
Stream opened...
Event: {'jsonrpc': '2.0', 'method': 'update', 'params': {'count': 1, 'message': 'Event 1'}}
Event: {'jsonrpc': '2.0', 'method': 'update', 'params': {'count': 2, 'message': 'Event 2'}}
Event: {'jsonrpc': '2.0', 'method': 'update', 'params': {'count': 3, 'message': 'Event 3'}}
```

## The Code

Core MCP concepts in ~50 lines:

```python
# JSON-RPC Request (has 'id')
message = {"jsonrpc": "2.0", "method": "hello", "params": {"name": "Alice"}, "id": 1}
response = await client.post("http://127.0.0.1:8000/mcp", json=message)

# JSON-RPC Notification (no 'id')
message = {"jsonrpc": "2.0", "method": "ping", "params": {"timestamp": "now"}}
response = await client.post("http://127.0.0.1:8000/mcp", json=message)

# Server-Sent Events Stream
async with client.stream("GET", "http://127.0.0.1:8000/mcp") as response:
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            event = json.loads(line[6:])  # Remove "data: " prefix
```

## What You Learn

1. **JSON-RPC Format**: The standard message structure for MCP
2. **Request vs Notification**: Messages with `id` expect responses, without `id` don't
3. **SSE Protocol**: How to process server-sent event streams
4. **MCP Transport**: How AI agents communicate over HTTP

Perfect foundation for building AI agent communication systems! 🤖
