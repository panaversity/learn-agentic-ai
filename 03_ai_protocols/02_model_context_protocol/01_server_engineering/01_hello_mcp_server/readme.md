# 01: Hello, MCP Server!

**Objective:** Get your first, very basic Model Context Protocol (MCP) server running using the `FastMCP` library in a simplified **stateless** mode.

## 🧠 Understanding MCP Fundamentals

Before we build anything, let's understand **what MCP is and why it matters** for students new to both MCP and AI development.

### 🤔 What is MCP? (The Simple Explanation)

Think of MCP (Model Context Protocol) as a **universal translator between AI models and the world around them**. 

**Real-World Analogy**: Imagine you're a tour guide (AI model) in a foreign country. Without MCP, you can only answer questions based on what you memorized before the trip. With MCP, you suddenly have:
- 📱 A smartphone to look up real-time information (Tools)
- 📚 Access to local guidebooks and maps (Resources)  
- 🗣️ Ready-made conversation starters for different situations (Prompts)

**For Students Learning OpenAI Agents SDK**: If you're coming from OpenAI Agents SDK, think of MCP as a **standardized way to give your agents superpowers**. Instead of writing custom code for each new capability, MCP provides a standard protocol that works everywhere.

### 🏗️ The Three Building Blocks of MCP

Every MCP server provides one or more of these capabilities:

#### 1. 🔧 **Tools** (What We're Building Today)
- **What**: Functions that AI can call to perform actions
- **Example**: `get_weather(city)` - AI can get real weather data
- **Think of it as**: Giving the AI a toolbox it can use
- **In OpenAI terms**: Like function calling, but standardized across all AI platforms

#### 2. 📚 **Resources** (Lesson 03)
- **What**: Data and documents the AI can read for context
- **Example**: Company knowledge base, user files, database records
- **Think of it as**: Giving the AI a library to reference
- **In OpenAI terms**: Like RAG (Retrieval Augmented Generation), but standardized

#### 3. 💬 **Prompts** (Lesson 04)
- **What**: Template conversations that guide AI interactions
- **Example**: "Summarize this document in bullet points"
- **Think of it as**: Giving the AI conversation scripts
- **In OpenAI terms**: Like system prompts, but reusable and shareable

### 🌐 MCP vs. What You Might Know

| **If you know...** | **MCP is like...** | **Key difference** |
|-------------------|-------------------|-------------------|
| **REST APIs** | A standard protocol, but for AI-tool communication | Designed specifically for AI interactions |
| **OpenAI Function Calling** | Function calling that works with any AI model | Universal, not tied to one provider |
| **Webhooks** | Two-way communication between AI and external systems | Structured specifically for AI use cases |
| **Plugin Systems** | A plugin system for AI models | Cross-platform and standardized |

This initial step focuses on the bare essentials:
1.  Creating a server that handles each request independently.
2.  Defining a single, simple tool.
3.  Making the server accessible over Stateless Streamable HTTP.
4.  Interacting with it using a spec-compliant client that correctly performs the `initialize` handshake.

This serves as the "Hello, World!" for MCP development. It provides the simplest possible server configuration while teaching the correct client-side interaction flow.

## Key MCP Concepts

-   **`FastMCP` Server:** A Python library that handles the low-level details of the MCP `2025-06-18` specification.
-   **Stateless HTTP Transport (`stateless_http=True`):** A convenience mode in `FastMCP` where the server treats every request as a new, independent interaction. It handles and then immediately forgets the session, which is perfect for learning the basic request-response pattern without managing persistent state.
-   **`@mcp.tool()` Decorator:** The primary mechanism in `FastMCP` for exposing a Python function as a tool that AI agents can discover and call.
-   **`initialize`:** The mandatory first request in any MCP interaction. Even though our server is in stateless mode, a compliant client **MUST** always send this first, followed by `notifications/initialized`.
-   **`tools/list`:** The standard MCP method a client uses to ask a server, "What can you do?".
-   **`tools/call`:** The standard MCP method a client uses to execute a specific tool by name.
-   **Structured Tool Output (NEW in 2025-06-18):** Tools can now return structured content arrays instead of simple strings, enabling richer responses with metadata.
-   **Protocol Version Headers (NEW in 2025-06-18):** HTTP requests must include `MCP-Protocol-Version` header for proper version negotiation.
-   **Title Fields (NEW in 2025-06-18):** Servers and tools can now provide human-friendly `title` fields alongside programmatic `name` fields.

