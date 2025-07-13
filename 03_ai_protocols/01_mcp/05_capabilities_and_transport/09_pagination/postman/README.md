# MCP Pagination Postman Tests 🧪

This Postman collection provides a simple, hands-on way to test the spec-compliant, cursor-based pagination.

## 🚀 **Quick Setup**

### 1. Import the Collection

1.  Open Postman.
2.  Click `Import` and select the `MCP_Pagination_Tests.postman_collection.json` file.
3.  The collection will appear in your workspace.

### 2. Start the MCP Server

In your terminal, navigate to the `mcp_pagination_server` directory and start the server:

```bash
# From the 12_pagination directory
cd mcp_pagination_server
uv run server.py
```

The server will start on `http://localhost:8000`.

## 🧪 **Pagination Test Flow**

This collection demonstrates how to page through a large list of tools using a cursor.

1.  **`1. Initialize Session`**: This is the first request you should send. It establishes a session with the server and automatically saves the `mcp-session-id` and clears any old cursor from previous runs.

2.  **`2. List Tools (First Page)`**: This request fetches the first page of tools. Its test script will automatically find the `nextCursor` in the response and save it to a collection variable.

3.  **`3. List Tools (Next Page)`**: This request uses the `{{nextCursor}}` variable to ask the server for the next page. You can **run this request repeatedly** to page through the entire list of tools. Each time you send it, the test script will update the `nextCursor` variable.

When you reach the end of the list, the server will stop returning a `nextCursor`, the variable will be cleared, and subsequent requests will return an empty list of tools. Check the Postman Console to see the cursors being set. 