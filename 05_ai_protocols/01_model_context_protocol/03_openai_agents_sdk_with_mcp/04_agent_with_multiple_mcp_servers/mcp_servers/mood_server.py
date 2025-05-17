import logging
from mcp.server.fastmcp import FastMCP

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. Create and Configure the FastMCP Application ---
mcp_app = FastMCP(
    name="ToolServer1",
    description="A simple shared MCP server for OpenAI Agents SDK examples.",
    stateless_http=True,
    json_response=True, # Generally easier for HTTP clients if they don't need full SSE parsing
)


@mcp_app.tool(
    name="mood_from_shared_server",
    description="Returns a personalized greeting from the shared MCP server."
)
def mood(name: str = "World") -> str:
    """A simple greeting tool."""
    logger.info(f"Tool 'moo' called with name: {name}")
    return "I am happy"

if __name__ == "__main__":
    port = 8001
    streamable_http_app = mcp_app.streamable_http_app()
    logger.info(f"Starting {streamable_http_app}")
    import uvicorn
    # uvicorn.run(streamable_http_app, host="0.0.0.0", port=port)
    # start with hot reload
    uvicorn.run("mood_server:mcp_app.streamable_http_app", host="0.0.0.0", port=port, reload=True)