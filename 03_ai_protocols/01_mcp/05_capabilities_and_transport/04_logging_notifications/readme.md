# [Logging - Your Server's Voice](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging)

**Objective:** Learn how MCP servers communicate their internal state to clients through structured logging notifications using the **2025-06-18 specification**.

### 🤔 What is MCP Logging? (Simple Explanation)

Think of MCP logging as **giving your server a voice** so it can tell you what it's doing:

**Real-World Analogy**: Imagine you're cooking with a friend. Instead of working in silence, you narrate what you're doing:
- "I'm heating the oil" (info level)
- "The onions are browning nicely" (debug level)  
- "Careful - the pan is getting hot!" (warning level)
- "Oh no! I burned the garlic!" (error level)

**MCP Logging is Similar**: Your server narrates its activities to help you understand what's happening, debug problems, and monitor performance.

### 📊 MCP vs Familiar Technologies

| **Technology** | **What It Does** | **MCP Logging Advantage** |
|----------------|------------------|---------------------------|
| **Console.log()** | Basic text output | Structured, standardized format |
| **Winston/Bunyan** | Node.js logging | Protocol-native, client-aware |
| **Syslog** | System logging | AI-friendly, contextual |
| **CloudWatch** | AWS logging | MCP-specific, tool-integrated |

### 🎯 Why This Matters for AI Development

1. **🔍 Debugging**: See exactly what your AI agent is thinking
2. **📊 Monitoring**: Track performance and behavior patterns  
3. **🤝 Transparency**: Users can see what their AI is doing
4. **🛠️ Development**: Faster troubleshooting and optimization

## 🎓 Learning Objectives

By the end of this lesson, you will be able to:

### ✅ **Conceptual Understanding**
- Explain what MCP logging is and why it's important
- Describe the 8 logging levels and when to use each
- Understand the difference between logging and regular output

### ✅ **Technical Skills**
- Implement server-side logging using the Context object
- Create clients that listen for logging notifications
- Set and change logging levels dynamically
- Handle structured log data with metadata

### ✅ **Practical Application**
- Debug MCP server issues using logs
- Monitor AI agent behavior in real-time
- Create user-friendly logging displays
- Optimize logging for performance

## 🌟 The 8 Levels of Communication

Based on [RFC 5424](https://tools.ietf.org/html/rfc5424), MCP supports 8 logging levels:

| 🎯 **Level** | 🎭 **When to Use** | 💡 **Example Use Case** | 📝 **Sample Message** |
|-------------|-------------------|------------------------|----------------------|
| `emergency` | System is unusable | Complete failure | "Database cluster down" |
| `alert` | Immediate action needed | Critical component failing | "Memory usage at 95%" |
| `critical` | Critical conditions | Major functionality broken | "Authentication service offline" |
| `error` | Error conditions | Something failed | "Failed to process user request" |
| `warning` | Warning conditions | Potential issues | "API rate limit at 80%" |
| `notice` | Normal but significant | Important events | "User session started" |
| `info` | Informational messages | General information | "Processing 50 records" |
| `debug` | Debug-level messages | Detailed tracing | "Function entry: validateUser()" |


## 🛠️ What We'll Build

### **📡 Smart Logging Server** (`server.py`)
- **Structured Logging**: Uses MCP Context for proper logging
- **Multiple Log Levels**: Demonstrates all 8 severity levels
- **Realistic Scenarios**: Shows logging in real-world situations
- **Performance Tracking**: Logs timing and resource usage

### **👂 Listening Client** (`client.py`)
- **Real-time Display**: Shows logs as they happen
- **Level Filtering**: Controls which messages to show
- **Beautiful Formatting**: Colors and emojis for easy reading
- **Interactive Controls**: Change log levels on the fly

## 🔄 How MCP Logging Works

### **Step 1: Server Capability Declaration**
```python
# Server tells client: "I can send you log messages"
capabilities = {
    "logging": {}
}
```

### **Step 2: Client Sets Preferences**
```python
# Client tells server: "Send me 'info' level and above"
await session.set_logging_level("info")
```

### **Step 3: Server Sends Structured Messages**
```python
# Server narrates what it's doing
await ctx.info("Processing user request", extra={
    "user_id": "123",
    "request_type": "weather",
    "processing_time": 0.5
})
```

### **Step 4: Client Receives and Displays**
```python
# Client formats and shows the message
def log_handler(params):
    print(f"📰 [INFO] Processing user request")
    print(f"    User: 123, Type: weather, Time: 0.5s")
```

## 🏗️ Implementation Guide

### **Setting Up Your Environment**
```bash
# Navigate to the lesson directory
cd mcp_code

# Install dependencies
uv sync

# Run the server (Terminal 1)
uv run uvicorn server:app --reload

# Run the client (Terminal 2)
uv run python client.py
```

### **Testing Different Scenarios**
```bash
# Test with different log levels
uv run python client.py --log-level debug
uv run python client.py --log-level info
uv run python client.py --log-level warning
```

## 📚 Specification References

- **MCP 2025-06-18 Logging Specification**: [Official Docs](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging)
- **RFC 5424 Syslog**: Standard logging levels and format
- **JSON-RPC 2.0**: Message format for notifications

## 🎓 Assessment Questions

Test your understanding:

1. **Conceptual**: What's the difference between `warning` and `error` levels?
2. **Technical**: How do you set the logging level from a client?
3. **Practical**: When would you use `debug` level logging?
4. **Design**: How would you log a multi-step process?

## 🚀 Next Steps

After mastering logging, you'll be ready for:
- **07_tool_update_notification**: Dynamic tool management
- **08_progress**: Long-running operation tracking
- **09_ping**: Connection health monitoring

---

> **🎯 Success Criteria**: You'll know you've mastered this lesson when you can explain what your server is doing just by reading its logs, and you can control the level of detail you see based on your needs.

Ready to give your MCP server a voice? Let's start building! 🎤