from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="hello-mcp", stateless_http=True)

@mcp.tool(name="online_researcher", description="Search the web for information")
def search_online(query: str) -> str:
    # TODO: Implement search logic
    return f"Results for {query}..."

# Transport -> Get Starlette instance
mcp_app = mcp.streamable_http_app()
