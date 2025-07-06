# 05: Connection Lifecycle Management (2025-06-18)

**Objective:** Learn the complete MCP connection lifecycle with **2025-06-18 specification compliance**, including initialization sequences, capability negotiation, and graceful shutdown procedures.

**Building on All Previous Lessons**: You now understand MCP's three building blocks (Tools, Resources, Prompts). This lesson focuses on **how AI and MCP servers establish and manage their connection**.

### 🤔 What Is the MCP Connection Lifecycle? (Simple Explanation)

**Simple Definition**: The MCP Connection Lifecycle is the **conversation protocol** that AI and servers use to connect, negotiate capabilities, communicate, and disconnect.

**Real-World Analogy**: Think of it like meeting a new person:
1. 🤝 **Introduction (Initialization)**: "Hi, I'm Claude. I can do X, Y, Z. What can you do?"
2. 🗣️ **Conversation (Operation)**: Normal back-and-forth communication using agreed capabilities
3. 👋 **Goodbye (Shutdown)**: "Thanks for the chat, see you later!"

### 🏗️ MCP Lifecycle vs. What You Know

| **If you're familiar with...** | **MCP Lifecycle is like...** | **Key insight** |
|-------------------------------|-------------------------------|-----------------|
| **HTTP Request/Response** | HTTP, but with handshakes and ongoing sessions | More like WebSocket with negotiation |
| **API Authentication** | OAuth flow with capability discovery | Not just auth, but feature negotiation |
| **Database Connections** | Connection pooling with capabilities | Discovers what's available before using |
| **Network Protocols** | TCP handshake, but for AI communication | Ensures compatibility before operation |

### 🎯 Why Connection Lifecycle Matters

**The Problem**: Without proper lifecycle management:
- 🔧 **Tools might fail**: AI tries to use features the server doesn't support
- 📚 **Resources could be missing**: AI expects data that isn't available
- 💬 **Prompts may not work**: AI assumes templates that don't exist
- ⚡ **Errors are unclear**: No standardized error handling

**The MCP Lifecycle Solution**:
- ✅ **Capability Discovery**: AI learns what server can do before trying
- ✅ **Version Compatibility**: Ensures both sides speak the same protocol
- ✅ **Graceful Errors**: Standardized error handling and recovery
- ✅ **Resource Management**: Proper connection setup and cleanup

### 📋 The Three Essential Phases

#### **Phase 1: Initialization (The Handshake)**
- 🤝 **Negotiate protocol versions**: Ensure compatibility
- 📋 **Exchange capabilities**: "I can do X, you can do Y"
- 🆔 **Share identity information**: Names, versions, descriptions
- ✅ **Confirm readiness**: Both sides ready for normal operation

#### **Phase 2: Operation (The Conversation)**
- 🔧 **Call tools** using negotiated capabilities
- 📚 **Read resources** that were discovered
- 💬 **Use prompts** that are available
- 🔄 **Handle errors** gracefully

#### **Phase 3: Shutdown (The Goodbye)**
- 🧹 **Clean up resources** and connections
- 💾 **Save state** if needed
- 👋 **Graceful disconnection** without data loss

This lesson demonstrates the three-phase MCP lifecycle: **Initialization → Operation → Shutdown** according to the official [MCP 2025-06-18 Lifecycle specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle).

## Key MCP Concepts (2025-06-18)

### 🎯 **Lifecycle Phases**
1. **Initialization**: Protocol version agreement and capability negotiation
2. **Operation**: Normal protocol communication using negotiated capabilities  
3. **Shutdown**: Graceful connection termination

### 📊 **Core Requirements**
- **Protocol Version**: Use `"2025-06-18"` in JSON requests (per official spec)
- **HTTP Headers**: Include `MCP-Protocol-Version: 2025-06-18` after initialization
- **Session Management**: Server handles sessions automatically in stateful mode
- **Error Handling**: Proper JSON-RPC 2.0 error responses

## 🔧 Official 2025-06-18 Implementation

### **Phase 1: Initialization**

**Client Initialize Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {
            "roots": {
                "listChanged": true
            },
            "sampling": {},
            "elicitation": {}
        },
        "clientInfo": {
            "name": "ExampleClient",
            "title": "Example Client Display Name",
            "version": "1.0.0"
        }
    }
}
```

**Server Initialize Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2025-06-18",
        "capabilities": {
            "logging": {},
            "prompts": {
                "listChanged": true
            },
            "resources": {
                "subscribe": true,
                "listChanged": true
            },
            "tools": {
                "listChanged": true
            },
            "completions": {}
        },
        "serverInfo": {
            "name": "ExampleServer",
            "title": "Example Server Display Name",
            "version": "1.0.0"
        },
        "instructions": "Optional instructions for the client"
    }
}
```

**Client Initialized Notification:**
```json
{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
```

### **Phase 2: Operation**

After initialization, the client **MUST** include the `MCP-Protocol-Version` header:

```http
POST /mcp/ HTTP/1.1
Content-Type: application/json
MCP-Protocol-Version: 2025-06-18
mcp-session-id: <session-id>

{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
}
```

### **Phase 3: Shutdown**

Per the specification:
- **No specific shutdown messages are defined**
- **HTTP transport**: Shutdown by closing the HTTP connection
- Session cleanup happens automatically

## FastMCP Implementation

Our simplified server demonstrates proper lifecycle handling:

```python
from mcp.server.fastmcp import FastMCP

# FastMCP handles all lifecycle complexity automatically
mcp = FastMCP("weather", stateless_http=False)

@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city."""
    return f"The weather in {city} will be warm and sunny today! 🌤️"

mcp_app = mcp.streamable_http_app()
```

**What FastMCP Automatically Handles:**
- ✅ Protocol version negotiation (`2025-06-18` ↔ `2025-06-18`)
- ✅ HTTP header requirements (`MCP-Protocol-Version`)
- ✅ Session management (stateful mode)
- ✅ Capability negotiation
- ✅ JSON-RPC 2.0 compliance
- ✅ Error handling
- ✅ Graceful shutdown

## 🚀 Quick Start

### **Terminal 1: Start the Enhanced Server**
```bash
uv add mcp uvicorn httpx
uv run uvicorn server:mcp_app --host 0.0.0.0 --port 8000 --reload
```

### **Terminal 2: Test with Client**
```bash
uv run python client.py
```

## Key Learning Outcomes

### **✅ Lifecycle Management**
- Understanding the three mandatory phases
- Protocol version negotiation between JSON and HTTP headers
- Capability exchange and validation
- Proper session handling

### **✅ 2025-06-18 Compliance**
- Using correct protocol versions (`"2025-06-18"` in JSON)
- Required HTTP headers (`MCP-Protocol-Version: 2025-06-18`)
- Enhanced capability structure with `title` fields
- Proper error handling patterns

### **✅ FastMCP Benefits**
- Automatic lifecycle management
- Built-in 2025-06-18 compliance
- Simplified development experience
- Production-ready error handling

## References

- [MCP 2025-06-18 Lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [HTTP Transport Requirements](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#protocol-version-header)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

This lesson shows how FastMCP makes implementing the complete MCP 2025-06-18 lifecycle specification straightforward and reliable.