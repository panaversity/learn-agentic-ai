from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base # For base.UserMessage, base.AssistantMessage
from mcp.types import (
    PromptMessage,
    TextContent,
)

# Initialize FastMCP application
mcp = FastMCP(
    name="my-prompts-server",
)

# --- Prompt Template 1: Simple code review (returns string) ---
@mcp.prompt() # Name will be inferred as 'review_code'
def review_code(code: str) -> str:
    """Asks for a review of the provided code."""
    return f"Please review this code:\n\n{code}"

# --- Prompt Template 2: Debug error (returns list of base.Message) ---
@mcp.prompt() # Name will be inferred as 'debug_error'
def debug_error(error: str) -> list[base.Message]:
    """Starts a debugging conversation for a given error."""
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

# --- Prompt Template 3: Code Review Request (returns list of PromptMessage) ---
@mcp.prompt(
    name="code_reviewer", # Explicit name
    description="Generates a prompt to request a review of a code snippet, specifying language and focus areas."
)
async def code_review_prompt_template(code: str, language: str, focus: str) -> list[PromptMessage]: # Type hint for return
    """
    Generates a detailed prompt for requesting a code review.
    """
    prompt_text = (
        f"Please review the following {language} code snippet.\n"
        f"Focus on: {focus}.\n\n"
        f"Code:\n```\n{code}\n```\n\n"
        "Provide feedback on its quality, suggest improvements, and identify any potential issues."
    )
    return [
        PromptMessage(role="user", content=TextContent(text=prompt_text, type='text'))
    ]