# Module 2: Caching MCP Tool Lists with OpenAI Agents SDK

## Introduction

When an Agent interacts with an MCP server, it typically calls `list_tools()` to discover available tools. Frequent calls, especially to remote servers, can introduce latency. The OpenAI Agents SDK provides a way to cache this tool list to improve performance.

This module explains how to enable and verify tool list caching when using MCP server clients with the OpenAI Agents SDK, referencing the official SDK documentation.

As stated in the [OpenAI Agents SDK MCP Documentation](https://openai.github.io/openai-agents-python/mcp/):

> Every time an Agent runs, it calls `list_tools()` on the MCP server. This can be a latency hit, especially if the server is a remote server. To automatically cache the list of tools, you can pass `cache_tools_list=True`.



## Enabling Caching

To enable tool list caching, pass the boolean parameter `cache_tools_list=True` directly to the constructor of your MCP server client (e.g., `MCPServerStreamableHttp`, `MCPServerStdio`, or `MCPServerSse`).

```python
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

```

If you want to invalidate the cache, the documentation mentions you can call `invalidate_tools_cache()` on the servers, though the availability of this method might vary per client type and SDK version.

## Verifying Caching Behavior

**Server-Side Logs**: The most reliable way to verify caching is to check your MCP server's logs. When client-side caching is active, the server should receive significantly fewer `ListToolsRequest` messages for repeated `list_tools()` calls from the same client instance.

## Demonstration (`agent_connect_cache/agent_tool_caching.py`)

The `agent_tool_caching.py` script (located in the `agent_connect_cache` subdirectory of this module, as per your working version) demonstrates this caching behavior with `MCPServerStreamableHttp`.

It initializes an `MCPServerStreamableHttp` client with `cache_tools_list=True` and makes multiple calls to `list_tools()`. By observing the server logs, you can confirm that the `ListToolsRequest` is processed by the server far fewer times than `list_tools()` is called by the client.

### Running the Example:

1.  **Ensure your Shared MCP Server is Running**:
    The client script will target the URL (e.g., `http://localhost:8001/mcp`). Start your server accordingly.
    Example command to run the shared server from the `03_openai_agents_sdk_with_mcp/` directory:

    ```bash
    uv run python shared_mcp_server/server.py
    ```

2.  **Run the Caching Script**:
    Navigate to the `05_ai_protocols/01_model_context_protocol/03_openai_agents_sdk_with_mcp/02_caching_mcp_tool_lists/agent_connect_cache/` directory (or wherever your working `agent_tool_caching.py` is located) and run:

    ```bash
    uv run python agent_tool_caching.py
    ```

3.  **Observe Server Logs**: Note how many times your server logs a `ListToolsRequest` (or similar). With `cache_tools_list=True`, this should be minimal for repeated client calls.

This module, guided by the official documentation and your practical findings, clarifies how to enable and verify tool list caching.
