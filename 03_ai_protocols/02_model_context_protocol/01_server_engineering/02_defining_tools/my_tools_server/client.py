import httpx
import json
import asyncio
from typing import TypeVar

# This client is designed to be stateful and spec-compliant.
# It holds the protocol_version after initialization.
_protocol_version: str | None = None

T = TypeVar("T")

# --- Helper Function to Make MCP Requests ---
async def _mcp_request(method: str, params: dict[str, T] | None = None) -> T | None:
    """A simple, reusable function to make JSON-RPC requests to our MCP server."""
    global _protocol_version
    print(f"   -> Sending {method} request..." )

    # Generate a unique ID for the request
    current_task = asyncio.current_task()
    request_id = current_task.get_name() if current_task else "unknown"

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    # Add version headers if they exist
    if _protocol_version:
        headers["MCP-Protocol-Version"] = _protocol_version

    try:
        async with httpx.AsyncClient() as client, client.stream(
            "POST", "http://localhost:8000/mcp/", json=payload, headers=headers, timeout=10
        ) as response:
            print(f"   -> Sending {method} request...")

            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.strip().startswith("data:"):
                    return json.loads(line.split("data:", 1)[1].strip())

            return None

    except Exception as e:
        print(f"   -> An error occurred: {e}")
        return {"error": str(e)}

# --- Main Demonstration ---


async def main():
    """A step-by-step demonstration of interacting with an MCP tool server."""
    print("--- MCP Tool Client Demonstration ---")

    # 1. Initialize the session
    print("\n[Step 1: Initializing Session]")
    print("A compliant client MUST start with an 'initialize' request.")
    init_params = {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {
            "name": "tools-demo-client",
            "title": "MCP Tools Demo Client",
            "version": "1.0.0"
        }
    }
    init_response = await _mcp_request("initialize", init_params)

    global _protocol_version
    _protocol_version = init_response.get('result', {}).get('protocolVersion')
    server_info = init_response.get('result', {}).get('serverInfo', {})
    print(f"   -> Success! Connected to: {server_info.get('title', server_info.get('name', 'Unknown Server'))}")
    print(f"   -> Protocol version: {_protocol_version}")

    # Send initialized notification (required by 2025-06-18)
    print("   -> Sending initialized notification...")
    await _mcp_request("notifications/initialized")
    print("   -> Session fully ready for operations")

    # 2. List available tools
    print("\n[Step 2: Discovering Tools]")
    print("We ask the server what tools it has with a 'tools/list' request.")
    tools_response = await _mcp_request("tools/list")

    tools = tools_response.get('result', {}).get('tools', [])
    print(f"   -> Success! Server has {len(tools)} tools:")
    for tool in tools:
        tool_name = tool.get('name')
        tool_desc = tool.get('description', 'No description')
        print(f"      - {tool_name}: {tool_desc}")

    # 3. Test simple tools (auto-wrapped primitives)
    print("\n[Step 3: Testing Simple Tools (Auto-wrapped Results)]")

    # Test list_cities (returns list wrapped in {"result": ...})
    print("Testing list_cities...")
    cities_response = await _mcp_request("tools/call", {
        "name": "list_cities",
        "arguments": {}
    })
    if 'error' not in cities_response:
        result = cities_response.get('result', {})
        print(f"   -> Cities: {result}")

    # Test get_temperature (returns float wrapped in {"result": ...})
    print("Testing get_temperature...")
    temp_response = await _mcp_request("tools/call", {
        "name": "get_temperature",
        "arguments": {"city": "London"}
    })
    if 'error' not in temp_response:
        result = temp_response.get('result', {})
        print(f"   -> Temperature: {result}")

    # 4. Test structured Pydantic model tool
    print("\n[Step 4: Testing Pydantic Model Tool (Structured Output)]")
    print("Testing get_weather with structured WeatherData response...")
    weather_response = await _mcp_request("tools/call", {
        "name": "get_weather",
        "arguments": {"city": "Paris"}
    })
    if 'error' not in weather_response:
        result = weather_response.get('result', {})
        print(f"   -> Weather Data: {result}")

    # 5. Test advanced structured output with TextContent
    print("\n[Step 5: Testing Advanced Structured Output (TextContent)]")
    print("Testing add_numbers with rich annotations...")
    add_response = await _mcp_request("tools/call", {
        "name": "add_numbers",
        "arguments": {"a": 15.5, "b": 27.3}
    })
    if 'error' not in add_response:
        result = add_response.get('result', {})
        content_list = result.get('content', [])
        if content_list:
            for i, content in enumerate(content_list):
                print(f"   -> Content {i+1}: {content.get('text', 'No text')}")
                annotations = content.get('annotations', {})
                if annotations:
                    print(f"   -> Annotations: {annotations}")

    # 6. Test multi-content tool
    print("\n[Step 6: Testing Multi-Content Tool (Multiple TextContent Items)]")
    print("Testing analyze_data with multiple content sections...")
    analyze_response = await _mcp_request("tools/call", {
        "name": "analyze_data",
        "arguments": {"data_type": "sales", "sample_size": 500}
    })
    if 'error' not in analyze_response:
        result = analyze_response.get('result', {})
        content_list = result.get('content', [])
        print(f"   -> Received {len(content_list)} content items:")
        for i, content in enumerate(content_list):
            content_type = content.get('type', 'unknown')
            print(
                f"   -> Item {i+1} ({content_type}): {content.get('text', 'No text')[:100]}...")

    print("\n--- Demonstration Complete ---")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
