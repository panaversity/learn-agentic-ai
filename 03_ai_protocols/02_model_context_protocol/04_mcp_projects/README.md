# 05: MCP Projects

**Objective:** Apply the knowledge gained from the previous sections to build practical, real-world projects that solve complex problems using the Model Context Protocol.

This section serves as a "capstone" where we integrate multiple MCP features—tools, resources, prompts, and security—into complete, useful applications. The projects here will be more open-ended and focus on architecture and creative problem-solving.

## Project Ideas

This directory will house one or more larger projects. Potential ideas include:

### 1. **DACA-Aligned Codebase Assistant**
-   **Concept:** An agentic assistant that can read, analyze, and answer questions about a local codebase.
-   **MCP Features Used:**
    -   **Server:** Exposes tools for file system access (`read_file`, `list_directory`), code parsing (AST), and analysis.
    -   **Client:** Uses `roots` to identify the project directory. Implements `sampling` to allow the server's tools to use the client's LLM for code summarization or analysis.
    -   **Auth:** The server is protected via OAuth, ensuring only authorized clients can access the codebase.

### 2. **Interactive Database Query Agent**
-   **Concept:** An MCP server that provides tools to query a SQL database, but uses elicitation to confirm destructive actions.
-   **MCP Features Used:**
    -   **Server:** Exposes a `query(sql: str)` tool. It parses the SQL and if it detects a `DROP`, `DELETE`, or `UPDATE` command, it uses `elicitation` to ask the user for confirmation.
    -   **Client:** Implements a handler for the elicitation request, showing a confirmation dialog to the user.
    -   **Resources:** Exposes the database schema as a read-only resource (`resources/read`).

### 3. **Multi-Agent System with A2A Protocol**
-   **Concept:** A more advanced project demonstrating how multiple, independent MCP servers can collaborate using the Agent-to-Agent (A2A) protocol, with one server acting as a client to another.
-   **MCP Features Used:**
    -   **Server A (Orchestrator):** Exposes a high-level tool like `plan_trip(destination: str)`.
    -   **Server B (Flight Booker):** Exposes a tool to find flights.
    -   **Server C (Hotel Booker):** Exposes a tool to find hotels.
    -   **Workflow:** The Orchestrator server, when its `plan_trip` tool is called, acts as an MCP *client* to discover and call the tools on the Flight and Hotel booking servers.

## Implementation Plan

For each project, we will create a dedicated subdirectory containing:
-   A detailed `README.md` explaining the project's architecture and setup.
-   All necessary server and client code.
-   `pyproject.toml` and `uv.lock` files for dependency management.
-   Postman collections for testing, where applicable. 