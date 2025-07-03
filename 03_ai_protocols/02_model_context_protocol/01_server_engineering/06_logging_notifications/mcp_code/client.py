import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import LoggingMessageNotificationParams

async def log_handler(params: LoggingMessageNotificationParams):
    """Handle log messages from the server"""
    # print(f"🔍 RAW Logging message: {params}")
    emoji_map = {
        "debug": "🔍",
        "info": "📰", 
        "warning": "⚠️",
        "error": "❌"
    }
    emoji = emoji_map.get(params.level.lower(), "📝")
    logger_info = f" [{params.logger}]" if params.logger else ""
    print(f"    {emoji} [{params.level.upper()}]{logger_info} {params.data}")

async def main():
    """
    Simple MCP client that demonstrates logging functionality.
    
    Shows how to:
    1. Connect to MCP server via Streamable HTTP
    2. Call a tool that generates logs
    3. See the server's actual logging in action
    """
    
    print("🚀 Starting MCP Logging Demo")
    print("=" * 40)
    
    # Connect using streamable HTTP client
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream, logging_callback=log_handler) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            init_result = await session.initialize()
            print(f"🔧 Server capabilities: {init_result.capabilities}")
            
            # List available tools
            tools_result = await session.list_tools()
            print(f"🛠️ Available tools: {[tool.name for tool in tools_result.tools]}")
            
            print(f"\n📝 Calling tool - watch for server logs:")
            print("-" * 40)
            
            try:
                # Call the tool - server will naturally log during execution
                result = await session.call_tool("do_work", {"task": "data"})
                
                print("-" * 40)
                if result.content:
                    for content in result.content:
                        print(f"✅ Result: {content}")
                else:
                    print("✅ Tool completed successfully (no output)")
                    
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
    
    print("\n🎉 Demo completed!")
    print("\n💡 The log messages above came directly from the server via MCP protocol!")

if __name__ == "__main__":
    asyncio.run(main()) 