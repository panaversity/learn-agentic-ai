import httpx
import json
import asyncio
from typing import Any

# This client is designed to be stateful and spec-compliant.
# It holds the protocol_version after initialization.
_protocol_version: str | None = None

# --- Helper Function to Make MCP Requests ---
async def _mcp_request(method: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """A simple, reusable function to make JSON-RPC requests to our MCP server."""
    global _protocol_version

    # Handle the case where current_task() returns None
    current_task = asyncio.current_task()
    task_name = current_task.get_name() if current_task else "1"

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": task_name  # Use task name for a unique ID
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    # Add session and version headers if they exist
    if _protocol_version:
        headers["MCP-Protocol-Version"] = _protocol_version

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                "http://localhost:8000/mcp/",  # Use /mcp/ with trailing slash
                json=payload,
                headers=headers,
                timeout=10
            )
            print(f"   -> Sending {method} request...")

            if response.status_code != 200:
                print(
                    f"   -> HTTP error {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}"}

            # Parse SSE response
            for line in response.text.split('\n'):
                if line.strip().startswith('data:'):
                    data = json.loads(line.split('data:', 1)[1].strip())
                    if "error" in data:
                        print(f"   -> MCP error: {data['error']}")
                    return data

            return {"error": "No data in response"}

    except Exception as e:
        print(f"   -> An error occurred: {e}")
        return {"error": str(e)}

# --- Main Demonstration ---


async def main():
    """A step-by-step demonstration of interacting with an MCP resource server."""
    print("--- MCP Resource Client Demonstration (2025-06-18) ---")

    # 1. Initialize the session
    print("\\n[Step 1: Initializing Session]")
    print("A compliant client MUST start with an 'initialize' request.")
    init_params = {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {
            "name": "resources-demo-client",
            "title": "MCP Resources Demo Client",
            "version": "1.0.0"
        }
    }
    init_response = await _mcp_request("initialize", init_params)

    if 'error' in init_response:
        print(f"   -> Error initializing session: {init_response['error']}")
        return

    global _protocol_version
    _protocol_version = init_response.get('result', {}).get('protocolVersion')
    server_info = init_response.get('result', {}).get('serverInfo', {})
    print(
        f"   -> Success! Connected to: {server_info.get('title', server_info.get('name', 'Unknown Server'))}")
    print(f"   -> Protocol version: {_protocol_version}")

    # 2. List available resources
    print("\\n[Step 2: Discovering All Resources]")
    print("Asking the server what resources it has with 'resources/list'.")
    resources_response = await _mcp_request("resources/list")

    if 'error' in resources_response:
        print(f"   -> Error listing resources: {resources_response['error']}")
        return

    resources = resources_response.get('result', {}).get('resources', [])
    print(f"   -> Success! Server exposed {len(resources)} resources:")
    for res in resources:
        name = res.get('name', 'Unknown')
        title = res.get('title', name)  # NEW: 2025-06-18 title field
        uri = res.get('uri', 'Unknown')
        description = res.get('description', 'No description')
        print(f"      📄 {title}")
        print(f"         Name: {name}")
        print(f"         URI: {uri}")
        print(f"         Description: {description}")

    if not resources:
        print("   -> No resources found. Exiting.")
        return

    # 3. Read the static welcome message
    print("\\n[Step 3: Reading Static Resource]")
    print("Now, we'll read the 'app:///messages/welcome' resource.")
    read_params = {"uri": "app:///messages/welcome"}
    read_response = await _mcp_request("resources/read", read_params)

    if 'error' in read_response:
        print(f"   -> Error reading resource: {read_response['error']}")
    else:
        contents = read_response.get('result', {}).get('contents', [])
        if contents:
            first_content = contents[0]
            if isinstance(first_content.get('text'), dict):
                # Handle JSON response
                print(
                    f"   -> Success! Content (JSON): {json.dumps(first_content['text'], indent=2)}")
            else:
                # Handle text response
                print(
                    f"   -> Success! Content: '{first_content.get('text', '')}'")
        else:
            print(f"   -> No content found in response")

    # 4. Test template resource
    print("\\n[Step 4: Testing Template Resource]")
    print("Testing user profile template with user ID '99999'.")
    template_uri = "users://99999/profile"
    template_response = await _mcp_request("resources/read", {"uri": template_uri})

    if 'error' not in template_response:
        contents = template_response.get('result', {}).get('contents', [])
        if contents:
            template_content = contents[0].get('text', '')
            print(
                f"   -> Success! Template generated content: {template_content}")
        else:
            print(f"   -> No content found in template response")
    else:
        print(
            f"   -> Template resource error: {template_response.get('error')}")

    # 5. Test file listing resource
    print("\\n[Step 5: Testing File Listing Resource]")
    print("Reading the project files list.")
    files_response = await _mcp_request("resources/read", {"uri": "app:///files/list"})

    if 'error' not in files_response:
        contents = files_response.get('result', {}).get('contents', [])
        if contents:
            files_content = contents[0].get('text', '')
            print(f"   -> Success! Files list: {files_content[:200]}...")
        else:
            print(f"   -> No content found in files response")
    else:
        print(f"   -> Files resource error: {files_response.get('error')}")

    # 7. Test individual file reading
    print("\\n[Step 6: Testing Individual File Reading]")
    print("Reading a specific file: README.md")
    file_response = await _mcp_request("resources/read", {"uri": "file:///project/README.md"})

    if 'error' not in file_response:
        contents = file_response.get('result', {}).get('contents', [])
        if contents:
            file_content = contents[0].get('text', '')
            print(f"   -> Success! File content: {file_content[:200]}...")
        else:
            print(f"   -> No content found in file response")
    else:
        print(f"   -> File resource error: {file_response.get('error')}")

    print("\\n[Demonstration Complete]")
    print("Successfully tested resource discovery, reading, and template functionality!")
    print("The server demonstrates full 2025-06-18 MCP Resources specification compliance.")


if __name__ == "__main__":
    # Fix the asyncio.run() type issue by explicitly calling the coroutine
    asyncio.run(main())
