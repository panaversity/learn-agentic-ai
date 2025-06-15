# MCP Initialization Deep Dive - Postman Collection

This Postman collection provides comprehensive testing scenarios for MCP server initialization, capability negotiation, and connection lifecycle management using the [2025-03-26 specification](https://modelcontextprotocol.io/specification/2025-03-26/architecture).

## 🎯 Purpose

Unlike the basic Hello World collection, this collection focuses specifically on:
- **Three-phase initialization handshake**
- **Protocol version negotiation**
- **Capability declaration and negotiation**
- **Error handling during initialization**
- **Connection lifecycle management**

## 📋 Prerequisites

1. **Complete Hello World Example**: Understand basic MCP concepts first
2. **MCP Server Running**: Have an MCP server running on `http://localhost:8000`
3. **Postman Installed**: Download from [postman.com](https://www.postman.com/downloads/)

## 🚀 Collection Structure

### 01. Successful Initialization Flow
**Purpose**: Demonstrate the complete three-phase handshake
- **Step 1**: Send `initialize` request with protocol version and capabilities
- **Step 2**: Send `initialized` notification to complete handshake

**Learning Goals**:
- Understand the mandatory initialization sequence
- See capability negotiation in action
- Observe proper JSON-RPC message structure

### 02. Version Negotiation Scenarios
**Purpose**: Test protocol version compatibility
- **Compatible Version**: Test with current 2025-03-26 version
- **Older Version**: Test with legacy 2024-11-05 version

**Learning Goals**:
- Understand version negotiation process
- See how servers handle version mismatches
- Learn about backward compatibility

### 03. Capability Negotiation
**Purpose**: Explore different capability combinations
- **Full Capabilities**: Client declares all supported features
- **Minimal Capabilities**: Client declares no capabilities

**Learning Goals**:
- Understand capability-based feature negotiation
- See how servers respond to different client capabilities
- Learn about optional vs required features

### 04. Error Scenarios
**Purpose**: Test error handling during initialization
- **Malformed JSON**: Invalid JSON syntax
- **Missing Fields**: Required parameters omitted
- **Invalid Version**: Unsupported protocol version

**Learning Goals**:
- Understand JSON-RPC error responses
- See proper error handling patterns
- Learn about graceful degradation

### 05. Post-Initialization Operations
**Purpose**: Verify initialization requirements
- **Normal Operations**: Test tools/list after successful init
- **Premature Requests**: Test requests before initialization

**Learning Goals**:
- Understand initialization as a prerequisite
- See how servers enforce initialization requirements
- Learn about connection state management

## 🧪 Testing Workflow

### Step 1: Import Collection
1. Open Postman
2. Click **Import**
3. Select `MCP_Initialization_Deep_Dive.postman_collection.json`

### Step 2: Start MCP Server
```bash
cd 01_hello_mcp_server
uv run uvicorn server:mcp_app --port 8000 --reload
```

### Step 3: Test Scenarios

#### Successful Flow
1. Run **"01. Successful Initialization Flow"** folder
2. Observe the three-phase handshake
3. Note capability negotiation in responses

#### Version Testing
1. Run **"02. Version Negotiation Scenarios"**
2. Compare responses for different versions
3. Understand server version handling

#### Capability Testing
1. Run **"03. Capability Negotiation"**
2. Compare server responses to different client capabilities
3. Understand feature availability

#### Error Testing
1. Run **"04. Error Scenarios"**
2. Observe different error response formats
3. Understand error codes and messages

#### Lifecycle Testing
1. Run **"05. Post-Initialization Operations"**
2. See the difference between initialized and uninitialized states
3. Understand connection requirements

## 🔍 Key Observations

### Successful Initialization Response
```json
{
    "jsonrpc": "2.0",
    "result": {
        "protocolVersion": "2025-03-26",
        "serverInfo": {
            "name": "example-server",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": { "listChanged": true },
            "resources": { "subscribe": true, "listChanged": true },
            "prompts": { "listChanged": true }
        }
    },
    "id": 1
}
```

### Error Response Format
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32602,
        "message": "Invalid params",
        "data": "Missing required field: protocolVersion"
    },
    "id": 7
}
```

## 📚 Educational Value

This collection teaches:
1. **Protocol Compliance**: Understanding MCP specification requirements
2. **Error Handling**: Proper error response patterns
3. **State Management**: Connection lifecycle and state transitions
4. **Capability System**: Feature negotiation and availability
5. **Version Management**: Protocol evolution and compatibility

## 🔗 References

- [MCP 2025-03-26 Architecture](https://modelcontextprotocol.io/specification/2025-03-26/architecture)
- [Connection Lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/architecture#connection-lifecycle)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**Next Steps**: After mastering initialization, explore advanced MCP features like resource subscriptions and sampling in later examples. 