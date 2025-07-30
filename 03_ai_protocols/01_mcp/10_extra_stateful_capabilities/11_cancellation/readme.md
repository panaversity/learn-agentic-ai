# 11: 🛑 MCP Request Cancellation

This lesson demonstrates how a client can cancel a long-running operation on an MCP server. This is a critical feature for building responsive and efficient AI agents, allowing users to abort tasks without waiting for them to complete.

## Key Concepts

MCP handles cancellation gracefully through a cooperative, notification-based system. This is much simpler and more robust than manually tracking tasks.

-   ✅ **The Right Way (MCP-Native):** The server's tool implementation simply needs to handle an `asyncio.CancelledError`. The `FastMCP` framework automatically propagates the cancellation from the client's notification to the correct `asyncio.Task`.
-   ❌ **The Wrong Way (Manual):** Avoid manually tracking tasks in global dictionaries or implementing custom cancellation logic. The framework handles this for you.

### How it Works

1.  **Client Prepares a Task:** The client constructs a `tools/call` request for a long-running operation.
2.  **Client Gets Request ID:** Before sending the request, the client inspects its `session` object to get the ID for the *next* request (e.g., `session._request_id`). This is the proper way to get the ID without hardcoding it.
3.  **Client Starts Task & Sends Cancellation:** The client sends the request. In parallel, after a delay, it sends a `notifications/cancelled` message containing the `requestId` it captured in the previous step.
4.  **Server Handles Cancellation:**
    -   `FastMCP` receives the notification and finds the `asyncio.Task` associated with the `requestId`.
    -   It raises an `asyncio.CancelledError` inside that running task.
    -   The tool's `try...except asyncio.CancelledError` block catches the error, logs a message, and re-raises the error.
    -   `FastMCP` sends the final `RequestCancelled` error response (`-32800`) to the client.

## Files

| File                       | Purpose                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| `mcp_code/server.py`       | A `FastMCP` server with a single, long-running tool (`process_large_file`) that is designed to be cancellable.     |
| `mcp_code/client.py`       | A Python client that starts the long-running tool and then correctly cancels it after a few seconds.                |
| `postman/`                 | A Postman collection for testing the cancellation flow interactively.                                   |
| `postman/README.md`        | A guide on how to use the Postman collection.                                                           |

## How to Run This Example

You can test the cancellation flow using either the Python client or the Postman collection.

### Terminal 1: Start the Server

First, start the MCP server. It will listen on `http://localhost:8000`.

```bash
# From the 11_cancellation directory
cd mcp_code
uv run server.py
```

### Terminal 2 (Option A): Run the Python Client

The Python client will start a task, wait 3 seconds, cancel it, and confirm that it was cancelled successfully.

```bash
# From the mcp_code directory
uv run client.py
```

**Expected Output:**

```
🚀 Starting cancellable task demonstration...
✅ Connected to MCP server.
✅ Session initialized.
📁 Starting long-running task 'process_large_file'...
   (Task with request ID 1 will be cancelled in 3 seconds)
⏹️ Waited 3 seconds. Sending cancellation for request 1...
✅ Task 1 was successfully cancelled by the server!

🎉 Demo finished.
```

### Option B: Use the Postman Collection

For a more hands-on approach, use the Postman collection located in the `postman/` directory. It allows you to manually trigger each step of the cancellation flow. See the `postman/README.md` for detailed instructions.

## 🎯 Learning Paths

### 🟢 Beginner
- Run `simple_demo.py` to see concepts in action
- Understand task lifecycle and cancellation points
- Learn about asyncio task management

### 🟡 Intermediate  
- Study the FastMCP server implementation
- Explore tool-based cancellation approach
- Test with httpx client examples

### 🔴 Advanced
- Implement proper MCP notification handling
- Add per-session task tracking
- Build production-ready cancellation systems

## 🚀 Quick Start

### Run the Concept Demo
```bash
# See all cancellation concepts in action
uv run simple_demo.py
```

This comprehensive demo shows:
- ✅ Basic cancellation flow
- ✅ Race condition handling  
- ✅ Multiple concurrent tasks
- ✅ Resource cleanup

