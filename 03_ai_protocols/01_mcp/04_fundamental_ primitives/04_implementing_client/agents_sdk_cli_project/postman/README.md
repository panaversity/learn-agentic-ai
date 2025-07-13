# MCP Defining Tools - Postman Collection

This Postman collection provides a comprehensive test suite for the MCP tools implementation, specifically testing the document reader and editor tools.

## 🚀 Quick Start

### Prerequisites
1. **Postman**: Download and install [Postman](https://www.postman.com/downloads/)
2. **MCP Server**: Ensure the server is running on `http://localhost:8000/mcp/`

### Setup
1. **Import Collection**: Import `MCP_Defining_Tools.postman_collection.json` into Postman
2. **Environment Variables**: The collection uses `{{server_url}}` variable (defaults to `http://localhost:8000/mcp/`)
3. **Start Server**: Run `uv run uvicorn mcp_server:mcp_app --port 8000 --reload`

## 📋 Test Requests

### 1. Initialize Connection
- **Purpose**: Establishes the MCP connection with proper protocol version
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 initialize request with protocol version `2025-06-18`
- **Expected**: 200 status with result containing server capabilities

### 2. List Available Tools
- **Purpose**: Discovers what tools the MCP server provides
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 `tools/list` request
- **Expected**: 200 status with result containing `read_doc_contents` and `edit_document` tools

### 3. Read Document Contents
- **Purpose**: Tests the document reader tool
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 `tools/call` request for `read_doc_contents`
- **Parameters**: `doc_id: "deposition.md"`
- **Expected**: 200 status with document content in result

### 4. Edit Document
- **Purpose**: Tests the document editor tool
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 `tools/call` request for `edit_document`
- **Parameters**: 
  - `doc_id: "plan.md"`
  - `old_str: "implementation"`
  - `new_str: "execution"`
- **Expected**: 200 status with success message

### 5. Verify Document Edit
- **Purpose**: Confirms the document was successfully edited
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 `tools/call` request for `read_doc_contents`
- **Parameters**: `doc_id: "plan.md"`
- **Expected**: 200 status with updated content containing "execution" instead of "implementation"

### 6. Test Error Handling
- **Purpose**: Verifies proper error handling for missing documents
- **Method**: `POST`
- **Body**: JSON-RPC 2.0 `tools/call` request for `read_doc_contents`
- **Parameters**: `doc_id: "nonexistent.md"`
- **Expected**: 200 status with error message indicating document not found

## 🧪 Running Tests

### Option 1: Run All Tests
1. Open the collection in Postman
2. Click the "Run collection" button (▶️)
3. Select all requests and click "Run MCP Defining Tools"

### Option 2: Run Individual Tests
1. Open any request in the collection
2. Click "Send" to execute the request
3. Review the response and test results

### Option 3: Automated Testing
1. Use Postman's Newman CLI for automated testing:
```bash
newman run MCP_Defining_Tools.postman_collection.json
```

## 📊 Test Results

Each request includes automated tests that verify:
- **Status Code**: Ensures 200 OK response
- **Response Structure**: Validates JSON-RPC 2.0 format
- **Tool Discovery**: Confirms expected tools are available
- **Tool Execution**: Verifies tools work correctly
- **Error Handling**: Tests proper error responses

## 🔧 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the MCP server is running on port 8000
   - Check the server URL in environment variables

2. **Tool Not Found**
   - Verify the server implements the expected tools
   - Check tool names match exactly

3. **Invalid JSON-RPC**
   - Ensure request body follows JSON-RPC 2.0 specification
   - Verify Content-Type header is set to `application/json`

### Debug Steps

1. **Check Server Logs**: Monitor server output for errors
2. **Verify Request Format**: Ensure JSON-RPC structure is correct
3. **Test with MCP Inspector**: Use the inspector for visual debugging
4. **Check Tool Implementation**: Verify tools are properly decorated

## 📚 Related Resources

- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk) 