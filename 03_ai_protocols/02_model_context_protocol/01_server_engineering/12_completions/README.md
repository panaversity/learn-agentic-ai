# 12: Completions

**Objective:** Understand how to implement the `completions/` utility, which allows an MCP server to leverage a client's Large Language Model (LLM) for complex data processing, reasoning, or content generation tasks.

This turns the client from a simple consumer of tools into a powerful, collaborative partner for the server.

## Key MCP Concepts

-   **`completions/create` (Request):** The server-to-client request used to ask the client's LLM to complete a prompt.
-   **Prompt Engineering:** The server is responsible for constructing a high-quality prompt that includes all necessary context for the LLM to perform its task.
-   **Structured Data Exchange:** The flow of passing data from the server to the client's LLM and receiving the structured output back.
-   **Use Cases:** Ideal for tasks like summarizing complex data, transforming data formats, or generating creative content based on resources available only to the server.

## Implementation Plan

-   **`server.py`:**
    -   Will define a tool (e.g., `analyze_document`) that takes some input.
    -   Inside this tool, the server will construct a detailed prompt and use the `completions/create` method on the `Context` object (`ctx.completions.create(...)`) to ask the client's LLM to perform an analysis.
    -   The tool will then process the LLM's response and return a final result to the original caller.

-   **`client.py`:**
    -   The `mcp.client` library will handle responding to the `completions/create` request automatically by calling the configured LLM (e.g., an OpenAI model).
    -   Our client script will simply call the `analyze_document` tool and print the final, processed result returned by the server. We will see the "magic" of the server using our client's LLM behind the scenes. 