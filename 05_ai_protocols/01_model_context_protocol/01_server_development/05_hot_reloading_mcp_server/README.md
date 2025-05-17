# 05: Hot Reloading MCP Server

**Objective:** To understand and demonstrate how to run an MCP server with hot reloading enabled for a faster development lifecycle.

This module concludes the `01_server_development` section by showing a common development practice.

## 🔥 What is Hot Reloading?

Hot reloading is a feature provided by development servers like Uvicorn. When enabled, the server automatically monitors your Python code files for changes. If it detects a change (e.g., you save a modified `.py` file), the server will automatically restart or reload the application to apply those changes.

**Benefits:**

-   **Faster Iteration:** You don't need to manually stop and restart the server every time you make a code change.
-   **Increased Productivity:** Saves time and allows you to see the effects of your changes almost instantly.
-   **Smoother Development Experience:** Reduces friction in the development process.

## ⚙️ How This Example Works

The `server.py` in this module uses `uvicorn.run()` with the `reload=True` parameter:

```python
# In server.py
if __name__ == "__main__":
    port = 8001
    # Note: This server specifically exposes only the streamable HTTP transport.
    # For servers with custom routes (e.g., OAuth), you'd typically run "server:mcp_app".
    # streamable_http_app = mcp_app.streamable_http_app() # This line is effectively what server:mcp_app.streamable_http_app refers to
    logger.info(f"Starting MCP server with hot reloading on http://0.0.0.0:{port}")
    import uvicorn
    uvicorn.run(
        "server:mcp_app.streamable_http_app", # Points to the streamable_http_app within your mcp_app
        host="0.0.0.0",
        port=port,
        reload=True  # This enables hot reloading!
    )
```

When you run this server, Uvicorn will watch for changes in the directory and reload the application when files are updated.

## 🚀 Running the Hot Reloading Server

1.  **Navigate to this directory:**
    ```bash
    cd 05_hot_reloading_mcp_server
    ```

2.  **Ensure dependencies are installed** 

3.  **Run the server using `uv` (which will execute `server.py`):
    ```bash
    uv run python server.py
    ```
    You should see output indicating the server is running, typically on `http://0.0.0.0:8001`.

## 🔬 Testing Hot Reloading

1.  **Initial Test:**
    -   Once the server is running, you can use a tool like `curl` or the MCP Inspector to interact with one of its tools. For example, to call the `greet_from_shared_server` tool:
        ```bash
        curl -X POST -N -v http://localhost:8001/mcp/ \
            -H "Content-Type: application/json" \
            -H "Accept: application/json, text/event-stream" \
            -d '{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "greet_from_shared_server",
                    "arguments": {"name": "Developer"}
                },
                "id": "1"
                }'
        ```
    -   You should receive a JSON response like: `{"result": "Hello, Developer, from the SharedStandAloneMCPServer!"}`.

2.  **Make a Code Change:**
    -   Open `server.py` in your code editor.
    -   Modify the `response_message` in the `greet` function. For example:
        ```python
        # In server.py, inside the greet function
        response_message = f"Hello, {name}, from the UPDATED SharedStandAloneMCPServer with Hot Reload!"
        ```
    -   Save the `server.py` file.

3.  **Observe Reload:**
    -   Look at the terminal where your server is running. You should see Uvicorn detecting the change and reloading the application.

4.  **Test Again:**
    -   Run the same `curl` command (or use the MCP Inspector) again:
        ```bash
        curl -X POST -N -v http://localhost:8001/mcp/ \
            -H "Content-Type: application/json" \
            -H "Accept: application/json, text/event-stream" \
            -d '{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "greet_from_shared_server",
                    "arguments": {"name": "Developer"}
                },
                "id": "1"
                }'
        ```
    -   This time, you should see the updated response: `{"result": "Hello, Developer, from the UPDATED SharedStandAloneMCPServer with Hot Reload!"}`.

This confirms that hot reloading is working correctly!
