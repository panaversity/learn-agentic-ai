# Using the Postman Collection

This Postman collection allows you to test the MCP progress notification server interactively.

## How to Use

1.  **Import the Collection**: Import the `MCP_Progress_Notifications.postman_collection.json` file into Postman.
2.  **Start the Server**: Make sure the Python server is running (`uv run server.py`).
3.  **Run the Requests**: Execute the requests in the collection in order.

## Observing Progress

The key request is **"Call 'download_file' with Progress"**. When you send this request:

1.  Postman will keep the connection open and wait for the response.
2.  You will see `notifications/progress` events stream into the response body in real-time.
3.  The final `result` from the `tools/call` will appear at the end of the stream.

This is a great way to see the raw MCP messages and understand how the server pushes updates to the client during a long-running operation. 