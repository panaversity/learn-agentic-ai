from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="batching-server",
    description="A simple server to demonstrate MCP batching.",
    # stateless_http=True
)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers together."""
    print(f"Server: Executing add({a}, {b})")
    return a + b

@mcp.tool()
async def greet(name: str) -> str:
    """Provides a friendly greeting."""
    print(f"Server: Executing greet('{name}')")
    return f"Hello, {name}!"

# Expose the app for Uvicorn
mcp_app = mcp.streamable_http_app() 