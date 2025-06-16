# 📮 Postman Testing Guide for MCP Initialization

This directory contains Postman collections for testing Model Context Protocol (MCP) initialization sequences according to the [MCP 2025-03-26 Specification](https://modelcontextprotocol.io/specification/2025-03-26).

## 🎯 What You'll Learn

- How to test MCP initialization handshake manually
- Understanding the three-phase MCP connection lifecycle
- Protocol version negotiation testing
- Capability negotiation validation
- Session management verification
- Error scenario testing

## 📋 Prerequisites

1. **Start the Hello MCP Server**:
   ```bash
   cd ../hello-mcp
   uv run server.py
   ```
   Server will run on `http://localhost:8000`

2. **Import Collections**:
   - Import `MCP_Initialization_Tests.postman_collection.json`
   - Import `MCP_Environment.postman_environment.json`

## 🔄 MCP Initialization Flow Testing

### **Phase 1: Initialize Request** 
According to [MCP Architecture](https://modelcontextprotocol.io/specification/2025-03-26/architecture#connection-lifecycle):

**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "clientInfo": {
            "name": "postman-test-client",
            "version": "1.0.0"
        },
        "capabilities": {
            "experimental": {},
            "sampling": {}
        }
    },
    "id": 1
}
```

**Expected Response**: Server capabilities + session ID
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "experimental": {},
            "prompts": {"listChanged": false},
            "resources": {"subscribe": false, "listChanged": false},
            "tools": {"listChanged": false}
        },
        "serverInfo": {
            "name": "weather",
            "version": "1.9.4"
        }
    }
}
```

**Key Headers**:
- `Content-Type: text/event-stream`
- `mcp-session-id: <uuid>`

### **Phase 2: Initialized Notification**
**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
}
```

**Headers**: Include the `mcp-session-id` from Phase 1

**Expected Response**: `202 Accepted`

### **Phase 3: Normal Operations**

#### List Tools
**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
}
```

#### Call Tool
**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "get_forecast",
        "arguments": {
            "city": "San Francisco"
        }
    },
    "id": 3
}
```

## 🧪 Test Scenarios

### ✅ **Success Cases**
1. **Complete Flow**: Initialize → Initialized → List Tools → Call Tool
2. **Protocol Version Match**: Client and server both use `2025-03-26`
3. **Session Persistence**: Reuse session ID across requests

### ❌ **Error Cases**
1. **Skip Initialization**: Try tools/list without initialize
2. **Wrong Protocol Version**: Use `2024-11-05` instead of `2025-03-26`  
3. **Missing Session ID**: Omit session header after initialization
4. **Invalid JSON-RPC**: Send malformed JSON

## 📊 Expected Results

| Test Case | Expected Status | Expected Headers | Notes |
|-----------|----------------|------------------|-------|
| Initialize | 200 OK | `text/event-stream`, `mcp-session-id` | SSE format response |
| Initialized | 202 Accepted | Standard | Notification acknowledged |
| Tools List | 200 OK | `text/event-stream` | Tools array returned |
| Tool Call | 200 OK | `text/event-stream` | Tool result returned |

## 🔧 Postman Environment Variables

Set these in your Postman environment:
- `mcp_host`: `http://localhost:8000`
- `mcp_session_id`: `{{mcp-session-id}}` (auto-extracted)
- `protocol_version`: `2025-03-26`

## 📚 References

- [MCP 2025-03-26 Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [MCP Architecture](https://modelcontextprotocol.io/specification/2025-03-26/architecture)
- [Connection Lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/architecture#connection-lifecycle)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

## 🚀 Quick Start

1. Import both JSON files into Postman
2. Start the MCP server: `uv run server.py` 
3. Run "1. Initialize MCP Server" request
4. Copy the `mcp-session-id` from response headers
5. Run subsequent requests in order
6. Observe the complete MCP initialization flow!

---

**Pro Tip**: Watch the server logs while running tests to see the MCP lifecycle in action! 🔍 