## Implementation Plan

Inside the `hello-mcp/` subdirectory, we will:

-   **`server.py`:**
    -   Instantiate a `FastMCP` server in stateless mode (`stateless_http=True`).
    -   Define a simple function like `get_forecast(city: str)` and expose it as a tool using the `@mcp.tool()` decorator.
    -   Expose the server as a runnable ASGI application for `uvicorn`.

-   **`client.py`:**
    -   A simple Python script that uses `httpx` to make JSON-RPC requests.
    -   It will first call `initialize` to follow the spec.
    -   It will then call `tools/list` to discover the `get_forecast` tool.
    -   It will then call `tools/call` to execute the tool and print the result.

-   **Postman Collection:**
    -   The `postman/` directory contains a collection to demonstrate the spec-compliant, three-step interaction flow visually.

## Key Concepts

- **`FastMCP`:** A Python library designed to simplify the creation of MCP-compliant servers. It handles much of the underlying MCP protocol complexities, allowing you to focus on defining your server's capabilities.
- **Server Instantiation:** Creating an instance of the `FastMCP` application.
- **Server Metadata:** Providing basic information about your server (like its name and version) that it will share with clients during initialization.

## Steps

1.  **Setup:**

    - Ensure you have Python installed (Python 3.12+ recommended)and uv.

    ```bash
    uv init hello-mcp
    cd hello-mcp
    ```

2.  **Installation:**

    - Install the necessary packages using `uv`:

      ```bash
      uv add mcp uvicorn httpx
      ```

3.  Update (`server.py`):

    - We will import `FastMCP` and create a simple tool with the stateless http protocol.

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="weather-server",
    stateless_http=True
)


@mcp.tool()
async def get_forecast(city: str) -> list[TextContent]:
    """Get weather forecast for a city with structured output.

    Args:
        city: The name of the city to get weather for
        
    Returns:
        Structured content with weather information
    """
    # Demonstrate structured tool output (new in 2025-06-18)
    forecast_text = f"🌤️ Weather forecast for {city}:\n\n"
    forecast_text += f"Today: Warm and sunny, 75°F (24°C)\n"
    forecast_text += f"📍 Data source: Local Weather Station for {city}"
    
    # Return structured content (new in 2025-06-18)
    return [
        TextContent(
            type="text",
            text=forecast_text
        )
    ]

mcp_app = mcp.streamable_http_app()
```

4.  **Run the Server:**

    - Execute the command:

      ```bash
      uv run uvicorn server:mcp_app --port 8000 --reload
      ```

    - This will start:
      - MCP server at: http://localhost:8000
      

5.  **Test the MCP Server:**
    
    **Option 1: Python Client (Programmatic)**
    ```bash
    uv run python client.py
    ```

    **Option 2: Postman (Visual & Educational) - RECOMMENDED FOR LEARNING**
    1. Install Postman from [postman.com](https://www.postman.com/downloads/)
    2. Import the collection: `postman/Hello_MCP_Server.postman_collection.json`
    3. Run requests in sequence to understand MCP protocol
    4. See detailed documentation in `postman/README.md`

    **Option 3: MCP Inspector (Interactive)**
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    - Run and Open MCP Inspector at: http://127.0.0.1:6274
    - Select Tools Tab and list and run the tool

## 🎓 Why Use Postman for Learning?

**Postman provides the best educational experience** because it:
- **Visualizes the Protocol**: See raw JSON-RPC requests and responses, including the full `initialize` lifecycle.
- **Hands-on Learning**: Modify parameters and experiment easily
- **Better Debugging**: Clear error messages and response inspection
- **No Coding Required**: Focus on understanding MCP without Python complexity
- **Shareable**: Export collections to share with classmates/students

**Learning Path**:
1. Start with Postman to understand the protocol
2. Move to Python client to see programmatic usage
3. Use MCP Inspector for debugging later and testing

This "Hello, MCP Server!" example lays the groundwork. In subsequent sections, we'll build upon this to add tools, resources, and prompt templates, making our server progressively more useful to AI agents.

## 🔗 Next Steps

- **02_defining_tools**: Learn to create more complex tools with different data types.