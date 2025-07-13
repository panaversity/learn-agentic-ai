from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base as mcp_messages


# Initialize FastMCP server with enhanced 2025-06-18 metadata
mcp = FastMCP(
    name="my-prompts-server",
    stateless_http=True
)


@mcp.prompt(
    name="summarize",
    title="Simple Text Summarization",  # For Postman compatibility
    description="Basic text summarization prompt for educational purposes"
)
def summarize(text: str) -> str:
    """
    Simple text summarization prompt that matches Postman collection expectations.

    Args:
        text: The text content to be summarized

    Returns:
        A basic summarization prompt
    """
    return f"""Please provide a clear and concise summary of the following text: {text}
Focus on the main points and key information. Keep the summary informative but brief."""


@mcp.prompt(
    name="debug_error",
    title="Simple Debugging Help",  # For Postman compatibility
    description="Basic debugging conversation starter for educational purposes"
)
def debug_error(error_message: str, code_snippet: str) -> list[mcp_messages.Message]:
    """
    Simple debugging conversation that matches Postman collection expectations.

    Args:
        error_message: The error that occurred
        code_snippet: The code that caused the error

    Returns:
        A basic debugging conversation
    """
    return [
        mcp_messages.UserMessage(
            content=f"""I'm having trouble with this code. Here's the error I'm getting:
**Error:** {error_message}
**Code:** {code_snippet}

Can you help me understand what's wrong and how to fix it?"""
        ),

        mcp_messages.AssistantMessage(
            content=f"""I can help you debug this issue. Let me analyze the error and code:
The error '{error_message}' suggests there's an issue with the code logic.Let's work through this step by step."""
        )
    ]



# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()
