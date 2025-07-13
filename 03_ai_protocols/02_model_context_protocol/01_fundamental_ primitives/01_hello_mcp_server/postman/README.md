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

## 🧪 Testing Different Scenarios

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

**Happy Testing!** 🧪✨

Remember: The goal is to understand the MCP protocol through hands-on experimentation. Don't just run the requests - read the responses, modify parameters, and explore edge cases! 