from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", stateless_http=True)

docs = {
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource(
    "docs://{doc_id}",
    mime_type="text/plain"
)
def get_doc(doc_id: str) -> str:
    return docs[doc_id]

# Transport -> Get Starlette instance
mcp_app = mcp.streamable_http_app()
