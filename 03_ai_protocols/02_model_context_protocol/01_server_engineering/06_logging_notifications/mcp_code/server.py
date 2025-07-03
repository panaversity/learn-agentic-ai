import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

# Setup logging for our console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server - FastMCP automatically supports logging via Context
mcp = FastMCP("Simple Logging Server", stateless_http=False)

@mcp.tool()
async def do_work(task: str, ctx: Context) -> str:
    """
    Perform some work and demonstrate MCP logging.
    
    Args:
        task: The task to perform
        ctx: MCP context for logging
    """
    await ctx.info(f"Starting to process task: {task}")
    
    # Simulate some work with natural logging
    await ctx.debug("Initializing task processor...")
    await ctx.info("Loading configuration...")
    
    if "data" in task.lower():
        await ctx.debug("Processing data-related task")
        await ctx.info("Validating input data...")
        await ctx.info("Data validation successful")
        await ctx.debug("Applying data transformations...")
        await ctx.info("Task processing completed successfully")
        return f"Successfully processed data task: {task}"
    else:
        await ctx.debug(f"Processing general task: {task}")
        await ctx.info("Executing task logic...")
        await ctx.info("Task completed successfully")
        return f"Task '{task}' completed successfully"


# Create the streamable HTTP app
mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn    
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)