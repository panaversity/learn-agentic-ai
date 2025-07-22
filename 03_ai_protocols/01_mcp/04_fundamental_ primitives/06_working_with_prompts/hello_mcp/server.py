from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.types import PromptMessage, TextContent

mcp = FastMCP("DocumentMCP", stateless_http=True)

docs = {
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_content: str = Field(description="Contents of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The contents of the document you need to reformat is:
    <document_content>
    {doc_content}
    </document_content>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """

    return [base.UserMessage(prompt)]

@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of the document."
)
def summarize_document(doc_content: str = Field(description="Contents of the document to summarize")) -> list[PromptMessage]:

    prompt_text = f"""
    Your goal is to summarize the contents of the document.
    Document Contents: {doc_content}
    Include a concise summary of the document's main points.
    """
    return [PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))]


# Transport -> Get Starlette instance
mcp_app = mcp.streamable_http_app()
