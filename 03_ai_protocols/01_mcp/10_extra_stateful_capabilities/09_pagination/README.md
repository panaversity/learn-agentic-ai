# 12: MCP Pagination

This example demonstrates how to implement server-side pagination for `tools/list` and `resources/list` requests, a crucial feature for any MCP server that manages a large number of items. Pagination allows clients to fetch large datasets in smaller, manageable chunks, improving performance and reliability.

This lesson uses the **cursor-based** model mandated by the `2025-06-18` MCP specification. We use the low-level `mcp.server.lowlevel.Server` to demonstrate how to implement the pagination logic manually, combined with the `StreamableHTTPSessionManager` to expose it over the web.

The server exposes a list of 150 dummy tools and resources, and the client fetches them in pages of 20.


## Key Concepts

-   **Cursor-Based Pagination**: The server provides an opaque `nextCursor` in its response. The client sends this cursor back in its next request to get the subsequent page.
-   **Stateful Cursor**: The cursor is a base64-encoded JSON string containing the next page number. This allows the server to remain stateless while providing the client with the means to continue where it left off.
-   **PaginatedRequest**: The `mcp.types.ListToolsRequest` and `mcp.types.ListResourcesRequest` types inherit from `PaginatedRequest`, which provides the `params` field for the client to send the cursor.

## How to Run This Example

### 1. Start the Server

Navigate to this directory and start the Uvicorn server:

```sh
cd mcp_pagination_server
uvicorn server:app --reload
```

The server will start on `http://127.0.0.1:8000`.

### 2. Run the Client

In a separate terminal, run the Python client:

```sh
cd mcp_pagination_server
uv run python client.py
```

You will see the client connect to the server and fetch all 150 tools in 8 pages (7 pages of 20, and 1 page of 10).

### 3. Test with Postman

You can also test the server's pagination endpoints using the provided Postman collection.

1.  Import the collection from the `postman/` directory into your Postman client.
2.  Run the "Get Tools (Page 1)" request.
3.  Copy the `nextCursor` value from the response body.
4.  Paste it into the `cursor` field in the body of the "Get Tools (Page 2)" request and send it.
5.  Repeat this process to paginate through all the tools. 