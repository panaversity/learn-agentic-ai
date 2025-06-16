"""
Replay Client Example - Demonstrates MCP EventStore Event Replay

This client shows how to interact with the replay server:
- Tests event generation and replay
- Uses longer timeouts to see full event sequences
- Demonstrates understanding of event replay concepts
"""

import asyncio
import json


# Simple MCP request function based on user's template
async def mcp_request(method: str, params=None):
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
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"   -> Sending {method} request...")
            response = await client.post("http://localhost:8001/mcp/", json=payload, headers=headers)
            response.raise_for_status()
            print("RAW RESPONSE: ", type(response.text),
                  response.text[:200], "...")

            # The server sends back SSE, so we parse it to get the JSON data
            for line in response.text.strip().split('\n'):
                print("LINE: ", line[:100] +
                      "..." if len(line) > 100 else line)
                if line.startswith('data: '):
                    return json.loads(line[6:])
            return {"error": "No data found in SSE response"}
    except ImportError:
        print("httpx not available - using mock response")
        return {"result": {"tools": []}}
    except Exception as e:
        print(f"   -> An error occurred: {e}")
        return {"error": str(e)}


async def main():
    """A step-by-step demonstration of replay functionality."""
    print("--- Replay Client Demo: Event Replay with EventStore ---")
    print()

    # 1. List available tools
    print("[Step 1: Ask the server what it can do]")
    print("We send a 'tools/list' request to discover available tools.")
    tools_response = await mcp_request("tools/list")

    if 'error' in tools_response:
        print(f"   -> Error listing tools: {tools_response['error']}")
        print("   -> Make sure replay server is running on port 8001")
        print("   -> Run: python examples/event_stores/replay_server/server.py")
        return

    tools = tools_response.get('result', {}).get('tools', [])
    if not tools:
        print("   -> The server didn't return any tools.")
        return

    print(f"   -> Success! The server has {len(tools)} tools:")
    for tool in tools:
        tool_name = tool.get('name')
        tool_desc = tool.get('description', '').strip()
        print(f"      - {tool_name}: {tool_desc[:60]}...")

    print()

    # 2. Test normal forecast tool
    print("[Step 2: Test normal forecast tool]")
    city = "London"
    print(f"Now, we'll call get_forecast to get the weather for '{city}'.")
    call_params = {"name": "get_forecast", "arguments": {"city": city}}
    call_response = await mcp_request("tools/call", call_params)

    if 'error' in call_response:
        print(f"   -> Error calling 'get_forecast': {call_response['error']}")
    else:
        result = call_response.get('result', {}).get('content', [{}])
        if result:
            text = result[0].get('text', 'No text found')
            print(f"   -> Success! Response: '{text}'")

    print()

    # 3. Test event generation tool
    print("[Step 3: Generate events for replay testing]")
    print("Calling generate_events to create multiple events...")
    event_params = {"name": "generate_events", "arguments": {"count": 5}}
    event_response = await mcp_request("tools/call", event_params)

    if 'error' in event_response:
        print(
            f"   -> Error calling 'generate_events': {event_response['error']}")
    else:
        result = event_response.get('result', {}).get('content', [{}])
        if result:
            text = result[0].get('text', 'No text found')
            print(f"   -> Success! Events generated: '{text}'")

    print()

    # 4. Test slow task (demonstrates multiple events)
    print("[Step 4: Test slow task for event sequence]")
    print("Calling slow_task to see event logging...")
    slow_params = {"name": "slow_task",
                   "arguments": {"task_name": "replay-demo"}}
    slow_response = await mcp_request("tools/call", slow_params)

    if 'error' in slow_response:
        print(f"   -> Error calling 'slow_task': {slow_response['error']}")
    else:
        result = slow_response.get('result', {}).get('content', [{}])
        if result:
            text = result[0].get('text', 'No text found')
            print(f"   -> Success! Slow task result: '{text}'")

    print()
    print("--- Replay Demo Complete ---")
    print()
    print("💡 Key Concepts Demonstrated:")
    print("- Event generation during tool execution")
    print("- Multiple events per request (generate_events)")
    print("- Event logging for replay functionality")
    print("- EventStore captures all events for later replay")
    print()
    print("🔄 In production:")
    print("- Events would be stored in persistent storage (Redis, DB)")
    print("- Clients could replay events from any point using Last-Event-ID")
    print("- Useful for debugging, auditing, and resuming connections")


if __name__ == "__main__":
    asyncio.run(main())
