# Postman Collections for MCP Learning

This directory contains Postman collections and documentation for testing MCP (Model Context Protocol) servers. Using Postman provides an excellent educational experience for understanding the JSON-RPC protocol and MCP message flow.

## 🎯 Why Postman for MCP Learning?

### Educational Benefits
- **Visual Interface**: See raw HTTP requests and responses
- **Easy Testing**: No coding required to test different scenarios  
- **Better Understanding**: Clear visualization of headers, body, and responses
- **Interactive Learning**: Modify parameters and see immediate results
- **Documentation**: Built-in documentation with examples
- **Shareable**: Easy to export and share collections with students

### Technical Benefits
- **JSON-RPC Visualization**: Understand the protocol structure
- **SSE Response Handling**: See Server-Sent Events in action
- **Error Handling**: Learn how MCP handles different error scenarios
- **Parameter Validation**: Test input validation and schemas
- **Header Management**: Understand required HTTP headers

## 📋 Prerequisites

1. **Install Postman**: Download from [postman.com](https://www.postman.com/downloads/)
2. **Start MCP Server**: Ensure your MCP server is running
3. **Import Collection**: Load the `.postman_collection.json` file

## 🚀 Quick Start

### 1. Start the Hello MCP Server
```bash
cd hello-mcp
uv run uvicorn server:mcp_app --port 8000 --reload
```

### 2. Import the Postman Collection
1. Open Postman
2. Click **Import** button
3. Select `Hello_MCP_Server.postman_collection.json`
4. The collection will appear in your workspace

### 3. Run the Requests in Order
Execute the requests in sequence to understand the compliant MCP client flow:

1. **Initialize Session** - Even for a stateless server, a compliant client MUST send this first.
2. **Send Initialized Notification** - Required by 2025-06-18 spec after successful initialization.
3. **List Available Tools** - Discovers what the server can do.
4. **Call Weather Tool** - Executes a weather forecast with structured output (new in 2025-06-18).

## 📚 Collection Overview

### Request Structure
Each request demonstrates key MCP concepts:

```json
{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
}
```

### Response Format (Server-Sent Events)
```
data: {"jsonrpc":"2.0","result":{"tools":[...]},"id":2}
```

### Required Headers
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`
- `MCP-Protocol-Version: 2025-06-18` (for requests after `initialize`)

## 🔍 Understanding the Requests

### 1. Initialize Request
**Purpose**: Start an MCP interaction. This is the **mandatory** first step for any compliant client.

**Key Elements**:
- Method: `initialize`
- `protocolVersion: "2025-06-18"` in params
- Client capabilities and info
- Server responds with negotiated version and capabilities

### 2. Initialized Notification
**Purpose**: Complete the initialization sequence (required in 2025-06-18).

**Key Elements**:
- Method: `notifications/initialized`
- Sent after successful initialize response
- Tells server the client is ready for normal operations

### 3. Tools List Request  
**Purpose**: Discover what tools the server provides.

**Key Elements**:
- Method: `tools/list`
- Returns tool schemas with title fields (new in 2025-06-18)
- Must include `MCP-Protocol-Version: 2025-06-18` header

### 4. Tool Call Request
**Purpose**: Execute a specific tool with parameters.

**Key Elements**:
- Method: `tools/call`
- Tool name and arguments in params
- Returns structured content arrays (new in 2025-06-18)
- Parameter validation against schema

## 🧪 Testing Different Scenarios

### Modify Parameters
Try different cities in the weather tool:
- "London", "Tokyo", "Sydney"
- Empty string ""
- Invalid types (numbers instead of strings)

### Test Error Conditions
- Call non-existent tools
- Omit required parameters
- Send malformed JSON
- Use wrong HTTP methods

### Experiment with Headers
- Remove required headers
- Try different Accept headers
- Test with wrong Content-Type

## 📊 Collection Features

### Automated Tests
Each request includes test scripts that:
- Verify HTTP status codes
- Parse SSE responses
- Validate JSON structure
- Check for expected fields

### Environment Variables
- `baseUrl`: Server URL (default: http://localhost:8000)

## 🎓 Educational Workflow

### For Students
1. **Import and Explore**: Load collection and read descriptions
2. **Run in Sequence**: Execute requests in order to see the full lifecycle.
3. **Examine Responses**: Study the JSON-RPC format
4. **Modify Parameters**: Experiment with different inputs
5. **Create Variations**: Duplicate requests and try edge cases

### For Instructors
1. **Demonstrate Live**: Run requests while explaining concepts
2. **Assign Exercises**: Have students modify parameters
3. **Error Analysis**: Show different failure modes
4. **Protocol Basics**: Explain JSON-RPC 2.0 fundamentals
5. **Compare Implementations**: Test different MCP servers

## 📤 Exporting Collections

### Share with Students
1. Right-click collection name
2. Select **Export**
3. Choose **Collection v2.1** format
4. Share the JSON file

### Include Environment
1. Export the collection
2. Export environment variables separately
3. Provide both files to students

## 🔧 Advanced Usage

### Testing Multiple Servers
- Modify `baseUrl` variable for different servers
- Create separate environments for dev/staging/prod
- Compare responses across implementations

### Automation
- Use Postman Runner for batch testing
- Create test suites for regression testing
- Set up monitoring for server health

### Integration
- Export to Newman for CI/CD
- Generate documentation from collections
- Create mock servers from examples

## 🆚 Postman vs Python Client

| Aspect | Postman | Python Client |
|--------|---------|---------------|
| **Learning Curve** | Low - Visual interface | Higher - Requires coding |
| **Debugging** | Excellent - See raw requests | Good - Print statements |
| **Experimentation** | Easy - Point and click | Requires code changes |
| **Documentation** | Built-in with examples | External docs needed |
| **Sharing** | Export/Import collections | Share code files |
| **Automation** | Newman/Runner | Native Python scripts |
| **Integration** | APIs and webhooks | Full programming capability |

## 🔗 Additional Resources

- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Postman Learning Center](https://learning.postman.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

---

**Happy Testing!** 🧪✨

Remember: The goal is to understand the MCP protocol through hands-on experimentation. Don't just run the requests - read the responses, modify parameters, and explore edge cases! 