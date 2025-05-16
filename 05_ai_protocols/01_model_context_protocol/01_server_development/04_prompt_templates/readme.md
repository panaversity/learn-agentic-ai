# 04: Offering [MCP Prompt Templates](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts): Guiding AI Interactions

**Objective:** This guide will teach you how to define, register, and expose MCP Prompt Templates from your `FastMCP` server. Prompt templates provide structured starting points for interactions, making it easier for clients (including AI agents and users) to leverage your server's capabilities for common tasks.

**Recap from "Exposing MCP Resources":** We've learned how to provide contextual data (Resources) to agents. Now, we'll explore how to offer pre-defined interaction patterns (Prompt Templates) that can guide how agents or users formulate requests or instructions, often incorporating tools and resources.

## Core Concepts for MCP Prompt Templates

### What are MCP Prompt Templates?

MCP Prompt Templates are server-defined structures that help clients construct messages for language models or initiate specific interaction flows. They are uniquely identified by a `name` and can include a `description` and a list of `arguments` for customization. When a client requests a prompt template using `prompts/get` (providing any necessary arguments), the server returns a structured list of `PromptMessage` objects.

- **Reference:** [MCP Specification - Prompts](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts)
- **Purpose:**
  - **Simplify Common Tasks:** Offer ready-to-use starting points for frequent interactions.
  - **Ensure Consistency:** Guide users/AIs to provide necessary information in the correct format.
  - **Enhance Discoverability:** Showcase common ways to utilize the server's tools and resources.
  - **Improve LLM Interaction:** Provide LLMs with well-structured prompts.

### Structure of a Prompt Template

When a client calls `prompts/get`, the `result` contains:

- **`description` (str, optional):** Human-readable explanation of the specific rendered prompt.
- **`messages` (list):** An array of `PromptMessage` objects that form the conversation starter. Each `PromptMessage` has:
  - `role` (str): `"user"` or `"assistant"`, indicating the sender.
  - `content`: The actual content of the message, which can be of various types:
    - **Text Content:** `{"type": "text", "text": "..."}`
    - **Image Content:** `{"type": "image", "data": "base64...", "mimeType": "image/png"}`
    - **Audio Content:** `{"type": "audio", "data": "base64...", "mimeType": "audio/wav"}`
    - **Embedded Resources:** `{"type": "resource", "resource": {"uri": "...", "mimeType": "...", "text": "..."}}` (Allows direct inclusion of MCP Resources).
