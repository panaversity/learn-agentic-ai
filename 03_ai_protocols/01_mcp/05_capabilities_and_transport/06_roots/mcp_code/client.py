"""
MCP Roots Client - Simple Educational Implementation

This client demonstrates how to:
1. Declare roots capability during initialization
2. Handle roots/list requests from servers
3. Provide project directory information
"""

import asyncio
from pathlib import Path
from pydantic import FileUrl

from mcp.shared.context import RequestContext
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Root, ListRootsResult, ErrorData

def _create_roots(root_paths: list[str]) -> list[Root]:
    """Convert path strings to Root objects."""
    roots = []
    for path in root_paths:
        p = Path(path).resolve()
        file_url = FileUrl(f"file://{p}")
        roots.append(Root(uri=file_url, name=p.name or "Root"))
    return roots

async def _handle_list_roots(
    context: RequestContext["ClientSession", None]
) -> ListRootsResult | ErrorData:
    """Callback for when server requests roots."""
    root_paths = [str(Path.cwd().absolute())]
    return ListRootsResult(roots=_create_roots(root_paths))


async def main():
    """Demonstrate roots capability with a simple server interaction."""
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, get_session_id):
            # Create session with elicitation capability

            async with ClientSession(read_stream, write_stream, list_roots_callback=_handle_list_roots) as session:
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
