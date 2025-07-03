# 📝 MCP Logging & Notifications: Your Server's Storytelling System

> **What We're Building**: A smart logging system where your MCP server can "talk" to clients, sharing what it's doing, celebrating successes, and reporting when things go wrong!

## 🎯 **Why This Matters**

Think of MCP logging like a **conversation between friends**:
- Your server has stories to tell ("Hey, I just connected to the database!")
- Your client wants to hear what's happening ("Tell me if something goes wrong!")
- Together, they create a **transparent, debuggable system**

Real-world example: Instead of silent failures, your AI agent can say *"Warning: API rate limit approaching"* or *"Success: Retrieved 50 weather records"*

## 🔍 **What You'll Learn**

After this module, you'll master:
1. **📢 Server Storytelling**: How servers send structured log messages
2. **🎚️ Volume Control**: How clients set logging levels (like turning volume up/down)
3. **🏷️ Message Categories**: Different types of messages (debug, info, warning, error)
4. **🔄 Real-time Communication**: Live logging notifications between server and client

## 🌟 **The MCP Logging Magic**

### **Core Concept**: Structured Conversations
Instead of messy console logs, MCP creates **structured conversations**:

```json
{
  "level": "info",
  "logger": "weather-service", 
  "data": {
    "action": "forecast_retrieved",
    "city": "San Francisco",
    "temperature": "72°F",
    "confidence": 0.95
  }
}
```

### **8 Levels of Communication** (Based on [RFC 5424](https://tools.ietf.org/html/rfc5424))

| 🎯 Level | 🎭 Personality | 💭 When to Use | 📝 Example |
|----------|----------------|----------------|-------------|
| `debug` | 🔍 Detective | "Let me trace every step" | Function entry/exit points |
| `info` | 📰 Reporter | "Here's what's happening" | "User logged in successfully" |
| `notice` | 📢 Announcer | "Something noteworthy occurred" | "Configuration updated" |
| `warning` | ⚠️ Advisor | "Heads up, pay attention!" | "API rate limit at 80%" |
| `error` | 🚨 Alarm | "Something broke!" | "Database connection failed" |
| `critical` | 🆘 Emergency | "System component down!" | "Payment service unavailable" |
| `alert` | 🚒 Fire Department | "Drop everything and fix this!" | "Data corruption detected" |
| `emergency` | 💥 Code Red | "The building is on fire!" | "Complete system failure" |

## 🎬 **How It Works: The Communication Flow**

### **Step 1: Server Declares "I Can Talk!"**
```json
{
  "capabilities": {
    "logging": {}
  }
}
```

### **Step 2: Client Sets Volume Level**
```json
{
  "method": "logging/setLevel",
  "params": {
    "level": "info"  // "Only tell me 'info' and above, skip the 'debug' chatter"
  }
}
```

### **Step 3: Server Shares Stories**
```json
{
  "method": "notifications/message",
  "params": {
    "level": "error",
    "logger": "database",
    "data": {
      "error": "Connection timeout",
      "retry_attempt": 3,
      "next_retry_in": "30s"
    }
  }
}
```

## 🛠️ **What We'll Build**

### **🖥️ Smart Server** (`server.py`)
- **Declares logging capability** to clients
- **Responds to log level changes** from clients  
- **Generates realistic log messages** during operations
- **Demonstrates all 8 severity levels** with practical examples

### **📱 Interactive Client** (`client.py`)
- **Connects and sets log preferences** (like choosing notification settings)
- **Listens for real-time messages** from server
- **Displays logs beautifully** with colors and emojis
- **Tests different scenarios** (normal operations, errors, etc.)

## 🚀 **Learning Path**

### **Phase 1: Understanding the Basics** ⭐
- Run the server and see basic logging in action
- Try setting different log levels
- Watch how messages change based on severity

### **Phase 2: Interactive Exploration** ⭐⭐
- Use the client to trigger different log scenarios
- Experiment with log filtering
- See real-time notifications in action

### **Phase 3: Advanced Scenarios** ⭐⭐⭐
- Test error conditions and recovery
- Explore structured data in log messages
- Create your own logging categories

## 💡 **Key Insights You'll Gain**

1. **🎯 Clarity Over Noise**: Good logging tells a story, not just facts
2. **🎚️ Context Matters**: Different situations need different detail levels
3. **🔄 Real-time is Powerful**: Live logging helps with debugging and monitoring
4. **🛡️ Security First**: Never log sensitive data (passwords, API keys, personal info)

## 🔗 **Official Specification**
📚 [MCP Logging Utility Specification](https://modelcontextprotocol.io/specification/2025-03-26/server/utilities/logging)

## 🎓 **Next Steps**
After mastering logging, you'll be ready for:
- **08_progress**: Track long-running operations
- **09_cancellation**: Handle operation cancellation
- **10_resumption**: Resume interrupted workflows

---

> **💪 Pro Tip**: Think of logging as **giving your AI agents a voice**. They can tell you what they're thinking, warn you about problems, and celebrate their successes. This makes debugging and monitoring infinitely easier!

Ready to give your MCP server a voice? Let's dive in! 🏊‍♂️

# 06: Logging Notifications

**Objective:** Learn how the server can send log messages to the client using the `$/logTrace` notification.

This feature is essential for debugging and providing visibility into the server's internal operations, allowing a client application to display server logs in its own interface.

## Key MCP Concepts

-   **Notification:** A one-way message from server to client that does not have a response. This requires a stateful connection.
-   **`$/logTrace` (Notification):** The standard MCP notification for sending log messages.
-   **`$/setTrace` (Request):** A request from the client to the server to set the desired level of logging (e.g., 'verbose', 'off').
-   **`Context` Object:** In `FastMCP`, stateful methods receive a `Context` object (`ctx`), which provides access to utilities for interacting with the client, including the logger (`ctx.log`). `FastMCP` automatically translates `ctx.log` calls into `$/logTrace` notifications.

## Implementation Plan

Inside the `mcp_code/` subdirectory:

-   **`server.py`:**
    -   We will create a tool (e.g., `do_work(task: str)`) that performs several steps.
    -   Inside this tool, we will use `ctx.log.info(...)`, `ctx.log.warning(...)`, etc., to send log messages back to the client at each step.
    -   The server will also handle the `$/setTrace` request to adjust its logging verbosity.

-   **`client.py`:**
    -   The client will establish a stateful, streaming connection to listen for notifications.
    -   It will first call `$/setTrace` to enable verbose logging.
    -   It will then call the `do_work` tool.
    -   In a separate task, it will listen on the event stream and print any `$/logTrace` notifications it receives from the server in real-time.