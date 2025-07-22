import asyncio

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context
from mcp import types

# Create a simple MCP server
mcp = FastMCP(
    name="Simple Logging Server",
    stateless_http=True  
)


@mcp.tool(
    name="process_item",
    description="Processes an item and generates logs at different levels."
)
async def process_item(
    ctx: Context,
    item_id: str,
    should_fail: bool = False,
) -> list[types.TextContent]:
    """
    A simple tool that demonstrates logging by emitting messages
    at different severity levels.
    """
    await ctx.debug(f"Starting processing for item: {item_id}")
    await asyncio.sleep(0.2)
    await ctx.info("Configuration loaded successfully.")
    await asyncio.sleep(0.2)

    if should_fail:
        await ctx.warning(f"Item '{item_id}' has a validation issue. Attempting to proceed...")
        await asyncio.sleep(0.2)
        await ctx.error(f"Failed to process item '{item_id}'. Critical failure.")
        return [types.TextContent(type="text", text=f"Failed to process {item_id}.")]

    await ctx.info(f"Item '{item_id}' processed successfully.")

    return [types.TextContent(type="text", text=f"Successfully processed {item_id}.")]

# Create the streamable HTTP app for stateful connections
mcp_app = mcp.streamable_http_app()
