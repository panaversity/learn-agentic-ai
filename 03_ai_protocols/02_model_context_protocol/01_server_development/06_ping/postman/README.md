# 📮 Postman Testing Guide for MCP Ping Utility

This directory contains Postman collections for testing the complete MCP Ping Utility according to the [MCP 2025-03-26 Ping Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping).

## 🎯 What You'll Test

- **🏓 Basic Ping Request/Response** - Standard ping according to specification
- **⏰ Response Time Validation** - Ensuring prompt responses as required
- **🔧 Specification Compliance** - Validating exact format requirements
- **⚡ Performance Testing** - Rapid ping scenarios
- **❌ Error Handling** - Invalid request scenarios

## 📋 Prerequisites

1. **Start the MCP Ping Server**:
   ```bash
   cd ../mcp_code
   uv run server.py
   ```
   Server will run on `http://localhost:8000`

2. **Import Collection**:
   - Import `MCP_Ping_Tests.postman_collection.json`
   - Collection includes environment variables setup

## 🔄 Complete MCP Ping Testing Flow

### **Phase 1: MCP Initialization** 
**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "clientInfo": {
            "name": "postman-ping-client",
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

### **Phase 3: Ping Testing**

#### Basic Ping (Per Specification)
**Request**: `POST http://localhost:8000/mcp/`
```json
{
    "jsonrpc": "2.0",
    "id": "ping_test_1",
    "method": "ping"
}
```

**Key Requirements from [MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping):**
- **No parameters object** - ping requests must not include params
- **Standard JSON-RPC 2.0 format**
- **Unique request ID** for response matching

**Expected Response**:
```json
{
    "jsonrpc": "2.0",
    "id": "ping_test_1",
    "result": {}
}
```

**Response Requirements:**
- **Empty result object** - `"result": {}`
- **Same ID as request**
- **Prompt response** - should be fast (< 1000ms typically)

#### Performance Testing
**Request**: Multiple rapid pings
- Tests server responsiveness under load
- Validates "prompt response" requirement
- Checks concurrent ping handling

## 🧪 Test Scenarios

### ✅ **Success Cases**
1. **Basic Ping** - Standard specification example
2. **Rapid Pings** - Multiple concurrent ping requests  
3. **Response Time** - Validates prompt response requirement
4. **Format Compliance** - Exact specification format validation

### ❌ **Error Cases**  
1. **Invalid Parameters** - Ping with params object (should be rejected)
2. **Missing Session** - Ping without MCP session
3. **Malformed JSON** - Invalid JSON-RPC format

## 📊 Expected Results

| Test Case | Expected Status | Response Time | Notes |
|-----------|----------------|---------------|-------|
| Basic Ping | 200 OK | < 1000ms | Specification compliance |
| Rapid Pings | 200 OK | < 500ms | Performance validation |
| Invalid Params | 200/400 | Any | Server handles gracefully |
| No Session | 200/400/401 | Any | Server policy dependent |

## 📚 Specification Validation

### From [MCP Ping Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping):

#### ✅ **Request Format**
- `"method": "ping"` - Exact method name
- No `params` object - Must be omitted
- Standard JSON-RPC 2.0 structure

#### ✅ **Response Format**  
- `"result": {}` - Must be empty object
- Same `id` as request
- Standard JSON-RPC 2.0 structure

#### ✅ **Behavior Requirements**
- **Prompt Response**: "The receiver MUST respond promptly"
- **Either Party**: Both client and server can initiate pings
- **Connection Health**: Used to verify connection is alive

## 🚀 Quick Start

1. Import `MCP_Ping_Tests.postman_collection.json` into Postman
2. Start the MCP server: `uv run server.py`
3. Run the collection in order:
   - **Initialize MCP Server** (captures session ID)
   - **Send Initialized Notification**
   - **Basic Ping Test** (validates specification compliance)
   - **Rapid Ping Test** (performance validation)
4. Explore error scenarios and specification examples

## 🔍 What to Look For

### **Successful Ping Indicators:**
- ✅ Status code 200
- ✅ Response time < 1000ms (prompt response)
- ✅ Empty result object `{}`
- ✅ Matching request/response IDs

### **Specification Compliance:**
- ✅ No parameters in ping request
- ✅ Empty result in ping response  
- ✅ Standard JSON-RPC 2.0 format
- ✅ Prompt server response

### **Performance Characteristics:**
- ✅ Consistent response times
- ✅ Handles multiple concurrent pings
- ✅ No degradation with rapid requests

## 📚 References

- [MCP Ping Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping)
- [MCP Basic Protocol](https://modelcontextprotocol.io/specification/2025-03-26/basic/overview)  
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**🎯 Key Learning:** MCP ping is the foundation of connection health monitoring. Understanding this simple utility prepares you for more complex MCP utilities like logging and progress tracking! 🏓 