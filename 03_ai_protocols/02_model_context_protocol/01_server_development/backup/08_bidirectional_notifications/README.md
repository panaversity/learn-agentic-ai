# MCP Bidirectional Notifications

## 🎯 **SIMPLIFIED VERSION AVAILABLE**

**👉 For a clear demonstration of the core concept, see:**
- `README_SIMPLE.md` - Simple explanation
- `simple_server.py` - Clean, minimal server
- `simple_client.py` - Clean, minimal client  
- `run_simple_demo.py` - Easy demo runner

**🚀 Quick Start:**
```bash
python3 run_simple_demo.py
```

## 💡 Core Concept

**Bidirectional communication** in MCP means:
- **Client → Server**: Client calls tools (normal)
- **Server → Client**: Server sends notifications during tool execution (bidirectional!)

This enables **real-time AI agents** that can provide live updates, perfect for the **DACA framework**.

---

## 🔄 Original Complex Example

The files below demonstrate advanced bidirectional patterns but are more complex:

**Real MCP bidirectional communication** using FastMCP and standard patterns from the [MCP specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#listening-for-messages-from-the-server).

## 🎯 What This Demonstrates

**Bidirectional communication** means both client and server can initiate messages:

1. **Client → Server**: Tool calls, notifications (traditional)
2. **Server → Client**: Notifications during tool execution (bidirectional)
3. **Real-time streaming**: Server sends progress updates via SSE

## 🔄 MCP Bidirectional Patterns

According to the MCP specification:

### Client → Server (POST)
```json
// Tool calls
{"jsonrpc": "2.0", "method": "tools/call", "params": {...}, "id": 1}

// Notifications  
{"jsonrpc": "2.0", "method": "notifications/initialized"}
```

### Server → Client (SSE/GET)
```json
// Progress notifications during tool execution
{"jsonrpc": "2.0", "method": "notifications/progress", "params": {...}}

// Log messages
{"jsonrpc": "2.0", "method": "logging/log", "params": {...}}

// Tool responses
{"jsonrpc": "2.0", "result": {...}, "id": 1}
```

## 🛠 Real Implementation

### Server Features (server.py)
- **FastMCP-based** real MCP server
- **Tools with logging** that generate server notifications
- **Progress tracking** during long-running operations
- **Error handling** with proper notifications
- **SSE streaming** handled automatically by FastMCP

### Client Features (client.py)
- **Standard MCP client** using httpx
- **SSE listener** for server notifications
- **Real-time progress** display
- **Bidirectional message handling**

## 🚀 Running the Original Demo

```bash
# Terminal 1: Start server
cd 08_bidirectional_notifications
python3 server.py

# Terminal 2: Run client
python3 client.py
```

## 📊 Expected Output

```
🔧 Calling tool: analyze_data
   Arguments: {'data': 'sample dataset'}

# Server logs (visible in Terminal 1):
2025-01-16 - 🔧 Starting analysis of: sample dataset
2025-01-16 - 📊 Step 1/4: Loading data
2025-01-16 - 📊 Step 2/4: Processing
2025-01-16 - 📊 Step 3/4: Analyzing patterns
2025-01-16 - 📊 Step 4/4: Generating report
2025-01-16 - ✅ Analysis result: Analysis complete...

# Client receives (via SSE):
📝 Server Log [info]: Starting analysis of: sample dataset
📝 Server Log [info]: Step 1/4: Loading data
📝 Server Log [info]: Step 2/4: Processing
📝 Server Log [info]: Step 3/4: Analyzing patterns
📝 Server Log [info]: Step 4/4: Generating report
✅ Tool result: Analysis complete for 'sample dataset'...
```

## 💡 Key Learning Points

### 1. Real Bidirectional Communication
- **Server logs** are automatically streamed to client via SSE
- **FastMCP handles** the SSE streaming automatically
- **Client listens** on GET endpoint for server messages
- **No custom implementation** needed - uses standard MCP patterns

### 2. MCP Specification Compliance
- **Single endpoint** (`/mcp/`) handles both POST and GET
- **POST**: Client sends requests and notifications
- **GET**: Client receives server notifications via SSE
- **Session management** with session IDs
- **Standard JSON-RPC** message format

### 3. Practical Use Cases
- **Progress tracking** for long-running operations
- **Real-time logging** from server to client
- **Error notifications** with detailed context
- **Tool execution feedback** in real-time

### 4. Implementation Simplicity
- **FastMCP** handles all the complex SSE logic
- **Standard logging** becomes bidirectional notifications
- **No custom message queuing** required
- **Works with existing** MCP client patterns

## 🔍 Technical Details

### Server-Side Notifications
```python
# Any logging automatically becomes a notification
logger.info("🔧 Starting analysis...")  # → Client receives this via SSE
logger.warning("⚠️ Warning message")    # → Client receives this via SSE
logger.error("❌ Error occurred")       # → Client receives this via SSE
```

### Client-Side Listening
```python
# Standard SSE listening pattern
async with client.stream("GET", base_url, headers=headers) as response:
    async for chunk in response.aiter_text():
        # Process server notifications
        await process_server_message(chunk)
```

## 🌟 Real-World Applications

1. **Long-running AI tasks** with progress updates
2. **Data processing pipelines** with status notifications
3. **Multi-step workflows** with real-time feedback
4. **Error monitoring** with immediate alerts
5. **Collaborative tools** with live updates

---

**This demonstrates true MCP bidirectional communication using real, working patterns from the specification.**

## 🎓 Key Learning Points

### 1. Bidirectional Nature
- MCP is not just request-response
- Server can initiate communication with client
- Both parties can send notifications and requests

### 2. Communication Channels
- **POST:** Client → Server (all client-initiated messages)
- **GET/SSE:** Server → Client (all server-initiated messages)
- **Single Endpoint:** Both channels use same URL

### 3. Request Types
- **Client Requests:** Tools, resources, prompts
- **Server Requests:** Sampling, capabilities, custom protocols
- **Notifications:** Progress, logging, changes (both directions)

### 4. Real-World Use Cases
- **Progress Tracking:** Long-running operations
- **LLM Integration:** Server requests AI analysis from client
- **Resource Monitoring:** Real-time data change notifications
- **Error Handling:** Detailed error reporting and recovery
- **Multi-Agent Coordination:** Server orchestrates multiple clients

### 5. Advanced Patterns
- **Server-Side Orchestration:** Server coordinates multiple tool calls
- **Human-in-the-Loop:** Server requests human approval via client
- **Dynamic Capability Negotiation:** Runtime capability updates
- **Event-Driven Architecture:** Real-time reactive systems

## 🔍 MCP Specification References

- [Client Features - Sampling](https://modelcontextprotocol.io/specification/2025-03-26/client/sampling)
- [Server Features - Logging](https://modelcontextprotocol.io/specification/2025-03-26/server/utilities/logging)
- [Progress Notifications](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/progress)
- [JSON-RPC Bidirectional](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle)

## 🌟 Advanced Scenarios

### Scenario 1: Multi-Agent Coordination
Server acts as coordinator, sending requests to multiple MCP clients to orchestrate complex workflows.

### Scenario 2: Human-in-the-Loop
Server requests human approval/input via client before executing sensitive operations.

### Scenario 3: Real-Time Analytics
Server continuously streams analysis results and progress updates to monitoring clients.

### Scenario 4: Dynamic Tool Discovery
Server notifies clients when new tools become available or existing tools change.

---

**Previous:** `07_single_http_connection_behavior/` - Understanding single HTTP endpoint behavior
**Next:** Advanced MCP patterns and integration with DACA framework 