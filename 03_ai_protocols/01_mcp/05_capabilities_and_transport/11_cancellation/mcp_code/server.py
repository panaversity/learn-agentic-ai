import asyncio
from mcp.server.fastmcp import FastMCP, Context

# Create the FastMCP application instance
mcp_server = FastMCP(
    "Cancellation Demo Server",
    title="Cancellation Demo Server",
    description="A server to demonstrate MCP cancellation.",
)


@mcp_server.tool()
async def process_large_file(
    ctx: Context,
    filename: str,
    processing_time: int = 10,
) -> str:
    """
    Simulates a long-running, cancellable task. The framework will inject
    an `asyncio.CancelledError` into this task when the client sends a
    cancellation notification.
    """
    await ctx.info(f"Starting to process {filename} (Request: {ctx.request_id})")
    try:
        for i in range(processing_time):
            # The 'await' gives asyncio a chance to interrupt the task.
            await asyncio.sleep(1)
            await ctx.debug(f"Processed chunk {i + 1}/{processing_time}")

        return f"Successfully processed {filename}"

    except asyncio.CancelledError:
        # This block runs when the framework cancels the task.
        await ctx.warning(f"Processing of {filename} was cancelled by client.")
        # Re-raise the error. The framework will catch this and send the
        # correct JSON-RPC error response to the client (-32800).
        raise

mcp_app = mcp_server.streamable_http_app()
