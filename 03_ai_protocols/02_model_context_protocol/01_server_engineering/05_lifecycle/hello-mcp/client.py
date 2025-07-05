import httpx
import asyncio


async def initialize_mcp(client: httpx.AsyncClient, url: str) -> str:
    """Step 1: Initialize MCP connection."""
    print("\n[Step 1: Initialize the MCP server]")

    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {},
                "elicitation": {}
            },
            "clientInfo": {
                "name": "example-client",
                "title": "Example Client Display Name",
                "version": "1.0.0"
            }
        },
        "id": 1
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    print("   -> Sending initialize request...")
    response = await client.post(url, json=init_payload, headers=headers)
    response.raise_for_status()

    print(f"   -> Response status: {response.status_code}")
    session_id = response.headers.get("mcp-session-id")
    if session_id:
        print(f"   -> Session ID: {session_id}")

    print(f"\n   -> [RESPONSE]: {response.text}\n")
    return session_id


async def send_initialized(client: httpx.AsyncClient, url: str, session_id: str):
    """Step 2: Send initialized notification."""
    print("\n[Step 2: Send initialized notification]")

    initialized_payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2024-11-05",
        "mcp-session-id": session_id
    }

    print("   -> Sending initialized notification...")
    response = await client.post(url, json=initialized_payload, headers=headers)
    print(f"   -> Response status: {response.status_code}")


async def list_tools(client: httpx.AsyncClient, url: str, session_id: str):
    """Step 3: List available tools."""
    print("\n[Step 3: List available tools]")

    list_tools_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2024-11-05",
        "mcp-session-id": session_id
    }

    print("   -> Requesting tools list...")
    response = await client.post(url, json=list_tools_payload, headers=headers)
    response.raise_for_status()

    print(f"\n   -> [RESPONSE]: {response.text}\n")


async def call_tool(client: httpx.AsyncClient, url: str, session_id: str):
    """Step 4: Call a weather tool."""
    print("\n[Step 4: Call the weather tool]")

    call_tool_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_forecast",
            "arguments": {
                "city": "San Francisco"
            }
        },
        "id": 3
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2024-11-05",
        "mcp-session-id": session_id
    }

    print("   -> Calling get_forecast tool...")
    response = await client.post(url, json=call_tool_payload, headers=headers)
    response.raise_for_status()

    print(f"\n   -> [RESPONSE]: {response.text}\n")


def prepare_for_shutdown(session_id: str):
    """Step 5: Prepare for MCP connection shutdown."""
    print("\n[Step 5: Prepare for MCP shutdown]")
    print("   -> Per MCP 2025-06-18 spec: 'No specific shutdown messages are defined'")
    print("   -> For HTTP transport: 'shutdown is indicated by closing HTTP connection'")
    print(f"   -> Session {session_id} will terminate when connection closes")


async def main():
    """Complete MCP client demonstrating full lifecycle."""
    print("=== MCP Complete Lifecycle Demo (2025-06-18 Specification) ===")

    url = "http://localhost:8000/mcp/"
    session_id = None

    async with httpx.AsyncClient() as client:
        print("\n🔗 Opening HTTP connection for MCP session...")

        try:
            # Complete MCP lifecycle
            session_id = await initialize_mcp(client, url)
            if not session_id:
                print("❌ Failed to get session ID - aborting")
                return

            await send_initialized(client, url, session_id)
            await list_tools(client, url, session_id)
            await call_tool(client, url, session_id)
            prepare_for_shutdown(session_id)

        except Exception as e:
            print(f"❌ MCP lifecycle error: {e}")

    print("\n🔚 HTTP connection closed - MCP lifecycle complete!")

if __name__ == "__main__":
    asyncio.run(main())
