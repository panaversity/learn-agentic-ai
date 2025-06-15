# 05: MCP Server Initialization Deep Dive

**Objective:** Understand the complete MCP connection lifecycle, initialization handshake, and capability negotiation process as defined in the [MCP 2025-03-26 Specification](https://modelcontextprotocol.io/specification/2025-03-26/architecture).

This example focuses on the critical initialization phase that establishes proper communication between MCP clients and servers.

## 🎯 Learning Goals

After completing this example, you will understand:
- The three-phase MCP initialization handshake
- Protocol version negotiation
- Capability declaration and negotiation
- Connection lifecycle management
- Error handling during initialization
- Best practices for robust MCP connections

## 📋 Prerequisites

Complete the `01_hello_mcp_server` example first to understand basic MCP concepts.

## 🔄 MCP Connection Lifecycle

### Phase 1: Initialization
The initialization phase **MUST** be the first interaction between client and server.

#### Step 1: Initialize Request
Client sends an `initialize` request containing:
```json
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "clientInfo": {
            "name": "example-client",
            "version": "1.0.0"
        },
        "capabilities": {
            "roots": {
                "listChanged": true
            },
            "sampling": {}
        }
    },
    "id": 1
}
```

#### Step 2: Initialize Response
Server responds with its capabilities:
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
            "tools": {
                "listChanged": true
            },
            "resources": {
                "subscribe": true,
                "listChanged": true
            },
            "prompts": {
                "listChanged": true
            }
        }
    },
    "id": 1
}
```

#### Step 3: Initialized Notification
Client sends confirmation to begin normal operations:
```json
{
    "jsonrpc": "2.0",
    "method": "initialized",
    "params": {}
}
```

### Phase 2: Operation
Normal protocol communication with negotiated capabilities.

### Phase 3: Shutdown
Graceful termination of the connection.

## 🔧 Version Negotiation

Per the [MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26/architecture):

1. **Client Request**: Client sends the latest protocol version it supports
2. **Server Response**: 
   - If server supports the version → responds with same version
   - If server doesn't support → responds with its latest supported version
3. **Client Decision**: If client doesn't support server's version → should disconnect

## 🎛️ Capability Negotiation

Capabilities determine which protocol features are available during the session:

### Server Capabilities
- **`tools`**: Server can provide executable tools
  - `listChanged`: Server will notify when tool list changes
- **`resources`**: Server can provide contextual resources
  - `subscribe`: Client can subscribe to resource changes
  - `listChanged`: Server will notify when resource list changes
- **`prompts`**: Server can provide prompt templates
  - `listChanged`: Server will notify when prompt list changes

### Client Capabilities
- **`roots`**: Client can provide filesystem roots
  - `listChanged`: Client will notify when roots change
- **`sampling`**: Client can perform LLM sampling for servers

## 🚨 Critical Requirements

1. **Initialization First**: No requests (except pings) before successful initialization
2. **Capability Respect**: Both parties must respect negotiated capabilities
3. **Version Compatibility**: Ensure protocol version alignment
4. **Proper Shutdown**: Clean connection termination

## 🧪 Testing Scenarios

### Successful Initialization
1. Compatible protocol versions
2. Successful capability negotiation
3. Proper three-phase handshake

### Error Scenarios
1. **Version Mismatch**: Client and server incompatible versions
2. **Capability Conflicts**: Required capabilities not supported
3. **Timeout Errors**: Initialization takes too long
4. **Malformed Requests**: Invalid JSON-RPC format

## 📁 Example Files

- `server.py` - MCP server with detailed initialization logging
- `client.py` - MCP client demonstrating proper initialization
- `postman/` - Postman collection for testing initialization scenarios
- `examples/` - Various initialization scenarios and error cases

## 🔗 References

- [MCP 2025-03-26 Architecture](https://modelcontextprotocol.io/specification/2025-03-26/architecture)
- [MCP Connection Lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/architecture#connection-lifecycle)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**Next Steps**: After mastering initialization, explore advanced MCP features like resource subscriptions and sampling in later examples. 