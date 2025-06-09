import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse, Response

app = FastAPI(title="MCP Simple Tutorial")

def process_method(method: str, params: dict):
    if method == "hello":
        name = params.get("name", "World")
        result = f"Hello, {name}!"
    elif method == "add":
        a = params.get("a", 0)
        b = params.get("b", 0)
        result = a + b
    else:
        result = f"Don't know method: {method}"
    return result

@app.post("/mcp")
async def mcp_post(request: dict):
    """
    Simple POST - send JSON-RPC, get response
    """
    try:
        data = request.get("payload")
        print(f"📤 Got: {data}")
    
        if isinstance(data, list):
            async def stream_batch_response():
                for item in data:
                    print(f"📤 Processing batch item: {item}")
                    if isinstance(item, dict) and "id" in item:
                        method = item.get("method", "unknown")
                        params = item.get("params", {})
                        result = process_method(method, params)
                        response = {
                            "jsonrpc": "2.0",
                            "result": result,
                            "id": item["id"]
                        }
                        yield f"data: {json.dumps(response)}\n\n"
                        await asyncio.sleep(0.1)  # Small delay between batch items
            return StreamingResponse(stream_batch_response(), media_type="text/event-stream")
        # If it has 'id', send back a result
        elif isinstance(data, dict) and "id" in data:
            print(f"📤 Processing individual request: {data}")
            method = data.get("method", "unknown")
            params = data.get("params", {})
            result = process_method(method, params)
            
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": data["id"]
            }
            print(f"📤 Sending response: {response}")
            return JSONResponse(response)
        
        # No 'id' means notification - just accept it
        else:
            return Response(status_code=202)
            
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": f"Bad request: {str(e)}"}, status_code=400)


@app.get("/mcp")
async def mcp_get():
    """
    Simple GET - stream some events
    """
    async def send_events():
        print("📡 Streaming...")
        
        # Send 3 simple events
        for i in range(3):
            event = {
                "jsonrpc": "2.0",
                "method": "update",
                "params": {"count": i + 1, "message": f"Event {i + 1}"}
            }
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(1)
        
        print("📡 Done")
    
    return StreamingResponse(send_events(), media_type="text/event-stream")


@app.get("/")
async def root():
    return {
        "message": "Simple MCP Tutorial",
        "try": {
            "POST /mcp": "Send JSON-RPC messages",
            "GET /mcp": "Get event stream"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Simple MCP Tutorial Server")
    uvicorn.run(app, host="127.0.0.1", port=8000) 