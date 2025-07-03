# 13: Pagination

**Objective:** Learn how to use pagination for `resources/list` and `tools/list` requests to efficiently handle MCP servers that expose a very large number of items.

This is a crucial pattern for performance and scalability, ensuring that clients are not overwhelmed by a massive initial payload.

## Key MCP Concepts

-   **Pagination Parameters (`limit`, `offset`):**
    -   `limit`: The client specifies the maximum number of items to receive in a single response.
    -   `offset`: The client specifies the starting point in the collection for the requested items.
-   **`has_more` Field:** The server includes this boolean in its response to indicate whether more items are available beyond the current page.
-   **Client-Side Looping:** The client is responsible for making subsequent requests with an updated `offset` until `has_more` is `false` to fetch the complete list.

## Implementation Plan

-   **`server.py`:**
    -   Will be seeded with a large number of dummy tools or resources (e.g., 100+).
    -   The implementation of the `resources/list` and `tools/list` handlers will be modified to:
        -   Accept `limit` and `offset` parameters from the client's request.
        -   Slice the full list of items according to these parameters.
        -   Include the `has_more` flag in the response.

-   **`client.py`:**
    -   Will implement a loop to fetch all resources or tools page by page.
    -   It will start with an initial `offset` of 0 and a chosen `limit`.
    -   In each iteration, it will process the received page of items and then increment the `offset` for the next request, continuing as long as the server indicates `has_more: true`.
    -   The client will print its progress as it fetches each page. 