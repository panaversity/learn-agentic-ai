# Module 2: Caching MCP Tool Lists with OpenAI Agents SDK

## Introduction

When an Agent interacts with an MCP server, it typically calls `list_tools()` to discover available tools. Frequent calls, especially to remote servers, can introduce latency. The OpenAI Agents SDK provides a way to cache this tool list to improve performance.

This module explains how to enable and verify tool list caching when using MCP server clients with the OpenAI Agents SDK, referencing the official SDK documentation.

As stated in the [OpenAI Agents SDK MCP Documentation](https://openai.github.io/openai-agents-python/mcp/):

> Every time an Agent runs, it calls `list_tools()` on the MCP server. This can be a latency hit, especially if the server is a remote server. To automatically cache the list of tools, you can pass `cache_tools_list=True`.


## Enabling Caching

To enable tool list caching, pass the boolean parameter `cache_tools_list=True` directly to the constructor of your MCP server client (e.g., `MCPServerStreamableHttp`, `MCPServerStdio`, or `MCPServerSse`).

```python
    async with MCPServerStreamableHttp(params=mcp_params_cached, name="CachedClient", cache_tools_list=True)
```

If you want to invalidate the cache, you can call invalidate_tools_cache() on the servers.


## Verifying Caching Behavior

**Server-Side Logs**: The most reliable way to verify caching is to check your MCP server's logs. When client-side caching is active, the server should receive significantly fewer `ListToolsRequest` messages for repeated `list_tools()` calls from the same client instance.

## Demonstration (`agent_connect_cache/agent_tool_caching.py`)

The `agent_tool_caching.py` script (located in the `agent_connect_cache` subdirectory of this module, as per your working version) demonstrates this caching behavior with `MCPServerStreamableHttp`.

It initializes an `MCPServerStreamableHttp` client with `cache_tools_list=True` and makes multiple calls to `list_tools()`. By observing the server logs, you can confirm that the `ListToolsRequest` is processed by the server far fewer times than `list_tools()` is called by the client.

### Running the Example:

1.  **Ensure your Shared MCP Server is Running**:
    The client script will target the URL (e.g., `http://localhost:8001/mcp`). Start your server accordingly.
    Example command to run the shared server from the `07_openai_agents_sdk_integration/` directory:

    ```bash
    uv run python shared_mcp_server/server.py
    ```

2.  **Run the Caching Script**:
    Navigate to the `05_ai_protocols/01_mcp/07_openai_agents_sdk_integration/02_caching_tool_lists/agent_connect_cache/` directory (or wherever your working `agent_tool_caching.py` is located) and run:

    ```bash
    uv run python agent_tool_caching.py
    ```

3.  **Observe Server Logs**: Note how many times your server logs a `ListToolsRequest` (or similar). With `cache_tools_list=True`, this should be minimal for repeated client calls.

This module, guided by the official documentation and your practical findings, clarifies how to enable and verify tool list caching.
