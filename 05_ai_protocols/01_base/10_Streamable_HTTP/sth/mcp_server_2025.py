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