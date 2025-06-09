# Hello World JSON-RPC

The **absolute simplest** JSON-RPC example possible.

## What it does

**Request:**
```json
{"jsonrpc": "2.0", "method": "hello", "params": "Alice", "id": 1}
```

**Response:**
```json
{"jsonrpc": "2.0", "result": "Hello, Alice!", "id": 1}
```

## Files

- `json_rpc_models.py` - 2 simple Pydantic classes (10 lines)
- `json_rpc_server.py` - FastAPI server (20 lines)  
- `json_rpc_client.py` - Simple client (25 lines)

## Run it

```bash
# Install
uv add fastapi httpx

# Start server
python json_rpc_server.py

# Run client (new terminal)
python json_rpc_client.py
```

## Output

```
=== Hello World JSON-RPC ===

hello() -> Hello, World!
hello('Alice') -> Hello, Alice!
add([5, 3]) -> 8
unknown() -> Error: Method not found
```

That's it! 🎯
