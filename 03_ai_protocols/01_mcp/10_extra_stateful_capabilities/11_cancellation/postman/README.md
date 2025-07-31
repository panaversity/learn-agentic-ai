# MCP Cancellation Postman Tests 🧪

This Postman collection provides a simple, hands-on way to test MCP request cancellation.

## 🚀 **Quick Setup**

### **1. Import the Collection**
1. Open Postman.
2. Click `Import` and select the `MCP_Cancellation_Tests.postman_collection.json` file.
3. The collection will appear in your workspace.

### **2. Start the MCP Server**
In your terminal, navigate to the `mcp_code` directory and start the server:
```bash
# From the 11_cancellation directory
cd mcp_code
uv run server.py
```
The server will start on `http://localhost:8000`.

### **3. Run the Requests**
You can now run the requests in the collection. For the best experience, run them in order.

## 🧪 **Cancellation Test Flow**

This collection demonstrates the standard cancellation flow. It works best if you **run steps 3 and 4 quickly** one after the other.

1.  **`1. Initialize MCP Connection`**: Establishes a session with the server and saves the `sessionId`.
2.  **`2. Send Initialized Notification`**: Completes the MCP handshake.
3.  **`3. Start Long-Running Task`**: This sends a request to the `process_large_file` tool, which is set to run for 10 seconds. The request will appear to "hang" in Postman, which is expected.
4.  **`4. Cancel Long-Running Task`**: While the previous request is still "running", send this request. It sends a `notifications/cancelled` message to the server, telling it to stop the task.

## 📊 **Expected Results**

If you cancel the long-running task in time (by running step 4 within 10 seconds of step 3), the server logs will show:
```
INFO:     Calling tool: process_large_file
INFO:     Starting to process postman_test_file.csv (Request: 2)
DEBUG:    Processed chunk 1/10
DEBUG:    Processed chunk 2/10
WARNING:  Processing of postman_test_file.csv was cancelled by client.
```
And the response to the original request from **step 3** will resolve with a JSON error object indicating the cancellation (`"code": -32800`).

## 🔧 **Troubleshooting**

-   **Server Not Responding**: Make sure the server is running and that the `baseUrl` variable in the Postman collection is set correctly (default is `http://localhost:8000`).
-   **Session ID Issues**: If you get errors, try re-running the `1. Initialize MCP Connection` request to get a fresh session ID.

---
💡 **Pro Tip**: Watch the server's terminal output as you run the Postman requests. It provides a real-time view of how the server handles each step, including receiving the cancellation notice. 