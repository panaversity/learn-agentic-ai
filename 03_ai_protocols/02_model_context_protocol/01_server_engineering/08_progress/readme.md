# 📊 [MCP Progress Tracking](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/progress) - Your Real-Time Operation Monitor

> **Transform long-running tasks from mysterious black boxes into engaging, real-time experiences!** 

Ever wondered what your server is *actually* doing during that 30-second operation? MCP Progress Tracking turns those silent waits into interactive progress shows! 🎭

## 🎯 **What You'll Master**

By the end of this module, you'll understand how to:
- ✅ **Track long-running operations** in real-time
- ✅ **Send progress updates** from server to client  
- ✅ **Display beautiful progress bars** with meaningful messages
- ✅ **Handle progress tokens** properly in MCP protocol
- ✅ **Build responsive user experiences** for slow operations

## 🚀 **Quick Start**

### **1. Launch the Progress Server** ⭐
```bash
cd mcp_code
uv run server.py
```
*Look for: "📊 Starting MCP Progress Server!"*

### **2. Watch Progress Magic** ⭐⭐
```bash
uv run client.py
```
*Watch as progress bars fill up in real-time!*

## 🎪 **What Makes This Special**

### **📁 File Download Simulation**
```
📊 [████████████░░░░░░░░] 60.0% - Downloading dataset.zip... 60.0%
```
Experience realistic file download progress with:
- **Real-time percentage updates**
- **Visual progress bars** 
- **Descriptive status messages**

### **🔄 Data Processing Workflow**
```
📊 [██████░░░░░░░░░░░░░░] 30.0% - Applying transformations...
```
See how complex operations break down into phases:
- **Initialization** → **Validation** → **Processing** → **Completion**
- **Contextual messages** that explain what's happening
- **Smooth progress flow** from 0% to 100%

## 🎓 **Learning Phases**

### **⭐ Understanding Basics**
- **What is progress tracking?** - Real-time operation status updates
- **Why does it matter?** - Better user experience, debugging, monitoring
- **How does MCP handle it?** - Progress tokens and notification messages

### **⭐⭐ Interactive Exploration** 
- **Run the client** - See progress bars in action
- **Modify parameters** - Try different file sizes and record counts
- **Watch the flow** - Understand how progress updates stream

### **⭐⭐⭐ Advanced Scenarios**
- **Custom progress patterns** - Non-linear progress, unknown totals
- **Error handling** - What happens when operations fail mid-progress
- **Performance optimization** - Balancing update frequency vs overhead

## 🔧 **Real-World Applications**

### **File Operations** 📁
- Large file uploads/downloads
- Batch file processing
- Data import/export operations

### **Data Processing** 🔄
- Machine learning model training
- Database migrations
- Report generation

### **System Operations** ⚙️
- Software installations
- System backups
- Network synchronization

## 🧠 **Key Concepts Explained**

### **Progress Tokens** 🎫
Think of these as "tracking numbers" for your operations:
```json
{
  "_meta": {
    "progressToken": "download_123"
  }
}
```

### **Progress Notifications** 📢
Real-time updates sent from server to client:
```json
{
  "method": "notifications/progress",
  "params": {
    "progressToken": "download_123",
    "progress": 50,
    "total": 100,
    "message": "Downloading... 50%"
  }
}
```

### **Progress Flow** 🌊
1. **Client requests** operation with progress token
2. **Server starts** work and sends periodic updates
3. **Client receives** and displays progress
4. **Operation completes** and progress stops

## 💡 **Pro Tips**

### **For Better User Experience** ✨
- **Meaningful messages** - "Processing records..." vs "Working..."
- **Appropriate frequency** - Not too fast (spam) or slow (stale)
- **Visual feedback** - Progress bars, percentages, time estimates

### **For Developers** 🛠️
- **Unique tokens** - Avoid collisions across concurrent operations
- **Error handling** - Progress should stop on failures
- **Rate limiting** - Don't flood clients with updates

## 🎯 **Try These Experiments**

1. **Speed Comparison** - Run same operation with different sizes
2. **Concurrent Operations** - Multiple progress bars at once
3. **Custom Messages** - Modify server to send your own status updates
4. **Progress Patterns** - Try non-linear progress (fast start, slow end)

## 📚 **What's Next?**

After mastering progress tracking:
- **Cancellation** - Learn to stop long-running operations
- **Resumption** - Handle interrupted operations gracefully
- **Advanced Patterns** - Complex workflows with multiple progress stages

---

> **🎭 Remember**: Great progress tracking turns waiting into engagement. Your users should feel informed and in control, not frustrated and confused! 

*Ready to make your long-running operations shine? Let's track some progress!* 📊✨

# 08: Progress Notifications

**Objective:** Learn how a server can report progress on a long-running task to the client using the `$/progress` notification.

This is crucial for good user experience, allowing the client to display a progress bar or status message for operations that take more than a few seconds.

## Key MCP Concepts

-   **`$/progress` (Notification):** The standard notification for reporting progress. It includes a `token` to identify the specific operation, and a `value` payload containing the progress details (e.g., a message and a percentage).
-   **`window/workDoneProgress/create` (Request):** Before sending progress, the server must first ask the client to create a progress token. This allows the client to set up the UI element (like a progress bar).
-   **`Context` Object:** The `ctx` object in `FastMCP` provides a simple interface for managing progress reporting (`ctx.progress.create(...)`, `ctx.progress.report(...)`, `ctx.progress.done(...)`). `FastMCP` abstracts away the low-level `window/workDoneProgress/create` and `$/progress` messages.

## Implementation Plan

Inside the `mcp_code/` subdirectory:

-   **`server.py`:**
    -   Will define a tool for a long-running task, like `process_data(records: int)`.
    -   At the start, it will call `ctx.progress.create(...)` to get a progress token from the client.
    -   Inside its main loop, it will periodically call `ctx.progress.report(token, ...)` with the current percentage and a status message.
    -   When finished, it will call `ctx.progress.done(token)`.

-   **`client.py`:**
    -   Will need to handle the `window/workDoneProgress/create` request from the server (for this lesson, the `mcp.client` library can handle this automatically).
    -   Will listen for `$/progress` notifications.
    -   When a notification arrives, it will parse the payload and print a user-friendly progress update to the console, simulating a progress bar.