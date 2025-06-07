import logging
from mcp.server.fastmcp import FastMCP

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Create and Configure the FastMCP Application ---
mcp_app = FastMCP(
    name="SharedStandAloneMCPServer",
    description="A simple shared MCP server for OpenAI Agents SDK examples.",
    stateless_http=True,
)

# --- 2. Define a simple tool ---
@mcp_app.tool(
    name="greet_from_shared_server",
    description="Returns a personalized greeting from the shared MCP server."
)
def greet(name: str = "World") -> str:
    """A simple greeting tool."""
    logger.info(f"Tool 'greet_from_shared_server' called with name: {name}")
    # response_message = f"Hello, {name}, from the SharedStandAloneMCPServer!"
    response_message = f"Hello, {name}, from the UPDATED SharedStandAloneMCPServer with Hot Reload!"
    return response_message

@mcp_app.tool(
    name="mood_from_shared_server",
    description="Returns a personalized greeting from the shared MCP server."
)
def mood(name: str = "World") -> str:
    """A simple greeting tool."""
    logger.info(f"Tool 'mood' called with name: {name}")
    return "I am happy"

streamable_http_app = mcp_app.streamable_http_app()
logger.info(f"Starting {streamable_http_app}")

# --- Main entry point to run the server ---
if __name__ == "__main__":
    port = 8001
    import uvicorn
    uvicorn.run("server:streamable_http_app", host="0.0.0.0", port=port, reload=True)

