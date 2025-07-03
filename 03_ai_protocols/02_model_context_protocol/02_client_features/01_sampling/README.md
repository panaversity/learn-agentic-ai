# 01: Sampling

**Objective:** Understand and implement the `sampling/create` feature, which allows an MCP server to request an LLM inference from the client.

This powerful feature enables the creation of "agentic" tools—tools that can "think" or perform complex reasoning by leveraging the client's LLM capabilities to process information or generate content.

## Key MCP Concepts

-   **`sampling/create` (Request):** The server-to-client request that contains a prompt and asks the client to generate a completion using its own LLM.
-   **Agentic Tools:** Tools that are not purely deterministic. They can use LLM reasoning as part of their execution flow, making them far more flexible and powerful.
-   **Separation of Concerns:** The server holds the logic and context, while the client (the LLM application) holds the powerful (and potentially expensive) LLM. The server asks, and the client executes the inference.
-   **Security and Consent:** The MCP specification emphasizes that clients **MUST** obtain user consent before executing a sampling request, as it often involves API costs and data sharing.

## Implementation Plan

-   **`server.py`:**
    -   Will define a tool, for example, `create_story(topic: str)`.
    -   Inside this tool, it will construct a prompt (e.g., "Write a short, three-sentence story about {topic}.").
    -   It will then use the `Context` object to call `ctx.sampling.create(...)`, sending the prompt to the client.
    -   The tool will wait for the client to return the LLM-generated story and then return this story as the tool's final output.

-   **`client.py`:**
    -   When initializing the connection, the client will need to declare its `sampling` capability.
    -   The `mcp.client` library, when properly configured with an LLM (like an `openai.AsyncOpenAI` client), will automatically handle the incoming `sampling/create` request. It will call the LLM with the prompt received from the server and send the result back.
    -   Our client script will simply call the `create_story` tool and print the final story, demonstrating the complete round-trip flow. 