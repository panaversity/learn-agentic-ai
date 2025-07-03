# 🛑 MCP Request Cancellation

## 📋 Overview

This module demonstrates **request cancellation** in the Model Context Protocol (MCP). When AI agents need to handle long-running tasks, they must support graceful cancellation to remain responsive and resource-efficient.

## ❓ The Problem

Without cancellation support:
- 🐌 Long-running tasks block the system
- 💸 Resources are wasted on unwanted operations  
- 😤 Users can't interrupt incorrect or unnecessary tasks
- 🔥 Systems become unresponsive

## ✨ The Solution

MCP cancellation provides:
- ⏹️ **Graceful termination** of long-running tasks
- 🧹 **Resource cleanup** when tasks are cancelled
- 🏁 **Race condition handling** for immediate cancellations
- 📊 **Task lifecycle management** for better UX

## 🔄 Core Flow

```
1. 🚀 Start long-running task
   └── Get request/task ID for tracking

2. 📋 Track active tasks
   └── Store task references for cancellation

3. ⏹️ Cancel task (when needed)
   └── Send cancellation signal

4. 🧹 Clean up resources
   └── Remove from tracking, free memory
```

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