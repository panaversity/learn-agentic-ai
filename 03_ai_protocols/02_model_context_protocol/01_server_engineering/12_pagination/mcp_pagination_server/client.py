import asyncio

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def fetch_all_tools(session: ClientSession):
    """
    Fetches all tools from the server by following the pagination cursors.
    """
    print("\n--- Fetching all tools (paginated) ---")
    all_tools = []
    next_cursor: str | None = None
    page_num = 1

    while True:
        print(f"📄 Fetching page {page_num} (cursor: '{next_cursor}')...")
        response = await session.list_tools(cursor=next_cursor)

        print("\n[RESPONSE] : ", response)

        page_tools = response.tools
        all_tools.extend(page_tools)

        print(f"✅ Received {len(page_tools)} tools. Total so far: {len(all_tools)}")

        if not response.nextCursor:
            print("   🏁 No nextCursor found. All tools fetched.")
            break

        next_cursor = response.nextCursor
        page_num += 1
        # Small delay to make the demo easier to follow
        await asyncio.sleep(0.5)

    print("--- All tools fetched ---")
    return all_tools


async def main():
    """
    Main client function to demonstrate pagination.
    """
    print("🚀 Starting MCP Pagination Client Demo...")
    server_url = "http://localhost:8000/mcp/"

    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server.")
                await session.initialize()
                await fetch_all_tools(session)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("   Is the pagination server running?")

    print("\n🏁 Demo finished.")


if __name__ == "__main__":
    asyncio.run(main())
