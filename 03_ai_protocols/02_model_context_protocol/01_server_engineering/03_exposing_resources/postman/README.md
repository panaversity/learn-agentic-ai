# 🧰 MCP Exposing Resources - Postman Collection (2025-06-18)

This Postman collection demonstrates how to test an MCP server that **exposes resources** using the **2025-06-18 specification**. You'll learn how to initialize a session, discover available resources using `resources/list`, and fetch their content using `resources/read`.

## 🎯 What You'll Learn

- **Session Initialization**: The mandatory first step for any compliant MCP session.
- **Resource Discovery**: How to ask a server for a list of available resources for a given URI scheme (`file` in our case).
- **Resource Reading**: How to get the actual data from a specific resource using its URI with the `resources/read` method.
- **URI Schemes**: Understand how URIs are used to identify and categorize resources.
- **2025-06-18 Features**: Enhanced metadata, title fields, and structured content responses.

## 🚀 Quick Start

### 1. Start the Server
```bash
cd mcp-decoded/02_server_engineering/03_exposing_resources/my_resources_server
uvicorn server:mcp_app --host 0.0.0.0 --port 8000
```

### 2. Import Collection
- Open Postman and import `MCP_Exposing_Resources.postman_collection.json`.

### 3. Run the Requests
Start with **"01. Initialize Session"** and work your way through the collection.

## 🔍 Understanding the Requests

### 1. Initialize Session
- The required first step. This establishes a session with the server and negotiates capabilities.

### 2. Send Initialized Notification  
- Required by 2025-06-18 specification to complete session setup.

### 3. List `file` Resources
- This request calls `resources/list` with the parameter `"scheme": "file"`.
- The server's `@mcp.resource_provider("file")` function is triggered, and it returns a list of all the files in our virtual file system.

### 4. Read Resource Content
- This request calls `resources/read` with a specific URI (e.g., `"uri": "file:///project/src/main.py"`).
- The server's `@mcp.resource_reader("file")` function is triggered. It looks up the URI in its virtual file system and returns the content.

### 5. Error: Resource Not Found
- This request tries to read a resource with a URI that does not exist.
- It demonstrates how the server handles a "file not found" scenario gracefully.

## 📋 Request Details

| Request | Method | Purpose | Expected Result |
|---------|--------|---------|-----------------|
| **01**  | `initialize` | Initialize session | Session details and capabilities from the server |
| **02**  | `notifications/initialized` | Complete session setup | Confirmation notification |
| **03**  | `resources/list` | Discover `file` resources | A list of virtual files with metadata |
| **04**  | `resources/read` | Read content of `main.py` | The structured content with metadata |
| **05**  | `resources/read` | Read a non-existent file | An error message with helpful information |

## 🎓 Learning Path

1. **Initialize**: Run request #01 to start the session.
2. **Complete Setup**: Run request #02 to finish initialization.
3. **Discover**: Run request #03 to see the list of exposed file resources.
4. **Read Content**: Run request #04. Examine the `contents` array in the response.
5. **Test Error**: Run request #05 to see how the server handles requests for resources it doesn't have.

## 🔧 Key Concepts Explained

### Resource vs Tool
- **Resources** (`resources/read`): For **getting information** - safe, read-only operations
- **Tools** (`tools/call`): For **performing actions** - can modify server state

### 2025-06-18 Specification Changes
- **Method Name**: Uses `resources/read` instead of `resources/get`
- **Response Structure**: Returns `contents` array with structured content objects
- **Enhanced Metadata**: Includes title fields, size information, and rich descriptions
- **Capabilities**: Server declares resource capabilities during initialization

### URI Schemes
- **Static**: `app:///messages/welcome` - Fixed path, always same content
- **Dynamic**: `app:///system/info` - Fixed path, content changes
- **Templated**: `users://{user_id}/profile` - Variable path with parameters

### MIME Types
- **text/plain**: Simple text content
- **text/markdown**: Markdown formatted content
- **application/json**: Structured JSON data
- **text/x-python**: Python source code

## 🔧 Customization Tips

### Testing Different Resource Types
Add requests to test other resource schemes:
- Change the `scheme` parameter to `"app"` or `"users"`
- Explore different URI patterns
- Test template resources with parameters

### Creating New Test Cases
1. Duplicate an existing request
2. Modify the URI parameter
3. Update the description
4. Test your changes

### Testing Template Resources
- Use URIs like `users://test_user/profile`
- Try different user IDs to see dynamic generation
- Observe how templates expand parameters

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Connection refused** | Make sure server is running on port 8000 |
| **404 Not Found** | Check the URL path is `/mcp` |
| **Resource not found** | Verify the URI exactly matches the server's resources |
| **Invalid JSON** | Check request body syntax |
| **Wrong method** | Ensure using `resources/read` not `resources/get` |

### Expected Response Structure (2025-06-18)
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "contents": [
      {
        "uri": "file:///project/src/main.py",
        "name": "main.py", 
        "title": "Source Code: main.py",
        "mimeType": "text/x-python",
        "text": "#!/usr/bin/env python3\n..."
      }
    ]
  }
}
```

### Expected Error Responses
- **Resource not found**: Structured error content in `contents` array
- **Invalid URI**: URI format validation error
- **Missing parameters**: Parameter validation error

## 🎯 Success Criteria

You've mastered this collection when you can:
- ✅ Successfully initialize sessions with proper capability negotiation
- ✅ Discover all available resources and understand their enhanced metadata
- ✅ Read static, dynamic, and templated resources using `resources/read`
- ✅ Parse structured content responses correctly
- ✅ Handle and interpret error responses
- ✅ Explain the differences from older MCP versions

## 💡 Real-World Applications

### Enhanced Metadata Usage
- **Title Fields**: Display user-friendly names in applications
- **Size Information**: Enable progress indicators for large resources
- **MIME Types**: Proper content handling and syntax highlighting
- **Structured Responses**: Easier parsing and error handling

### Resource Patterns
- **Documentation**: README files, API docs, help content
- **Configuration**: Settings, server config, environment variables
- **Data**: CSV files, JSON data, database exports
- **Templates**: Dynamic content generation with parameters

## 🔗 Next Steps

After completing this collection:
1. **Resource Templates**: Explore `resources/templates/list` endpoint
2. **Subscriptions**: Test resource change notifications
3. **Pagination**: Handle large resource collections
4. **Integration**: Use resources in AI applications for context

## 📚 Additional Resources

- [MCP 2025-06-18 Resources Specification](https://spec.modelcontextprotocol.io/specification/2025-06-18/server/resources/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [URI Template Specification](https://tools.ietf.org/html/rfc6570) 