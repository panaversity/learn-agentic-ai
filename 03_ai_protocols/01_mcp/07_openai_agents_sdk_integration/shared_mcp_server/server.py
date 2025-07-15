import logging
from mcp.server.fastmcp import FastMCP

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Create and Configure the FastMCP Application ---
mcp_app = FastMCP(
    name="SharedStandAloneMCPServer",
    stateless_http=True,
    json_response=True, # Generally easier for HTTP clients if they don't need full SSE parsing
)

# --- 2. Define a simple tool ---
@mcp_app.tool(
    name="greet_from_shared_server",
    description="Returns a personalized greeting from the shared MCP server."
)
def greet(name: str = "World") -> str:
    """A simple greeting tool."""
    logger.info(f"Tool 'greet_from_shared_server' called with name: {name}")
    response_message = f"Hello, {name}, from the SharedStandAloneMCPServer!"
    return response_message

@mcp_app.tool(
    name="mood_from_shared_server",
    description="Returns a personalized greeting from the shared MCP server."
)
def mood(name: str = "World") -> str:
    """A simple greeting tool."""
    logger.info(f"Tool 'moo' called with name: {name}")
    return "I am happy"

# --- (Optional) Define a simple resource ---
WELCOME_MSG_URI = "app:///messages/shared_welcome"
@mcp_app.resource(
    uri=WELCOME_MSG_URI,
    name="Shared Welcome Message",
    description="A static welcome message from the shared server.",
    mime_type="text/plain"
)
def get_welcome_message() -> str:
    logger.info(f"Resource '{WELCOME_MSG_URI}' requested.")
    return "Welcome! This is a static resource from the SharedStandAloneMCPServer."

streamable_http_app = mcp_app.streamable_http_app()

if __name__ == "__main__":
    port = 8001
    import uvicorn
    uvicorn.run("server:streamable_http_app", host="0.0.0.0", port=port, reload=True)

