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
    """A step-by-step demonstration of interacting with an MCP prompt server."""
    print("--- MCP Prompt Template Client Demonstration for Students ---")
    
    # 1. List available prompts
    print("\n[Step 1: Discovering Prompt Templates]")
    print("We ask the server what prompt templates it has with a 'prompts/list' request.")
    prompts_response = await _mcp_request("prompts/list")
    
    if 'error' in prompts_response:
        print(f"   -> Error: {prompts_response['error']}")
        return
        
    prompts = prompts_response.get('result', {}).get('prompts', [])
    print(f"   -> Success! Server has {len(prompts)} prompt templates:")
    for p in prompts:
        print(f"      - {p.get('name')}: {p.get('description')}")

    # 2. Get the 'summarize' prompt
    print("\n[Step 2: Getting a simple text prompt]")
    print("Now, we'll get the 'summarize' prompt for a piece of text.")
    summarize_text = "The quick brown fox jumps over the lazy dog."
    get_params = {"name": "summarize", "arguments": {"text": summarize_text}}
    get_response = await _mcp_request("prompts/get", get_params)
    
    if 'error' in get_response:
        print(f"   -> Error: {get_response['error']}")
    else:
        # The result is a list of ChatML messages
        messages = get_response.get('result', {}).get('messages', [])
        print(f"   -> Success! The server returned a list with {len(messages)} message(s):")
        print(json.dumps(messages, indent=2))

    # 3. Get the 'debug_error' prompt
    print("\n[Step 3: Getting a multi-message conversation prompt]")
    print("Finally, let's get the 'debug_error' prompt to start a conversation.")
    debug_params = {
        "name": "debug_error", 
        "arguments": {
            "error_message": "TypeError: 'NoneType' object is not iterable",
            "code_snippet": "for item in get_data():\n  process(item)"
        }
    }
    get_response = await _mcp_request("prompts/get", debug_params)
    
    if 'error' in get_response:
        print(f"   -> Error: {get_response['error']}")
    else:
        messages = get_response.get('result', {}).get('messages', [])
        print(f"   -> Success! The server returned a list with {len(messages)} message(s):")
        print(json.dumps(messages, indent=2))


if __name__ == "__main__":
    asyncio.run(main()) 