"""
MCP Roots Server - Simple Educational Implementation

This server demonstrates the core roots feature, allowing servers to discover
and work with project directories exposed by the client.
"""
from pathlib import Path
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent

# Initialize FastMCP server
mcp = FastMCP(
    name="mcp-roots-server",
    stateless_http=False
)


@mcp.tool()
async def analyze_project(ctx: Context) -> TextContent:
    """
    Analyzes project structure using roots provided by the client.

    Returns:
        A summary of the project structure
    """
    print("-> Server: Requesting project roots from client...")
    roots = await ctx.session.list_roots()

    if not roots or not roots.roots:
        return TextContent(text="No project roots found", type="text")

    root = roots.roots[0]  # Get first root for simplicity
    print(f"<- Server: Received root: {root.uri}")

    # Parse the file URI to get the actual path
    path = Path(urlparse(root.uri).path)

    # Do a simple analysis
    py_files = list(path.glob("**/*.py"))

    analysis = f"Found {len(py_files)} Python files in project at {path}"
    print(f"-> Server: Analysis complete: {analysis}")

    return TextContent(text=analysis, type="text")

# Create FastAPI app
mcp_app = mcp.streamable_http_app()
