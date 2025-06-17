#!/usr/bin/env python3
"""
Simple test to verify MCP server functionality.
"""

import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def simple_test():
    """Test basic MCP functionality."""
    print("🧪 Simple MCP Test")
    print("-" * 30)
    
    try:
        async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Connected to MCP server!")
                
                # Initialize the session
                init_result = await session.initialize()
                print(f"🔧 Server: {init_result.serverInfo.name}")
                
                # List available tools
                tools_result = await session.list_tools()
                print(f"📋 Available tools: {[tool.name for tool in tools_result.tools]}")
                
                # Test one simple tool
                print("\n⚡ Testing quick_task...")
                result = await session.call_tool("quick_task", {"message": "Test message"})
    
                
                if result.content:
                    for content in result.content:
                        print(f"✅ Result: {content.text}")
                else:
                    print("✅ Tool completed (no content)")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(simple_test()) 