### Run the MCP Server (Optional)
```bash
# Terminal 1: Start server
uv run server.py

# Terminal 2: Test client
uv run httpx_client.py quick
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `simple_demo.py` | 🎭 **Complete concept demo** (recommended) |
| `server.py` | 🖥️ FastMCP server with cancellation tools |
| `httpx_client.py` | 🔌 Simple HTTP client for testing |
| `client.py` | 📡 Full MCP protocol client |
| `postman/` | 🧪 API testing collection |

## 🎭 Demo Output

The `simple_demo.py` shows three scenarios:

### 1. Basic Cancellation
```
🚀 Starting long-running task...
📊 Processing dataset.csv... 1/8 seconds
📊 Processing dataset.csv... 2/8 seconds  
⏹️ Cancelling task...
✅ Successfully cancelled task
❌ Processing was cancelled
```

### 2. Race Condition
```
🏁 Testing race condition...
⚠️ Task not found (may have already completed)
⚡ Quick response: This completes immediately
```

### 3. Multiple Tasks
```
🚀 Starting 3 concurrent tasks...
⏹️ Cancelling middle task...
📊 Final results:
  Task 0: ✅ Successfully processed
  Task 1: ❌ Processing was cancelled  
  Task 2: ✅ Successfully processed
```

## 🌍 Real-World Applications

### 📊 Data Processing
- Cancel expensive database queries
- Stop large file processing operations
- Interrupt model training/inference

### 🤖 AI Agents  
- Stop reasoning chains that take too long
- Cancel tool executions that are no longer needed
- Interrupt multi-step workflows

### 🌐 Web Services
- Handle user navigation away from pages
- Cancel API requests when clients disconnect  
- Stop batch operations when priorities change

## 🔧 Key Implementation Details

### Task Tracking
```python
# Global task registry
active_tasks: Dict[str, asyncio.Task] = {}

# Register task for cancellation
current_task = asyncio.current_task()
active_tasks[task_id] = current_task
```

### Cancellation Points
```python
# Check for cancellation during processing
for i in range(processing_time):
    if task_id in active_tasks:
        await asyncio.sleep(1)  # Cancellation point
    else:
        return "Task was cancelled"
```

### Resource Cleanup
```python
try:
    # Do work...
except asyncio.CancelledError:
    # Clean up resources
    if task_id in active_tasks:
        del active_tasks[task_id]
    return "Task cancelled"
```

## 📚 MCP Specification

This implementation follows the [MCP Cancellation Specification](https://spec.modelcontextprotocol.io/specification/server/cancellation/).

Key points:
- ⚡ Cancellation should be **fast** (< 1 second)
- 🧹 Resources must be **cleaned up** properly
- 🏁 **Race conditions** must be handled gracefully
- 📊 Task **status tracking** should be accurate

## 🎉 Success Criteria

After running the demos, you should understand:

✅ **How to track long-running tasks**  
✅ **When and how to cancel operations**  
✅ **How to handle race conditions**  
✅ **How to clean up resources properly**  
✅ **How to build responsive AI agents**

## 🔗 Next Steps

- 📖 Study MCP notifications for proper protocol handling
- 🏗️ Build production cancellation systems
- 🔧 Integrate with your AI agent framework
- 📊 Add metrics and monitoring for task lifecycle

---

💡 **Key Insight**: Cancellation isn't just about stopping tasks—it's about building **responsive, resource-efficient AI agents** that users can trust and control.

# 11: Cancellation

**Objective:** Learn how a client can request to cancel a long-running operation on the server using the `$/cancelRequest` notification.

This is an essential feature for providing a responsive user experience, allowing users to abort operations they no longer need without having to wait for them to complete.

## Key MCP Concepts

-   **`$/cancelRequest` (Notification):** A notification sent from the client to the server. It contains the `id` of the original request that should be canceled.
-   **Cooperative Cancellation:** Cancellation in MCP is cooperative. The server is not forced to terminate the task. It receives the notification and is responsible for gracefully stopping the operation at the next available opportunity.
-   **`Context` Object and `ctx.is_cancelled`:** `FastMCP` provides a simple mechanism for this. When a cancellation notification is received for a specific request, the server sets a flag on that request's `Context`. The tool's code can then periodically check `ctx.is_cancelled` and exit cleanly if it returns `True`.
-   **Error Response:** A successfully canceled request should typically respond with an `Error` object with the code `-32800` (RequestCancelled).

## Implementation Plan

Inside the `mcp_code/` subdirectory:

-   **`server.py`:**
    -   Will define a tool for a long-running task, like `process_large_file()`, which runs in a loop.
    -   Inside the loop, the function will check `if ctx.is_cancelled:` at the start of each iteration.
    -   If the flag is true, it will stop processing, perform any necessary cleanup, and raise a `CancelledError`. `FastMCP` will catch this and send the correct error response to the client.

-   **`client.py`:**
    -   The client will call the `process_large_file` tool.
    -   It will immediately get back the `id` for this request.
    -   After a short delay (e.g., 2 seconds), while the server is still working, the client will send a `$/cancelRequest` notification containing the stored `id`.
    -   The client will then wait for the response and verify that it receives the `RequestCancelled` error, confirming that the operation was successfully aborted.