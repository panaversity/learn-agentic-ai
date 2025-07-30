# MCP Completions Server - Postman Testing (Stateful)

This collection demonstrates how to test MCP completions using a stateful lifecycle via HTTP endpoints.

## 🚀 Quick Start

### 1. Start the Server
```bash
cd mcp_completions_server
uv run server.py
```
Server runs on `http://localhost:8000`

### 2. Run the Collection
1.  **Import Collection**: Import this file into Postman.
2.  **Run Lifecycle Requests**: Execute the requests in the "1. Connection Lifecycle" folder in order.
    -   The `Initialize Connection` request will automatically capture and set the `mcp_session_id` collection variable.
3.  **Test Completions**: Run any of the requests in the "Prompt Completions" or "Resource Completions" folders. They will use the captured session ID.

## 🎯 Testing Workflow

The collection is organized to follow the MCP session lifecycle:

### 1. Connection Lifecycle
-   **Initialize Connection**: Establishes a session with the server and gets a session ID.
-   **Send Initialized Notification**: Tells the server the client is ready.

### 2. Server Discovery
-   **List Prompts / Resources**: Asks the server what prompts and resources are available in this session.

### 3. Completions
-   Run individual completion requests for prompts and resources. Each request is a JSON-RPC call to the `/mcp/` endpoint.

## 📚 Learning Points

### 1. Stateful Lifecycle
-   All communication happens within a session, identified by `mcp-session-id`.
-   The `initialize` request is mandatory before any other calls can be made.

### 2. JSON-RPC Format
-   All requests after `initialize` are `POST` requests to `/mcp/` with a JSON-RPC body.
-   The `method` field specifies the operation (e.g., `complete`, `prompts/list`).
-   The `params` field contains the arguments for that method.

### Example `complete` request:
```json
{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "complete",
    "params": {
        "ref": { "type": "ref/prompt", "name": "review_code" },
        "argument": { "name": "language", "value": "py" }
    }
}
```

### 3. Automated Session Handling
-   The test script in the `Initialize Connection` request automates session ID handling:
    ```javascript
    const sessionId = pm.response.headers.get('mcp-session-id');
    pm.collectionVariables.set('mcp_session_id', sessionId);
    ```
-   All subsequent requests use `{{mcp_session_id}}` in their headers.

## 🔧 Customization

-   To start a new test session, simply re-run the `Initialize Connection` request.
-   Add new completion tests by duplicating an existing request and modifying the `params` in the request body.

## 🎓 Next Steps

-   **Explore Errors**: Try sending a `complete` request with an invalid session ID to see how the server responds.
-   **Check Other Examples**: Review other Postman collections in the project to see more complex lifecycle interactions. 