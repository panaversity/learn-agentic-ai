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

if __name__ == "__main__":
    import uvicorn
    logger.info("🏓 Starting MCP Server with Ping Utility...")
    logger.info("🌐 Server will run on http://0.0.0.0:8000")
    logger.info("🧪 Test ping with: POST /mcp/ {'method': 'ping', 'id': '1', 'jsonrpc': '2.0'}")
    
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)