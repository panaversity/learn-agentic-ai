import asyncio
import json
import httpx


async def test_get_stream():
    """Learn: Basic GET streaming (MCP SSE)"""
    print("📡 Testing GET Stream")
    
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://127.0.0.1:8000/mcp") as response:
            print("Stream opened...")
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: "
                    event = json.loads(data)
                    print(f"Event: {event}")


async def test_post_request():
    """Learn: POST JSON-RPC request"""
    print("\n📤 Testing POST Request")
    
    async with httpx.AsyncClient() as client:
        # Send proper JSON-RPC request
        message = {
            "jsonrpc": "2.0",
            "method": "hello",
            "params": {"name": "Alice"},
            "id": 1
        }
        print(f"Sending: {message}")
        
        response = await client.post("http://127.0.0.1:8000/mcp", json={"payload": message})
        result = response.json()
        print(f"Response: {result}")


async def test_post_notification():
    """Learn: POST JSON-RPC notification"""
    print("\n📢 Testing POST Notification")
    
    async with httpx.AsyncClient() as client:
        # Send notification (no 'id' field)
        message = {
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {"timestamp": "now"}
        }
        print(f"Sending: {message}")
        
        response = await client.post("http://127.0.0.1:8000/mcp", json={"payload": message})
        print(f"Status: {response.status_code}")


async def test_post_batch_request():
    """Learn: POST JSON-RPC batch request"""
    print("\n📤 Testing POST Batch Request")
    
    async with httpx.AsyncClient() as client:
        # Send batch request
        message = [
            {
                "jsonrpc": "2.0",
                "method": "hello",
                "params": {"name": "Alice"},
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "hello",
                "params": {"name": "Bob"},
                "id": 2
            }
        ]
        print(f"Sending: {message}")
        
        async with client.stream("POST", "http://127.0.0.1:8000/mcp", json={"payload": message}) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: "
                    event = json.loads(data)
                    print(f"Event: {event}")


async def main():
    """Learn MCP streaming concepts"""
    print("🎯 MCP Streaming Tutorial")
    print("=" * 30)
    print("📚 Learning: JSON-RPC over HTTP + SSE")
    print()
    
    try:
        await test_post_batch_request()
        await test_post_request()
        await test_post_notification()
        await test_get_stream()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 