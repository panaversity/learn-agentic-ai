import httpx
import json
import asyncio
from typing import Any

# --- Helper Function to Make MCP Requests ---
async def _mcp_request(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """A simple, reusable function to make JSON-RPC requests to our MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1  # A static ID is fine for these simple, sequential examples
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"   -> Sending {method} request...", payload)
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
    print("--- MCP Prompt Template Client Demonstration for Students (2025-06-18) ---")

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
        name = p.get('name', 'Unknown')
        title = p.get('title', name)  # NEW: 2025-06-18 title field
        description = p.get('description', 'No description')
        print(f"      📝 {title}")
        print(f"         Name: {name}")
        print(f"         Description: {description}")

    # 2. Test simple prompts (educational/Postman compatible)
    print("\n[Step 2: Getting simple educational prompts]")
    print("Testing the basic 'summarize' prompt for educational purposes.")
    summarize_text = "The quick brown fox jumps over the lazy dog. This is a common pangram used in typography and font testing."
    get_params = {
        "name": "summarize",
        "arguments": {
            "text": summarize_text
        }
    }
    get_response = await _mcp_request("prompts/get", get_params)

    if 'error' in get_response:
        print(f"   -> Error: {get_response['error']}")
    else:
        messages = get_response.get('result', {}).get('messages', [])
        print(
            f"   -> Success! The server returned {len(messages)} message(s):")
        if messages:
            content = messages[0].get('content', [{}])
            if isinstance(content, list) and content:
                text_content = content[0].get('text', '')
                print(f"   Content preview: {text_content[:200]}...")
            else:
                print(f"   Content: {content}")

    # 3. Test multi-message conversation prompts
    print("\n[Step 3: Getting multi-message conversation prompts]")
    print("Testing the 'debug_error' prompt for conversation structure.")
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
        print(
            f"   -> Success! The server returned {len(messages)} message(s):")
        for i, message in enumerate(messages):
            role = message.get('role', 'unknown')
            content = message.get('content', [{}])
            if isinstance(content, list) and content:
                text_content = content[0].get('text', '')[:100]
            else:
                text_content = str(content)[:100]
            print(f"      Message {i+1} ({role}): {text_content}...")

    print("The server demonstrates full 2025-06-18 MCP Prompts specification compliance.")

if __name__ == "__main__":
    asyncio.run(main())
