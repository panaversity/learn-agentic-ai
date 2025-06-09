# MCP Hello World Server

A **minimal** example of the Model Context Protocol (MCP) Streamable HTTP transport. This is a "hello world" implementation to learn the basic concepts.

## What This Demonstrates

**Basic MCP Concepts:**
- 📤 **POST /mcp**: Handle JSON-RPC messages (requests and notifications)
- 📡 **GET /mcp**: Stream server events using Server-Sent Events (SSE)

**That's it!** No sessions, no complex features - just the core concepts.

## Quick Start

```bash
# Start the server
uv run python -m mcp_server_mini.main

# In another terminal, test with the client
cd ../mcp-client-mini
uv run python -m mcp_client_mini.client
```

## The Code

### Server (`main.py`)
```python
# POST /mcp - Handle JSON-RPC messages
if "id" in data:  # Request expecting response
    return {"jsonrpc": "2.0", "result": "Hello, World!", "id": data["id"]}
else:  # Notification 
    return Response(status_code=202)

# GET /mcp - Send server events
async def send_events():
    yield f"data: {json.dumps(event)}\n\n"
```

### Client (`client.py`)
```python
# Send POST request
await client.post("http://127.0.0.1:8000/mcp", json=message)

# Listen to GET stream  
async with client.stream("GET", "http://127.0.0.1:8000/mcp") as response:
    async for line in response.aiter_lines():
        # Process events...
```

## Test It

**Manual Testing:**
```bash
# Test POST request
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "hello", "params": {"name": "World"}, "id": 1}'

# Test POST notification  
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "ping"}'

# Test GET stream
curl -X GET http://127.0.0.1:8000/mcp \
  -H "Accept: text/event-stream"
```

## What You'll Learn

1. **JSON-RPC over HTTP**: How to send/receive structured messages
2. **Request vs Notification**: Messages with `id` expect responses, without `id` don't
3. **Server-Sent Events**: How servers can push data to clients
4. **MCP Transport**: The foundation for building AI agent communication

Perfect for understanding the basics before adding sessions, authentication, and other production features!
