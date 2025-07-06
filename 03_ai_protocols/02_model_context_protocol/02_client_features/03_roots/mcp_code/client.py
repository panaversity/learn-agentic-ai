"""
MCP Roots Client - Simple Educational Implementation

This client demonstrates how to:
1. Declare roots capability during initialization
2. Handle roots/list requests from servers
3. Provide project directory information
"""

import asyncio
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.shared.context import RequestContext
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def mock_roots_list(context: RequestContext["ClientSession", Any]) -> types.ListRootsResult | types.ErrorData:
    """Handle roots/list requests from the server."""
    print(f"<- Client: Received roots/list request")

    # Get current directory as root
    root_uri = f"file://{Path.cwd().absolute()}"
    print(f"-> Client: Using root: {root_uri}")

    return types.ListRootsResult(roots=[types.Root(
        uri=types.FileUrl(root_uri),
        name="Current Project"
    )])


async def main():
    """Demonstrate roots capability with a simple server interaction."""
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, get_session_id):
            # Create session with elicitation capability

            async with ClientSession(read_stream, write_stream, list_roots_callback=mock_roots_list) as session:
                print("✅ Connected. Initializing session...")
                await session.initialize()
                print("🛠️ Session initialized with roots capability.")

                # Call the project analysis tool
                print("\n-> Client: Calling analyze_project tool...")
                result = await session.call_tool("analyze_project")

                print("\n🔍 Project Analysis Results:", result)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

    print("\n✅ Demo complete!")

if __name__ == "__main__":
    asyncio.run(main())
