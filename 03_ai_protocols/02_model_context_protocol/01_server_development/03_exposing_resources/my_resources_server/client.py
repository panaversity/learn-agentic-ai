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
    """A step-by-step demonstration of interacting with an MCP resource server."""
    print("--- MCP Resource Client Demonstration for Students ---")
    
    # 1. List available resources
    print("\n[Step 1: Discovering Resources]")
    print("We ask the server what resources it has with a 'resources/list' request.")
    resources_response = await _mcp_request("resources/list")
    
    if 'error' in resources_response:
        print(f"   -> Error: {resources_response['error']}")
        return
        
    resources = resources_response.get('result', {}).get('resources', [])
    print(f"   -> Success! Server has {len(resources)} resources:")
    for res in resources:
        print(f"      - {res.get('uri')}: {res.get('description')}")

    # 2. Read the static welcome message
    print("\n[Step 2: Reading a static resource]")
    print("Now, we'll read the 'app:///messages/welcome' resource.")
    read_params = {"uri": "app:///messages/welcome"}
    read_response = await _mcp_request("resources/read", read_params)
    
    if 'error' in read_response:
        print(f"   -> Error: {read_response['error']}")
    else:
        content = read_response.get('result', {}).get('content', [{}])[0].get('text')
        print(f"   -> Success! The server returned: '{content}'")

    # 3. Read the dynamic system time
    print("\n[Step 3: Reading a dynamic resource]")
    print("Next, we'll read 'app:///system/time'. This one is generated on the fly.")
    read_params = {"uri": "app:///system/time"}
    read_response = await _mcp_request("resources/read", read_params)
    
    if 'error' in read_response:
        print(f"   -> Error: {read_response['error']}")
    else:
        content = read_response.get('result', {}).get('content', [{}])[0]
        print(f"   -> Success! The server returned a JSON object:")
        print(f"      {json.dumps(content)}")

    # 4. Read a templated user profile
    print("\n[Step 4: Reading a templated resource]")
    print("Finally, we'll read 'users://jane.doe/profile' to get a specific user's data.")
    read_params = {"uri": "users://jane.doe/profile"}
    read_response = await _mcp_request("resources/read", read_params)
    
    if 'error' in read_response:
        print(f"   -> Error: {read_response['error']}")
    else:
        content = read_response.get('result', {}).get('content', [{}])[0]
        print(f"   -> Success! The server returned the user profile:")
        print(f"      {json.dumps(content)}")

if __name__ == "__main__":
    asyncio.run(main()) 