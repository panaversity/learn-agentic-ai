import httpx
import asyncio
import json

async def main():
    """A working MCP client that correctly handles initialization and tool calls."""
    print("--- Hello MCP World: A Working Client ---")
    
    # MCP endpoint
    url = "http://localhost:8000/mcp/"
    
    # Step 1: Initialize the MCP server with proper parameters
    print("\n[Step 1: Initialize the MCP server]")
    
    # Proper initialization parameters according to MCP spec
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",  # Supported MCP protocol version
            "capabilities": {
                "experimental": {},
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    async with httpx.AsyncClient() as client:
        print("   -> Sending initialize request...")
        response = await client.post(url, json=init_payload, headers=headers)
        response.raise_for_status()
        
        print(f"   -> Response status: {response.status_code}")
        print(f"   -> Response headers: {dict(response.headers)}")
        
        # Check if we got SSE or JSON response
        content_type = response.headers.get("content-type", "")
        session_id = response.headers.get("mcp-session-id")
        
        if session_id:
            print(f"   -> Session ID: {session_id}")
            headers["mcp-session-id"] = session_id
        
        # Parse response based on content type
        if content_type.startswith("text/event-stream"):
            print("   -> Received SSE response")
            # Parse SSE format: "event: message\ndata: {json}\n\n"
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    print(f"   -> Initialize result: {data}")
                    break
        else:
            print("   -> Received JSON response")
            data = response.json()
            print(f"   -> Initialize result: {data}")
    
    # Step 2: Send initialized notification
    print("\n[Step 2: Send initialized notification]")
    
    initialized_payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    
    async with httpx.AsyncClient() as client:
        print("   -> Sending initialized notification...")
        response = await client.post(url, json=initialized_payload, headers=headers)
        print(f"   -> Response status: {response.status_code}")
        
        # This might return 202 Accepted for notifications
        if response.status_code == 202:
            print("   -> Notification acknowledged")
        
    # Step 3: List available tools
    print("\n[Step 3: List available tools]")
    
    list_tools_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        print("   -> Requesting tools list...")
        response = await client.post(url, json=list_tools_payload, headers=headers)
        response.raise_for_status()
        
        # Parse response
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("text/event-stream"):
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"   -> Available tools: {data}")
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        for tool in tools:
                            print(f"      - {tool['name']}: {tool['description']}")
                    break
        else:
            data = response.json()
            print(f"   -> Available tools: {data}")
    
    # Step 4: Call the weather tool
    print("\n[Step 4: Call the weather tool]")
    
    call_tool_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_forecast",
            "arguments": {
                "city": "New York"
            }
        },
        "id": 3
    }
    
    async with httpx.AsyncClient() as client:
        print("   -> Calling get_forecast tool...")
        response = await client.post(url, json=call_tool_payload, headers=headers)
        response.raise_for_status()
        
        # Parse response
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("text/event-stream"):
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"   -> Tool result: {data}")
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content']
                        for item in content:
                            if item.get('type') == 'text':
                                print(f"   -> Weather forecast: {item['text']}")
                    break
        else:
            data = response.json()
            print(f"   -> Tool result: {data}")

if __name__ == "__main__":
    asyncio.run(main()) 