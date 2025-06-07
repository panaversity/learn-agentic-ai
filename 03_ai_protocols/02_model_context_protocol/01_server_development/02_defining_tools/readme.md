# 02: [Defining MCP Tools](https://modelcontextprotocol.io/specification/2025-03-26/server/tools): Enabling Agent Actions

**Objective:** This step will guide you through defining, registering, and annotating executable functions as Model Context Protocol (MCP) Tools. You'll learn to use Pydantic for creating clear input/output schemas, enabling AI agents to discover, understand, and execute these tools effectively.

**Recap from "Hello, MCP Server!":** In the previous step, we successfully set up a basic MCP server with a single tool. Now, it's time to expand our server's capabilities by defining more tools with detailed schemas and behavioral annotations.

## Core Concepts for Creating MCP Tools

### What are MCP Tools?

MCP Tools are Python functions exposed by your `FastMCP` server that an AI client (or an Agent interacting through a client) can request to execute. They are the primary way an AI performs actions, interacts with external systems, or carries out computations via MCP.

- **Reference:** [MCP Specification - Tools](https://modelcontextprotocol.io/specification/2025-03-26/server/tools)

### Defining Tool Logic with Python Functions

The core of an MCP Tool is a Python function (often `async def`, but can be synchronous) that contains the tool's logic.

### Registering Tools with `FastMCP`

You register tools using the `@mcp.tool()` decorator, where `mcp` is your instance of the `FastMCP` class.

- **Key Decorator Arguments:**
  - `name` (str, optional): The unique name (e.g., `add` or `"calculator/add"`). If omitted, `FastMCP` often infers it from the function name (e.g., `get_forecast` becomes `get_forecast`).
  - `description` (str, optional): Human-readable explanation. If omitted, `FastMCP` often infers it from the function's docstring.
  - `annotations` (`ToolInfo.ToolAnnotations`, optional): Metadata about tool behavior (see below).
- `FastMCP` can also infer `parameters_model` from function type hints and `response_model` from the return type hint.

### Tool Annotations (`ToolInfo.ToolAnnotations`)

These provide crucial metadata to clients about a tool's behavior, guiding safe and effective usage. They are defined using the `ToolInfo.ToolAnnotations` class from `mcp.sdk.types`.

- **Purpose:** Help clients/users/LLMs make informed decisions (e.g., warn before running a destructive tool).
- **Common Annotations:**
  - `title: str`: A human-readable title for the tool.
  - `readOnlyHint: bool`: `True` if the tool doesn't modify state.
  - `destructiveHint: bool`: `True` if the tool makes irreversible changes.
  - `idempotentHint: bool`: `True` if repeated calls with the same arguments have no additional effect after the first successful call.
  - `openWorldHint: bool`: `True` if the tool interacts with external, unpredictable entities.
- **Client Responsibility:** Clients should treat annotations as hints and are responsible for how they interpret them, especially regarding security.
- **Reference:** [MCP Specification - ToolInfo](https://modelcontextprotocol.io/specification/2025-03-26/basic/definitions/#toolinfo).

### MCP Tool Operations

- **Discovery (`tools/list`):** Clients use this to get a list of available tools, their schemas, and annotations. `FastMCP` handles this automatically. The server must declare the `tools` capability in its `initialize` response (e.g., `{ "capabilities": { "tools": { "listChanged": false } } }`).
- **Execution (`tools/call`):** Clients use this to run a tool by its `name`, providing `arguments`. `FastMCP` routes this to your Python function.
- **Tool Result Content Types**: Tool results can contain various content types (text, image, resource). `FastMCP` helps serialize Python return values into these structures.

### Basic Error Handling

Python exceptions raised in your tool functions are generally caught by `FastMCP` and converted into structured MCP error responses (Protocol Errors or Tool Execution Errors).

### Security Considerations

- **Servers MUST:** Validate inputs, control access, consider rate limiting, and sanitize outputs.
- **Clients SHOULD:** Prompt for confirmation for sensitive operations, validate results, and log usage.

## Practical Steps: Building Your Multi-Tool Server

1.  **Create Project Directory:**

    ```bash
    uv init my_tools_server
    cd my_tools_server
    ```

2.  **Initialize Python Environment with `uv`:**

    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate    # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    uv add "mcp[cli]" pydantic
    ```

    - `mcp[cli]`: The core MCP SDK with `FastMCP` and CLI tools.
    - `pydantic`: For defining data models/schemas.

4.  **Create `main.py`:**
    This file will contain your server logic.

5.  **Populate `main.py`:**
    Refer to the "Full Code Example" section below which includes:

    - Imports: `FastMCP`, `ServerInfo`, `ToolInfo`, `BaseModel`, `Field`, `datetime`.
    - `ServerInfo` Initialization (good practice).
    - `FastMCP` app instance (e.g., `mcp = FastMCP(...)`).
    - **Tool 1:** `add` (calculator function, inferred name and description).
    - **Tool 2:** `get_forecast` (inferred name, simple string).
    - **Tool 3:** `dummy_data_manager/delete_item` (complex tool with detailed `ToolAnnotations` and explicit Pydantic models for params/response).

6.  **Running Your MCP Server:**
    The simplest way to run and test during development:

    ```bash
    uv run mcp dev main.py
    ```

    This starts your server via stdio and launches the MCP Inspector (e.g., at `http://127.0.0.1:6274`), which should auto-connect to the proxy (e.g., on port 6277).

7.  **Testing Your Tools:**
    - Use the connected MCP Inspector to browse the list of tools.
    - Select a tool to see its description, schema, and annotations.
    - Execute tools by providing parameters in the Inspector's UI.
    - Observe the results and any logs. For `delete_dummy_item`, try executing with `confirm: false` and then `confirm: true`.

## Full Code Example (`my_tools_server/main.py`)

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP(name="my-tools-server", stateless_http=True)


class AddParameters(BaseModel):
    a: int = Field(description="The first number to add")
    b: int = Field(description="The second number to add")


class AddResponse(BaseModel):
    result: int = Field(description="The sum of the two numbers")


@mcp.tool(name="calculator/add", description="Add two numbers together")
def add(parameters: AddParameters) -> AddResponse:
    """Add two numbers together.

    Args:
        a(int): The first number to add
        b(int): The second number to add

    Returns:
        AddResponse: The sum of the two numbers
    """
    return AddResponse(result=parameters.a + parameters.b)


@mcp.tool(name="forecast", description="Get weather forecast for a city")
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    return f"The weather in {city} will be warm and sunny"

# --- Tool 3: Dummy Data Manager - Delete Item (Demonstrates ToolAnnotations) ---
class DeleteItemParameters(BaseModel):
    item_id: str = Field(description="The ID of the dummy item to delete.")
    confirm: bool = Field(
        default=False, description="Confirmation flag to proceed with deletion.")


class DeleteItemResponse(BaseModel):
    status: str = Field(description="The status of the delete operation.")
    message: str = Field(description="A message detailing the outcome.")


@mcp.tool(
    name="dummy_data_manager/delete_item",
    description="Simulates deleting a dummy item by its ID. This tool demonstrates various annotations.",
    annotations=ToolAnnotations(
        title="Delete Dummy Item",
        readOnlyHint=False,  # This tool modifies (simulated) state
        destructiveHint=True,  # This tool simulates a destructive action
        # Calling it again for the same ID after success would be different (e.g., item not found)
        idempotentHint=False,
        openWorldHint=False,  # Operates on a known, internal dummy dataset
        # Example of a custom annotation if your ToolAnnotations model supports 'extra="allow"'
        # and your client/host knows how to interpret it:
        # custom_RequiresPrivilegeLevel="admin"
    )
)
async def delete_dummy_item(params: DeleteItemParameters) -> DeleteItemResponse:
    """
    Simulates deleting a dummy item.

    This tool is intended to showcase how ToolAnnotations can describe
    a tool's behavior, such as being non-read-only and destructive.
    It requires confirmation to proceed.
    """
    if not params.confirm:
        return DeleteItemResponse(
            status="aborted",
            message="Deletion aborted. Confirmation not provided."
        )

    # In a real scenario, you would interact with a database or state store here.
    # For this example, we'll just simulate success.
    print(f"[Server Log] Simulating deletion of item: {params.item_id}")

    return DeleteItemResponse(
        status="success",
        message=f"Successfully simulated deletion of item '{params.item_id}'. (This is a simulation)"
    )
```

## Key Takeaways

- Define tools as Python functions decorated with `@mcp.tool()`.
- Use Pydantic `BaseModel` for clear, validated input and output schemas.
- Leverage `ToolInfo.ToolAnnotations` to describe tool behavior for clients.
- `FastMCP` infers names, descriptions, and schemas if not explicitly provided in `@mcp.tool()`, but explicit definition enhances clarity.
- Test your server easily using `uv run mcp dev main.py` and the MCP Inspector.

## Next Steps

Now that you can create sophisticated tools, the next module, **`03_exposing_resources/`**, will cover how to provide contextual data to AI agents through MCP Resources.