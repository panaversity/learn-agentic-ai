# 03: Advanced Client Features

**Objective:** Explore the advanced, client-centric features of the Model Context Protocol: `sampling`, `elicitation`, and `roots`.

In the previous section, the server was the primary provider of capabilities. Here, the roles are partially reversed. These features enable the **server to request actions from the client**, allowing for more dynamic, interactive, and powerful collaborative workflows between the server and the LLM application.

## Key Concepts

This section covers features where the server initiates a request to the client:

-   **`sampling/create` (Client Feature):** Allows a server to ask the client's host application to perform an LLM inference (a "sample"). This is essential for agentic behaviors, where a tool might need to "think" or consult an LLM to complete its work. The server provides the prompt, but the client controls the execution.

-   **`elicitation/create` (Client Feature):** Enables a server to request additional, out-of-band information from the user via the client. This is how a tool can ask clarifying questions (e.g., "Which file do you mean?" or "Please provide your API key") through a native UI element in the client application.

-   **`roots/list` (Client Feature):** Allows a server to discover the user's workspaces or contexts (e.g., open project folders, database connections) from the client. This is crucial for tools that need to operate within a specific user context, like a code refactoring tool needing to know the project's root directory.

## Learning Path

We will explore each of these powerful features in dedicated, hands-on lessons:

1.  **`01_sampling`:** Implement a tool that uses the client's LLM to generate creative text.
2.  **`02_elicitation`:** Build a tool that asks the user for confirmation before performing a destructive action.
3.  **`03_roots`:** Create a tool that lists the contents of a project directory provided by the client. 