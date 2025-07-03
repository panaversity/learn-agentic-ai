from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base as mcp_messages

# Initialize a stateless FastMCP server
mcp = FastMCP(
    name="my-prompts-server",
    description="A simple server to demonstrate defining and using MCP Prompt Templates.",
    stateless_http=True
)

# --- Prompt 1: A simple prompt that returns a single string ---
# This is the most basic form. The string becomes the content of a single user message.
@mcp.prompt()
def summarize(text: str) -> str:
    """
    Creates a prompt asking an AI to summarize the provided text.
    
    Args:
        text: The text to be summarized.
    """
    return f"Please summarize the following text in three bullet points:\n\n---\n{text}\n---"

# --- Prompt 2: A more complex prompt that returns a list of messages ---
# This is useful for setting up a multi-turn conversation or providing examples.
@mcp.prompt()
def debug_error(error_message: str, code_snippet: str) -> list[mcp_messages.Message]:
    """
    Creates a conversation to start debugging an error.

    Args:
        error_message: The error message that was observed.
        code_snippet: The relevant code that produced the error.
    """
    return [
        mcp_messages.UserMessage(f"I'm running into an issue with this code:\n\n```\n{code_snippet}\n```"),
        mcp_messages.UserMessage(f"It's producing the following error:\n\n{error_message}"),
        mcp_messages.AssistantMessage("I see. Let's debug this. Can you tell me what you've already tried to do to fix it?")
    ]

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()