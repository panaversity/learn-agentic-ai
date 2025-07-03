# 02: Elicitation

**Objective:** Learn how to use the `elicitation/create` feature, which enables an MCP server to request additional information or confirmation from the user through the client application's native UI.

Elicitation is a powerful mechanism for creating interactive tools that can handle ambiguity or require user consent for sensitive actions.

## Key MCP Concepts

-   **`elicitation/create` (Request):** The server-to-client request used to ask the user a question. The request can include a message and define the expected response format (e.g., a simple text input, a choice from a list, a confirmation button).
-   **Interactive Tools:** Tools that can pause their execution to wait for user input, making them more robust and user-friendly.
-   **User Interface Integration:** The client application is responsible for rendering a native UI element (like a dialog box, a form, or a quick-pick menu) to present the elicitation request to the user.
-   **Out-of-Band Data:** Elicitation allows the server to gather information that wasn't provided in the initial tool call, resolving ambiguity or gathering necessary credentials.

## Implementation Plan

-   **`server.py`:**
    -   Will define a tool, for example, `delete_file(path: str)`.
    -   Inside the tool, before performing the deletion, it will construct an elicitation request to ask for user confirmation.
    -   It will call `ctx.elicitation.create(...)` with a message like "Are you sure you want to delete {path}?" and expect a boolean response.
    -   The tool will only proceed with the deletion if the user confirms via the elicitation response.

-   **`client.py`:**
    -   Will need to declare its `elicitation` capability during initialization.
    -   Will provide a handler for incoming `elicitation/create` requests.
    -   For this lesson, our handler will be a simple command-line prompt (`input()`) that displays the server's message and waits for the user to type "yes" or "no".
    -   The client script will call the `delete_file` tool and the user will see the confirmation prompt directly in their terminal. 