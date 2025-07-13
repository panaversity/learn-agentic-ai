import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("Ping Demo Server")


@mcp.tool()
def get_current_time() -> str:
    """Get the current server time.

    Returns:
        Current time as a string
    """
    import datetime
    return f"Current server time: {datetime.datetime.now().isoformat()}"


# The ping functionality is automatically handled by FastMCP
# according to the MCP specification - no additional code needed!

# Create the streamable HTTP app
mcp_app = mcp.streamable_http_app()
