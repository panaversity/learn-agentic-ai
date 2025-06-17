import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def progress_handler(progress: float, total: float | None, message: str | None):
    """Handle progress updates from the server"""
    if total:
        percentage = (progress / total) * 100
        progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
        print(f"    📊 [{progress_bar}] {percentage:.1f}% - {message or 'Working...'}")
    else:
        print(f"    📊 Progress: {progress} - {message or 'Working...'}")

async def main():
    """
    Simple MCP client that demonstrates progress tracking.
    
    Shows how to:
    1. Connect to MCP server via Streamable HTTP
    2. Call long-running tools with progress tokens
    3. Receive and display progress updates in real-time
    """
    
    print("🚀 Starting MCP Progress Demo")
    print("=" * 50)
    
    # Connect using streamable HTTP client
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            init_result = await session.initialize()
            print(f"🔧 Server capabilities: {init_result.capabilities}")
            
            # List available tools
            tools_result = await session.list_tools()
            print(f"🛠️ Available tools: {[tool.name for tool in tools_result.tools]}")
            
            # Test progress tracking with different scenarios
            scenarios = [
                {
                    "name": "📁 File Download",
                    "tool": "download_file",
                    "args": {"filename": "dataset.zip", "size_mb": 5}
                },
                {
                    "name": "🔄 Data Processing", 
                    "tool": "process_data",
                    "args": {"records": 20}
                }
            ]
            
            for scenario in scenarios:
                print(f"\n{scenario['name']}")
                print("-" * 40)
                
                try:
                    # Call tool with progress tracking
                    result = await session.call_tool(
                        scenario["tool"], 
                        scenario["args"],
                        progress_callback=progress_handler
                    )
                    
                    print("-" * 40)
                    if result.content:
                        for content in result.content:
                            print(f"✅ Result: {content}")
                    else:
                        print("✅ Tool completed successfully (no output)")
                        
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                
                print()  # Extra spacing between scenarios
    
    print("🎉 Demo completed!")
    print("\n💡 Progress updates were sent in real-time via MCP protocol!")

if __name__ == "__main__":
    asyncio.run(main()) 