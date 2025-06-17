# 05: MCP Server Connection Lifecycle Implementation 🚀

**What you'll learn:** How to properly implement the Model Context Protocol (MCP) connection lifecycle according to the [official specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle).

The Model Context Protocol defines a **rigorous lifecycle** for client-server connections that ensures proper capability negotiation and state management. This implementation demonstrates the complete lifecycle phases with working code examples.

## 🎯 What We're Building

A complete MCP connection lifecycle implementation that demonstrates:

1. **🚀 Initialization Phase** - Capability negotiation and protocol version agreement
2. **⚙️ Operation Phase** - Normal protocol communication  
3. **🛑 Shutdown Phase** - Graceful termination of the connection

This follows the **official MCP 2025-03-26 specification** exactly, ensuring compatibility with all MCP-compliant systems.

## 📋 The Three Phases of MCP Lifecycle

### Phase 1: Initialization 🚀

The initialization phase **MUST** be the first interaction between client and server. During this phase:

- Protocol version compatibility is established
- Capabilities are exchanged and negotiated
- Implementation details are shared

#### Step 1: Initialize Request
The **client** initiates with an `initialize` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "experimental": {},
      "sampling": {}
    },
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

**Key Requirements:**
- The initialize request **MUST NOT** be part of a JSON-RPC batch
- No other requests are possible until initialization completes
- Client **SHOULD NOT** send requests (except pings) before server responds

#### Step 2: Initialize Response
The **server** responds with its capabilities:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "logging": {},
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "weather-server",
      "version": "1.0.0"
    }
  }
}
```

#### Step 3: Initialized Notification
The **client** sends an `initialized` notification to confirm readiness:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

**Important:** Server **SHOULD NOT** send requests (except pings and logging) before receiving this notification.

### Phase 2: Operation ⚙️

During the operation phase, client and server exchange messages according to negotiated capabilities:

- Both parties **MUST** respect the negotiated protocol version
- Only capabilities that were successfully negotiated **SHOULD** be used
- Normal MCP operations (tools, resources, prompts) are now available

### Phase 3: Shutdown 🛑

**Per the MCP Specification**: *"No specific shutdown messages are defined—instead, the underlying transport mechanism should be used to signal connection termination"*

Clean termination of the protocol connection using the underlying transport mechanism:

- **stdio**: Client closes input stream, waits for server exit, sends SIGTERM/SIGKILL if needed  
- **HTTP**: Shutdown indicated by closing HTTP connection(s) - **no JSON-RPC messages needed**

This is **spec-compliant behavior** - the transport layer handles termination, not the protocol layer.

## 🔧 Version Negotiation

### Protocol Version Handling
- Client **MUST** send a supported protocol version (preferably latest: `2025-03-26`)
- Server responds with same version (if supported) or different supported version
- If client doesn't support server's version, it **SHOULD** disconnect

### Version Compatibility
- **`2025-03-26`** - Latest specification with full feature support ✅
- **`2024-11-05`** - Previous version with limited features
- **`draft`** - Development version (not for production)

## 🛠️ Capability Negotiation

### Client Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| `roots` | Filesystem root access | `{ "listChanged": true }` |
| `sampling` | LLM sampling requests | `{}` |
| `experimental` | Non-standard features | `{}` |

### Server Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| `tools` | Callable functions | `{ "listChanged": true }` |
| `resources` | Readable resources | `{ "subscribe": true, "listChanged": true }` |
| `prompts` | Template prompts | `{ "listChanged": true }` |
| `logging` | Structured logs | `{}` |
| `completions` | Autocompletion | `{}` |
| `experimental` | Non-standard features | `{}` |

**Sub-capabilities:**
- `listChanged`: Support for list change notifications
- `subscribe`: Support for individual item change subscriptions (resources only)

## ⚠️ Error Handling

### Common Error Cases
- Protocol version mismatch
- Failed capability negotiation  
- Request timeouts
- Invalid initialization parameters

### Example Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2025-03-26", "2024-11-05"],
      "requested": "1.0.0"
    }
  }
}
```

## ⏱️ Timeouts and Reliability

### Timeout Management
- Implementations **SHOULD** establish timeouts for all requests
- Timeout prevents hung connections and resource exhaustion
- SDKs **SHOULD** allow per-request timeout configuration
- Progress notifications **MAY** reset timeout clock
- Maximum timeout **SHOULD** always be enforced

