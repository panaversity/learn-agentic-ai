# 03: Roots

**Objective:** Learn to use the `roots/list` feature, which allows an MCP server to discover the user's workspaces, projects, or other high-level contextual boundaries from the client.

This feature is fundamental for tools that need to operate on a collection of files or within a specific project context, such as linters, search tools, or refactoring agents.

## Key MCP Concepts

-   **`roots/list` (Request):** The server-to-client request to get a list of the user's "root" contexts.
-   **Resource URI:** A "root" is represented as a resource with a URI, typically a `file://` scheme pointing to a directory.
-   **Contextual Awareness:** This feature makes a server "contextually aware." It's not just executing blind commands; it knows the boundaries of the user's current project.
-   **User-Provided Context:** The list of roots is determined entirely by the client application (e.g., the folders a user has opened in their IDE). The server simply asks for this list.

## Implementation Plan

-   **`server.py`:**
    -   Will define a tool, for example, `list_project_files()`.
    -   Inside the tool, it will first call `ctx.roots.list()` to get the list of open project folders from the client.
    -   For this example, it will assume there is at least one root. It will take the first root's URI.
    -   It will then use standard Python libraries (`os.walk` or `pathlib`) to scan the directory specified by the root's URI and return a list of all files within that project.

-   **`client.py`:**
    -   Will need to declare its `roots` capability during initialization.
    -   Will provide a handler for incoming `roots/list` requests.
    -   For our simple command-line client, the handler will be hardcoded to return a list containing a single root: the current working directory (`pathlib.Path.cwd().as_uri()`).
    -   In a real application like an IDE, this handler would return the list of currently opened project folders.
    -   The client script will call `list_project_files()` and print the list of files returned by the server, which originates from the context provided by the client itself. 