- **Reference:** [MCP Specification - Prompt Data Types](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#data-types)

For `prompts/list`, each prompt entry includes:

- **`name` (str):** Unique identifier for the prompt template (e.g., `"summarize_text"`, `"code_reviewer"`).
- **`description` (str, optional):** Human-readable explanation of what the prompt template does.
- **`arguments` (list, optional):** Defines parameters the client can provide to customize the prompt. `FastMCP` typically infers these from the type hints of your Python function. Each argument entry details its `name`, `description`, and whether it's `required`.

### Server Capabilities

Servers supporting prompt templates **MUST** declare the `prompts` capability in their `initialize` response.

- **`listChanged` (bool, optional):** Indicates if the server will send `notifications/prompts/list_changed` when the available templates change.
- **Example:** `{"capabilities": {"prompts": {"listChanged": true}}}`
- **Reference:** [MCP Specification - Capabilities](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#capabilities)

### MCP Prompt Template Operations

- **`prompts/list`:** Clients send this to discover available prompt templates. Supports pagination.
  - **Reference:** [MCP Specification - Listing Prompts](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#listing-prompts)
- **`prompts/get`:** Clients send this with a prompt `name` and filled `arguments` to retrieve the fully rendered prompt (i.e., the list of `PromptMessage` objects within a result structure).
  - **Reference:** [MCP Specification - Getting a Prompt](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#getting-a-prompt)

### Registering Prompt Templates with `FastMCP`

You define prompt templates as Python functions decorated with `@mcp.prompt()`.

- The function arguments (with type hints) become the template's arguments.
- The function's return value (e.g., a `str`, a list of `PromptMessage` objects, or a list of SDK-specific message objects like `base.Message`) is processed by `FastMCP` to form the `messages` array in the `prompts/get` response.
- The decorator can also take `name` and `description` parameters to override defaults inferred from the function name and docstring.

### Error Handling & Security

- Servers should return standard JSON-RPC errors for issues like invalid prompt names or missing arguments.
- Implementations **MUST** validate inputs to prevent injection attacks or unauthorized access, especially when arguments are used to construct messages or embed resources.
- **Reference:** [MCP Specification - Error Handling](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#error-handling) and [Security](https://modelcontextprotocol.io/specification/2025-03-26/server/prompts#security)

## Practical Steps: Building Your Prompt-Enabled Server

1.  **Create Project Directory:**

    ```bash
    uv init my_prompts_server
    cd my_prompts_server
    ```

2.  **Initialize Python Environment with `uv`:**

    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate    # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    uv add "mcp[cli]"
    ```

    - `mcp[cli]`: The core MCP SDK with `FastMCP`.

4.  **Create `main.py`:** This file will contain your server logic and prompt template definitions.

5.  **Populate `main.py`:** Refer to the "Full Code Example" section below. It will demonstrate:

    - Importing necessary types from `mcp.types` and `mcp.server.fastmcp.prompts`.
    - Creating functions that generate prompt content (string or message lists).
    - Registering these functions as prompt templates with `FastMCP` using `@mcp.prompt()`.

6.  **Running Your MCP Server:**

    ```bash
    uv run mcp dev main.py
    ```

    This starts your server and the MCP Inspector.

7.  **Testing Your Prompt Templates:**
    - Open the MCP Inspector in your browser.
    - Navigate to the "Prompt Templates" section (or similar, depending on Inspector version).
    - **List Templates:** Verify that your defined templates appear (e.g., `review_code`, `debug_error`, `code_reviewer`).
    - **Get Template:** Select a template. If it has arguments (like `code_reviewer`), the Inspector should allow you to input them. Execute to see the rendered `PromptMessage` structure in the JSON response.

## Full Code Example (`my_prompts_server/main.py`)

````python
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

# To make the server runnable with `uv run mcp dev main.py`
# FastMCP automatically provides the ASGI app, so an explicit `app = mcp.asgi_app()`
# is often not needed in main.py when using `mcp dev`.
````

## Key Takeaways

- MCP Prompt Templates standardize how clients request LLM interactions or initiate common server tasks by defining functions decorated with `@mcp.prompt()`.
- `FastMCP` infers template `name`, `description` (from docstring), and `arguments` (from function signature and type hints). These can be overridden in the decorator.
- The decorated function's return value (`str`, `list[PromptMessage]`, or `list[mcp.server.fastmcp.prompts.base.Message]`) is transformed by `FastMCP` into the `messages` array for the `prompts/get` response.
- `PromptMessage` objects have a `role` and `content` (which can be `TextContent`, `ImageContent`, `AudioContent`, or `ResourceContent`).
- Servers declare a `prompts` capability. Clients use `prompts/list` to discover templates and `prompts/get` (with arguments) to retrieve the rendered messages.

## Next Steps

You've now covered the essentials of MCP server development: setting up a server, defining tools, exposing resources, and offering prompt templates!

Consider exploring:

- **Advanced Prompt Content:** Experiment with `ImageContent`, `AudioContent`, or `ResourceContent` within your prompt messages.
- **More Complex Argument Types:** Using more complex data types for arguments if needed, and how `FastMCP` handles their schema generation.
- **Dynamic Prompt Logic:** Implementing more intricate logic within your Python functions that generate prompt content based on arguments or server state.
- **Client-Side Usage:** How a client application would effectively interact with these prompt templates.