### Best Practices
- Configure reasonable timeouts (30-120 seconds typical)
- Handle timeout gracefully with cancellation notifications
- Implement retry logic for transient failures
- Log timeout events for debugging

## 🧪 Testing the Implementation

### Test 1: Complete Lifecycle
```bash
cd hello-mcp

# Terminal 1: Start MCP server
uv run server.py

# Terminal 2: Test complete lifecycle  
uv run client.py
```

**Expected Flow:**
1. ✅ Initialize request sent with protocol version `2025-03-26`
2. ✅ Server responds with capabilities (tools, logging, etc.)
3. ✅ Initialized notification confirms readiness
4. ✅ Tools list retrieved successfully
5. ✅ Weather tool called and responds correctly
6. ✅ Connection closes gracefully (no termination message needed)

### Test 2: Postman API Testing
```bash
cd postman/
# Import MCP lifecycle test collection
# Run complete lifecycle test suite
```

## 🔍 Implementation Details

### Our Implementation Stack
- **Server**: FastMCP with HTTP transport
- **Client**: Python httpx with async support
- **Transport**: HTTP with Server-Sent Events (SSE)
- **Session Management**: MCP session IDs in headers

### Key Features Implemented
- ✅ Complete 3-phase lifecycle
- ✅ Proper capability negotiation
- ✅ Version compatibility checking
- ✅ Session ID management
- ✅ Error handling and timeouts
- ✅ Tool discovery and execution

## 🚨 Common Implementation Mistakes

### ❌ Wrong: Skipping Initialization Steps
```python
# Don't do this - missing initialized notification
response = await client.post(url, json=initialize_request)
# Immediately calling tools without initialized notification
```

### ✅ Right: Complete Lifecycle
```python
# 1. Initialize
response = await client.post(url, json=initialize_request)
# 2. Send initialized notification  
await client.post(url, json=initialized_notification)
# 3. Now tools are available
```

### ❌ Wrong: Incorrect Version Handling
```python
# Don't hardcode old versions
"protocolVersion": "2024-11-05"  # Outdated
```

### ✅ Right: Use Latest Version
```python
"protocolVersion": "2025-03-26"  # Current specification
```

### ❌ Wrong: Ignoring Capabilities
```python
# Don't assume server has capabilities
await call_tool("nonexistent_tool")
```

### ✅ Right: Check Negotiated Capabilities
```python
# First check what tools are available
tools_response = await client.post(url, json=list_tools_request)
# Then call only available tools
```

### ❌ Wrong: Sending Unnecessary Shutdown Messages
```python
# Don't send termination notifications - not required by spec
await client.post(url, json={"method": "notifications/terminated"})
```

### ✅ Right: Spec-Compliant Shutdown
```python
# Per MCP spec: "No specific shutdown messages are defined"
# For HTTP: shutdown indicated by closing connection
async with httpx.AsyncClient() as client:
    # ... MCP operations ...
    pass  # Connection closes automatically - that's it!
```

## 🎓 What You've Learned

✅ **MCP Lifecycle Phases** - Initialization, Operation, Shutdown  
✅ **Version Negotiation** - Protocol compatibility handling  
✅ **Capability Exchange** - Client/server feature negotiation  
✅ **Error Handling** - Proper error responses and timeouts  
✅ **Transport Details** - HTTP/SSE implementation specifics  
✅ **Session Management** - Maintaining connection state  

## 🚀 Next Steps

Now that you understand MCP connection lifecycle:

1. **Advanced MCP Features** - Explore resources, prompts, and logging
2. **Transport Options** - Learn stdio transport implementation  
3. **Security** - Add authentication and authorization
4. **Performance** - Optimize for high-throughput scenarios
5. **Monitoring** - Add observability and debugging tools

## 🆘 Troubleshooting

### Problem: "Invalid protocol version"
**Solution:** Ensure both client and server support `2025-03-26`

### Problem: Tools not available after initialization
**Solution:** Verify initialized notification was sent and acknowledged

### Problem: Session timeouts
**Solution:** Implement proper session ID management and timeout handling

### Problem: Capability negotiation fails  
**Solution:** Check that client/server capabilities are properly formatted

## 📚 References

- [Official MCP Lifecycle Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle)
- [MCP Protocol Overview](https://modelcontextprotocol.io/specification/2025-03-26/basic/overview)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**🎯 Key Takeaway:** The MCP connection lifecycle is critical for reliable agent communication. Proper implementation ensures compatibility, reliability, and maintainability of your MCP-based systems! 