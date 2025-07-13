"""
MCP Logging Client - Simple Educational Implementation

This client provides a minimal, easy-to-understand demonstration of
receiving MCP logging notifications.
"""

import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import LoggingMessageNotificationParams


async def log_handler(params: LoggingMessageNotificationParams):
    """Handles and formats log messages from the server."""
    emoji_map = {
        "debug": "🔍",
        "info": "📰",
        "warning": "⚠️",
        "error": "❌",
    }
    emoji = emoji_map.get(params.level.lower(), "📝")
    logger_info = f" [{params.logger}]" if params.logger else ""
    print(f"    {emoji} [{params.level.upper()}]{logger_info} {params.data}")


async def main():
    """A simple client to demonstrate receiving MCP logging notifications."""
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, get_session_id):
            async with ClientSession(read_stream, write_stream, logging_callback=log_handler) as session:
                print("✅ Connected. Initializing session...")
                await session.initialize()
                print("🛠️ Session initialized.")

                print("\nSCENARIO 1: Successful processing")
                print("-" * 40)
                result = await session.call_tool("process_item", {"item_id": "item-123", "should_fail": False})
                if result.content:
                    print(f"✅ Result: {result.content[0].text}")

                await asyncio.sleep(1)

                print("\nSCENARIO 2: Processing with failure")
                print("-" * 40)
                result = await session.call_tool("process_item", {"item_id": "item-456", "should_fail": True})
                if result.content:
                    print(f"✅ Result: {result.content[0].text}")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Make sure the server is running.")

    print("\n🎉 Demo finished.")

if __name__ == "__main__":
    asyncio.run(main())
