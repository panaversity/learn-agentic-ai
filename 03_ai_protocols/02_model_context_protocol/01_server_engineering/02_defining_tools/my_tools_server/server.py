from mcp.server.fastmcp import FastMCP

# Initialize a stateless FastMCP server
mcp = FastMCP(
    name="my-tools-server",
    description="A simple server to demonstrate defining MCP tools.",
    stateless_http=True
)

# --- Tool 1: A simple calculator tool ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two integers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    return a + b

# --- Tool 2: A simple greeter tool ---
@mcp.tool()
async def greet(name: str) -> str:
    """
    Provides a friendly greeting.

    Args:
        name: The name of the person to greet.

    Returns:
        A personalized greeting message.
    """
    return f"Hello, {name}! Welcome to the world of MCP tools."

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()