from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="FastMCP", stateless_http=True)

docs = {
    "intro": "This is a simple example of a stateless MCP server.",
    "readme": "This server supports basic MCP operations.",
    "guide": "Refer to the documentation for more details.",
}


@mcp.resource("docs://documents", 
              mime_type="application/json")
def list_docs():
    """List all available documents."""
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_name}",
                mime_type="application/json")
def read_doc(doc_name: str):
    """Read a specific document."""
    if doc_name in docs:
        return {"name": doc_name, "content": docs[doc_name]}
    else:
        raise mcp.ResourceNotFound(f"Document '{doc_name}' not found.")
    

mcp_server = mcp.streamable_http_app()