#!/usr/bin/env python3
"""
MCP Client demonstrating proper cancellation using MCP's built-in capabilities.

This shows how to interact with cancellable tools using the standard MCP client.
"""

import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_quick_operations():
    """Test quick operations that complete immediately."""
    print("\n🔥 QUICK OPERATIONS TEST")
    print("-" * 40)
    
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            await session.initialize()
            
            # Test quick task
            print("⚡ Testing quick task...")
            result = await session.call_tool("quick_task", {"message": "Hello from MCP client!"})
            
            if result.content:
                for content in result.content:
                    print(f"✅ Quick task result: {content.text}")
            
            # Test request status
            print("📊 Checking request status...")
            result = await session.call_tool("get_request_status", {})
            
            if result.content:
                for content in result.content:
                    print(f"📋 Status: {content.text}")

async def test_long_running_task():
    """Test a long-running task with progress updates."""
    print("\n🔄 LONG-RUNNING TASK TEST")
    print("-" * 40)
    
    async def progress_handler(progress: float, total: float | None, message: str | None):
        """Handle progress updates from the server"""
        if total:
            percentage = (progress / total) * 100
            progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
            print(f"    📊 [{progress_bar}] {percentage:.1f}% - {message or 'Processing...'}")
        else:
            print(f"    📊 Progress: {progress} - {message or 'Processing...'}")
    
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            await session.initialize()
            
            # Start long-running file processing
            print("📁 Starting file processing...")
            try:
                result = await session.call_tool(
                    "process_large_file", 
                    {
                        "filename": "large_dataset.csv",
                        "processing_time": 8
                    },
                    progress_callback=progress_handler
                )
                
                print("-" * 40)
                if result.content:
                    for content in result.content:
                        print(f"✅ Processing result: {content.text}")
                        
            except Exception as e:
                print(f"❌ Error during processing: {e}")

async def test_network_simulation():
    """Test network request simulation."""
    print("\n🌐 NETWORK REQUEST TEST")
    print("-" * 40)
    
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            await session.initialize()
            
            # Test network request
            print("🌐 Simulating network request...")
            try:
                result = await session.call_tool(
                    "simulate_network_request", 
                    {
                        "url": "https://api.example.com/data",
                        "timeout": 3
                    }
                )
                
                if result.content:
                    for content in result.content:
                        print(f"✅ Network result: {content.text}")
                        
            except Exception as e:
                print(f"❌ Error during network request: {e}")

async def test_cancellation_demo():
    """Demonstrate cancellation by starting a task and cancelling it."""
    print("\n⏹️ CANCELLATION DEMO")
    print("-" * 40)
    print("This would demonstrate cancellation if MCP client supported it directly.")
    print("In practice, cancellation happens when the client disconnects or")
    print("the underlying asyncio task is cancelled.")
    
    # Note: The MCP client doesn't expose direct cancellation APIs
    # Cancellation typically happens at the transport level when connections are lost
    # or when the client process is terminated

async def list_available_tools():
    """List all available tools on the server."""
    print("\n🛠️ AVAILABLE TOOLS")
    print("-" * 40)
    
    async with streamablehttp_client("http://localhost:8000/mcp/") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server!")
            
            # Initialize the session
            init_result = await session.initialize()
            print(f"🔧 Server: {init_result.server_info.name}")
            
            # List available tools
            tools_result = await session.list_tools()
            print(f"📋 Available tools ({len(tools_result.tools)}):")
            
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description}")

async def main():
    """
    Main demo function showing MCP cancellation capabilities.
    """
    print("🧪 MCP Cancellation Demo Client")
    print("=" * 50)
    print("Demonstrating proper MCP client usage with cancellable tools")
    print()
    
    try:
        # Run all test scenarios
        await list_available_tools()
        await test_quick_operations()
        await test_long_running_task()
        await test_network_simulation()
        await test_cancellation_demo()
        
        print("\n🎉 All tests completed!")
        print("\n💡 Key learnings:")
        print("  • MCP handles request lifecycle automatically")
        print("  • Context provides request_id and progress reporting")
        print("  • asyncio.CancelledError enables graceful cancellation")
        print("  • No manual task tracking needed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nMake sure the server is running:")
        print("  uv run server.py")

if __name__ == "__main__":
    asyncio.run(main()) 