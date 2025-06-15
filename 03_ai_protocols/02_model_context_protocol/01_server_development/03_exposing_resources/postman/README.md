# 📚 MCP Exposing Resources - Postman Collection

This Postman collection demonstrates how to test an MCP server with **resources**. You'll learn the difference between tools and resources, and how to work with static, dynamic, and templated resources.

## 🎯 What You'll Learn

- **Resource vs Tool Distinction**: Understanding when to use resources (read-only data) vs tools (actions)
- **Resource Discovery**: How to find available resources on a server
- **Static Resources**: Content that never changes
- **Dynamic Resources**: Content generated on-demand (like current time)
- **Templated Resources**: Parameterized resources (like user profiles by ID)
- **URI Patterns**: How to construct and use resource URIs

## 🚀 Quick Start

### 1. Start the Server
```bash
cd 03_ai_protocols/02_model_context_protocol/01_server_development/03_exposing_resources/my_resources_server
uvicorn server:mcp_app --host 0.0.0.0 --port 8000
```

### 2. Import Collection
- Open Postman
- Click **Import** → **Upload Files**
- Select `MCP_Exposing_Resources.postman_collection.json`

### 3. Run the Requests
Start with **"01. Discover Available Resources"** and work your way through!

## 🔍 Understanding the Requests

### 1. Resource Discovery
**Purpose**: Find out what resources the server provides

**What to expect**:
- Server returns list of available resources
- Each resource includes URI, name, description, and MIME type
- Should see 3 resources: welcome message, server time, and user profile template

### 2. Static Resource Tests
**Purpose**: Test resources that return the same content every time

**Resource**: `app:///messages/welcome`
- **Type**: Static text message
- **Behavior**: Always returns the same welcome message
- **Use Case**: Fixed content like help text, configuration, or static data

### 3. Dynamic Resource Tests
**Purpose**: Test resources that generate content on-demand

**Resource**: `app:///system/time`
- **Type**: Dynamic JSON object
- **Behavior**: Returns current server time (changes with each request)
- **Use Case**: Real-time data like timestamps, system status, or live metrics

### 4. Templated Resource Tests
**Purpose**: Test parameterized resources that accept variables

**Resource**: `users://{user_id}/profile`
- **Type**: Templated resource
- **Behavior**: Returns user-specific content based on the user_id parameter
- **Use Case**: User profiles, file content, database records by ID

### 5. Error Scenarios
**Purpose**: Understand how the server handles invalid requests

**Error Types**:
- **Invalid URIs**: Resources that don't exist
- **Malformed URIs**: Incorrect URI format
- **Missing Parameters**: Required parameters not provided
- **Wrong Template Format**: Incorrect use of templated resources

## 📋 Request Details

| Request | Resource Type | URI | Purpose | Expected Result |
|---------|---------------|-----|---------|----------------|
| **01** | Discovery | - | List resources | 3 resources with metadata |
| **02** | Static | `app:///messages/welcome` | Welcome message | Static text string |
| **03** | Dynamic | `app:///system/time` | Current time | JSON with timestamp |
| **04** | Templated | `users://jane.doe/profile` | User profile | Profile for jane.doe |
| **05** | Templated | `users://john.smith/profile` | User profile | Profile for john.smith |
| **06** | Templated | `users://alice_123/profile` | User profile | Profile for alice_123 |
| **07** | Templated | `users://user-with-dashes/profile` | User profile | Profile with special chars |
| **08** | Dynamic | `app:///system/time` | Time comparison | Different timestamp |
| **09** | Error | `app:///nonexistent/resource` | Invalid URI | Error response |
| **10** | Error | `invalid-uri-format` | Malformed URI | Error response |
| **11** | Error | (missing URI) | Missing parameter | Validation error |
| **12** | Error | `users:///profile` | Wrong template | Error response |

## 🎓 Learning Path

### For Beginners
1. **Start with Discovery**: Run request #01 to see all available resources
2. **Try Static Resource**: Run request #02 multiple times - notice it's always the same
3. **Try Dynamic Resource**: Run request #03 multiple times - notice the time changes
4. **Try Templated Resources**: Run requests #04-#07 with different user IDs
5. **Learn from Errors**: Run requests #09-#12 to understand error handling

### For Advanced Users
1. **Compare Resource Types**: Notice differences between static, dynamic, and templated
2. **Analyze URI Patterns**: Study how different URI schemes work
3. **Test Edge Cases**: Try unusual user IDs or URI formats
4. **Performance Testing**: Compare response times between resource types

## 🔧 Key Concepts Explained

### Resource vs Tool
- **Resources** (`resources/read`): For **getting information** - safe, read-only operations
- **Tools** (`tools/call`): For **performing actions** - can modify server state

### URI Schemes
- **Static**: `app:///messages/welcome` - Fixed path, always same content
- **Dynamic**: `app:///system/time` - Fixed path, content changes
- **Templated**: `users://{user_id}/profile` - Variable path with parameters

### MIME Types
- **text/plain**: Simple text content
- **application/json**: Structured JSON data
- **Other types**: Images, HTML, XML, etc. (not in this example)

## 🔧 Customization Tips

### Testing Different User IDs
Modify the templated resource requests to test with your own user IDs:
- Change `jane.doe` to any string you want
- Try special characters, numbers, or symbols
- See how the server responds to different formats

### Creating New Test Cases
1. Duplicate an existing request
2. Modify the URI parameter
3. Update the description
4. Test your changes

### Comparing Dynamic Resources
- Run request #03 (server time) multiple times
- Run request #08 immediately after #03
- Compare the timestamps to see the dynamic behavior

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Connection refused** | Make sure server is running on port 8000 |
| **404 Not Found** | Check the URL path is `/mcp` |
| **Resource not found** | Verify the URI exactly matches the server's resources |
| **Invalid JSON** | Check request body syntax |

### Expected Error Responses
- **Invalid resource**: `{"error": {"code": -32601, "message": "Method not found"}}`
- **Missing URI**: Validation error with parameter details
- **Malformed URI**: URI format error

## 🎯 Success Criteria

You've mastered this collection when you can:
- ✅ Discover all available resources and understand their metadata
- ✅ Successfully read static, dynamic, and templated resources
- ✅ Understand the difference between resource types
- ✅ Use templated resources with different parameters
- ✅ Handle and interpret error responses
- ✅ Explain when to use resources vs tools

## 💡 Real-World Applications

### Static Resources
- Configuration files
- Help documentation
- Terms of service
- Static content

### Dynamic Resources
- System status
- Current metrics
- Live data feeds
- Real-time information

### Templated Resources
- User profiles
- File contents by path
- Database records by ID
- Personalized content

## 🔗 Next Steps

After completing this collection:
1. **Combine with Tools**: Try servers that have both tools and resources
2. **Build Your Own**: Create a server with custom resources
3. **Advanced Patterns**: Learn about resource subscriptions and notifications
4. **Integration**: Use resources in AI applications for context

## 📚 Additional Resources

- [MCP Specification - Resources](https://spec.modelcontextprotocol.io/specification/basic/resources/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [URI Template Specification](https://tools.ietf.org/html/rfc6570) 