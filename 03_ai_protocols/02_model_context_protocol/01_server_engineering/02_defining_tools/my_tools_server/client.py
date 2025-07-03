import httpx
import json
import asyncio

# --- Helper Function to Make MCP Requests ---
async def _mcp_request(method: str, params: dict = None):
    """A simple, reusable function to make JSON-RPC requests to our MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1 # A static ID is fine for these simple, sequential examples
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"   -> Sending {method} request...")
            response = await client.post("http://localhost:8000/mcp/", json=payload, headers=headers)
            response.raise_for_status()
            # The server sends back SSE, so we parse it to get the JSON data
            for line in response.text.strip().split('\n'):
                if line.startswith('data: '):
                    return json.loads(line[6:])
            return {"error": "No data found in SSE response"}
        except Exception as e:
            print(f"   -> An error occurred: {e}")
            return {"error": str(e)}

# --- Main Demonstration ---
async def main():
    """A step-by-step demonstration of interacting with an MCP tool server."""
    print("--- MCP Tool Client Demonstration for Students ---")
    
    # 1. List available tools
    print("\n[Step 1: Discovering Tools]")
    print("We ask the server what tools it has with a 'tools/list' request.")
    tools_response = await _mcp_request("tools/list")
    
    if 'error' in tools_response:
        print(f"   -> Error listing tools: {tools_response['error']}")
        return
        
    tools = tools_response.get('result', {}).get('tools', [])
    print(f"   -> Success! Server has {len(tools)} tools:")
    for tool in tools:
        print(f"      - {tool.get('name')}: {tool.get('description')}")

    # 2. Call the 'add' tool
    print("\n[Step 2: Calling the 'add' tool]")
    print("Now, we'll call the 'add' tool with numbers 5 and 7.")
    add_params = {"name": "add", "arguments": {"a": 5, "b": 7}}
    add_response = await _mcp_request("tools/call", add_params)
    
    if 'error' in add_response:
        print(f"   -> Error calling 'add': {add_response['error']}")
    else:
        result = add_response.get('result', {}).get('content', [{}])[0].get('text')
        print(f"   -> Success! The server returned the result: '{result}'")

    # 3. Call the 'greet' tool
    print("\n[Step 3: Calling the 'greet' tool]")
    print("Finally, we'll call the 'greet' tool with the name 'Student'.")
    greet_params = {"name": "greet", "arguments": {"name": "Student"}}
    greet_response = await _mcp_request("tools/call", greet_params)
    
    if 'error' in greet_response:
        print(f"   -> Error calling 'greet': {greet_response['error']}")
    else:
        result = greet_response.get('result', {}).get('content', [{}])[0].get('text')
        print(f"   -> Success! The server returned the greeting: '{result}'")

if __name__ == "__main__":
    asyncio.run(main()) 