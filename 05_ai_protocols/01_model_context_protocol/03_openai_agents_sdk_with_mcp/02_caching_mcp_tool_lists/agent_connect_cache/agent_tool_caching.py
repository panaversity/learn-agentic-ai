import asyncio
import time
from agents.mcp import (
    MCPServerStreamableHttpParams,
    MCPServerStreamableHttp,
)
import logging
logger = logging.getLogger("openai.agents") # or openai.agents.tracing for the Tracing logger

# To make all logs show up
logger.setLevel(logging.DEBUG)

# Load environment variables from .env file
async def demonstrate_tool_listing(mcp_server_client: MCPServerStreamableHttp, description: str):
    """Helper to list tools and print timing, using the client directly."""
    print(f"\n[{time.strftime('%H:%M:%S')}] Attempting to list tools ({description}):")
    start_time = time.perf_counter()
    try:
        # The actual list_tools call happens when the SDK needs the tools,
        # e.g., during agent initialization if not already cached, or when explicitly called.
        # Here, we call it directly on the client for a clear demonstration.
        tools_list = await mcp_server_client.list_tools()
        end_time = time.perf_counter()
        if tools_list:
            print(f"    Tools listed: {[tool.name for tool in tools_list if tool.name]}")
        else:
            print("    No tools listed or error occurred.")
        print(f"    Time taken for list_tools(): {end_time - start_time:.4f} seconds")
    except Exception as e:
        end_time = time.perf_counter()
        print(f"    Error listing tools: {e}")
        print(f"    Time taken before error: {end_time - start_time:.4f} seconds")
    # SDK log should indicate cache status (e.g., "Using cached tools..." or "Fetching tools...")


async def main():


    # Correct base URL for our shared server
    mcp_server_base_url = "http://localhost:8001/mcp"

    print(f"--- Demonstrating Tool List Caching---")
    print(f"Target MCP Server: {mcp_server_base_url}")
    
    # --- Scenario 1: Caching Enabled ---_shared_mcp_server
    print("\n--- Scenario 1: Caching Enabled ---")
    mcp_params_cached = MCPServerStreamableHttpParams(
        url=mcp_server_base_url
    )
    print(f"mcp_params_cached: {mcp_params_cached}")
    async with MCPServerStreamableHttp(params=mcp_params_cached, name="CachedClient", cache_tools_list=True) as mcp_client_cached:
        print(f"mcp_client_cached: {mcp_client_cached}")
        # First call: should fetch from server and populate cache
        await demonstrate_tool_listing(mcp_client_cached, "1.1: First call (cache miss expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.2: Second call (cache hit expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.3: Second call (cache hit expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.4: Second call (cache hit expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.5: Second call (cache hit expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.6: Second call (cache hit expected)")
        await demonstrate_tool_listing(mcp_client_cached, "1.7: Second call (cache hit expected)")
    

    print("\n    Closed session for CachedClient.")

    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemonstration interrupted by user.")
