# 07: Tool Update Notification

**Objective:** Learn how a server can proactively notify a client when its toolset has changed, avoiding the need for the client to poll `tools/list` repeatedly.

This is critical for dynamic environments where tools might be added or removed based on user permissions, system state, or other external factors.

## Key MCP Concepts

-   **`tools/didChange` (Notification):** The core server-to-client notification that signals a change in the available tools.
-   **Dynamic Tool Management:** The server-side logic for adding or removing tools from the registry after the initial handshake.
-   **Client-Side State Synchronization:** The client's responsibility to update its local understanding of available tools upon receiving a `didChange` notification.

## Implementation Plan

-   **`server.py`:**
    -   Will expose an initial set of tools.
    -   Will include a mechanism (e.g., a simple HTTP endpoint or a timed event) to trigger the addition or removal of a tool.
    -   Upon change, it will broadcast a `tools/didChange` notification to all connected clients.

-   **`client.py`:**
    -   Will connect and list the initial set of tools.
    -   Will listen for the `tools/didChange` notification.
    -   When the notification is received, it will automatically call `tools/list` again to refresh its state and print the updated toolset. 