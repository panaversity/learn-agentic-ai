# 📮 Postman Testing Guide for MCP Lifecycle

This directory contains Postman collections for testing the complete Model Context Protocol (MCP) connection lifecycle according to the [MCP 2025-06-18 Lifecycle specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle).

## 🎯 What You'll Learn

- Testing the complete MCP connection lifecycle phases
- Protocol version negotiation with proper JSON/HTTP header usage
- Capability negotiation validation
- Session management with HTTP headers
- Error scenario testing

## 📋 Prerequisites

1. **Start the MCP Server**:
   ```bash
   cd ../hello-mcp
   uv run server.py
   ```
   Server runs on `http://localhost:8000`

2. **Import Collection**:
   - Import `MCP_Lifecycle_Tests.postman_collection.json`

## 🔄 MCP Lifecycle Testing (2025-06-18 Specification)

### **Phase 1: Initialization** 

**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {
                "listChanged": true
            },
            "sampling": {},
            "elicitation": {}
        },
        "clientInfo": {
            "name": "postman-test-client",
            "title": "Postman Test Client",
            "version": "1.0.0"
        }
    }
}
```

**Expected Response**:
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "logging": {},
            "prompts": {"listChanged": true},
            "resources": {"subscribe": true, "listChanged": true},
            "tools": {"listChanged": true},
            "completions": {}
        },
        "serverInfo": {
            "name": "weather",
            "title": "Weather Forecast Server",
            "version": "1.0.0"
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
    "method": "notifications/initialized"
}
```

**Required Headers (per 2025-06-18 spec)**:
```http
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Protocol-Version: 2024-11-05
mcp-session-id: <session-id-from-init>
```

**Expected Response**: `202 Accepted`

### **Phase 3: Operation**

#### List Tools
**Request**:
```json
{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
}
```

**Required Headers**:
```http
MCP-Protocol-Version: 2024-11-05
mcp-session-id: <session-id>
```

#### Call Tool
**Request**:
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

### **Phase 4: Shutdown**

**Per MCP 2025-06-18 Specification**: 
- **"No specific shutdown messages are defined"**
- **"For HTTP transports, shutdown is indicated by closing the associated HTTP connection(s)"**

Connection termination happens automatically when HTTP connection closes.

## 🧪 Test Scenarios

### ✅ **Success Cases**
1. **Complete Lifecycle**: Initialize → Initialized → List Tools → Call Tool → (Close Connection)
2. **Protocol Versions**: Use `"2024-11-05"` in JSON, `2024-11-05` in HTTP headers
3. **Session Persistence**: Reuse session ID across requests
4. **Header Compliance**: Include `MCP-Protocol-Version` header after initialization

### ❌ **Error Cases**
1. **Missing Protocol Header**: Omit `MCP-Protocol-Version` header
2. **Invalid Protocol Version**: Use unsupported version like `"1.0.0"`
3. **Malformed JSON**: Send invalid JSON-RPC

## 📊 Expected Results

| Test Case | Expected Status | Key Headers | Notes |
|-----------|----------------|-------------|-------|
| Initialize | 200 OK | `text/event-stream`, `mcp-session-id` | SSE format |
| Initialized | 202 Accepted | Standard | Notification only |
| Tools List | 200 OK | `text/event-stream` | Tools array |
| Tool Call | 200 OK | `text/event-stream` | Forecast result |
| Shutdown | N/A | N/A | Close HTTP connection |

## 🔧 Key Protocol Points

### **Protocol Version Usage (2025-06-18)**
- **JSON Requests**: Use `"protocolVersion": "2024-11-05"`
- **HTTP Headers**: Use `MCP-Protocol-Version: 2024-11-05`
- This follows the official specification examples exactly

### **Required Headers After Initialization**
All requests after `initialize` **MUST** include:
```http
MCP-Protocol-Version: 2024-11-05
mcp-session-id: <session-id>
```

### **Capability Structure**
Enhanced in 2025-06-18 with:
- `title` fields in clientInfo/serverInfo
- `completions` capability for autocompletion
- Granular options like `listChanged`, `subscribe`

## 🚀 Quick Test Flow

1. Import `MCP_Lifecycle_Tests.postman_collection.json`
2. Start MCP server: `uv run server.py`
3. Run requests in order:
   - **Initialize** → captures session ID automatically
   - **Initialized** → uses captured session ID
   - **List Tools** → shows available tools
   - **Call Tool** → executes weather forecast

4. Observe complete MCP 2025-06-18 lifecycle!

## 📚 References

- [MCP 2025-06-18 Lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [HTTP Transport Requirements](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#protocol-version-header)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**Note**: The 2025-06-18 specification uses `"2024-11-05"` in JSON examples while referring to itself as the 2025-06-18 revision. This is the official protocol version for the current specification. ✅