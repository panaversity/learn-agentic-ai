import httpx
import json
import asyncio
from typing import Any

async def _mcp_request(method: str, params: dict[str, Any] | None = None):
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

    try:
        async with httpx.AsyncClient() as client, client.stream(
            "POST", "http://localhost:8000/mcp/", json=payload, headers=headers, timeout=10
        ) as response:
            print(f"   -> Sending {method} request...")
            response.raise_for_status()

            # The stateless transport sends back a stream of newline-delimited JSON objects.
            # We iterate through the response line by line.
            async for line in response.aiter_lines():
                if line:  # Skip empty lines
                    print(f"   <- Received raw data: {line}")
                    if line.startswith("data: "):
                        line = line[6:]
                        print(f"   <- Received data: {line}")
                        return json.loads(line)

            return {"error": "No data received in the response stream."}
    except Exception as e:
        print(f"   -> An error occurred: {e}")
        return {"error": str(e)}

async def main():
    print("\n[Step 1: Ask the server what it can do]")
    print("We send a 'tools/list' request to discover available tools.")
    tools_response = await _mcp_request("tools/list")
    
    print("\nRESULT OF TOOLS: ", tools_response)

if __name__ == "__main__":
    asyncio.run(main())
