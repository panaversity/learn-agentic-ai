# 🧰 MCP Defining Tools - Postman Collection

This Postman collection demonstrates how to test an MCP server with **multiple tools**. You'll learn how to discover available tools and execute them with different parameters.

## 🎯 What You'll Learn

- **Tool Discovery**: How to find out what tools a server provides
- **Tool Execution**: How to call tools with proper parameters
- **Parameter Validation**: Understanding type checking and required fields
- **Error Handling**: What happens when things go wrong

## 🚀 Quick Start

### 1. Start the Server
```bash
cd 03_ai_protocols/02_model_context_protocol/01_server_development/02_defining_tools/my_tools_server
uvicorn server:mcp_app --host 0.0.0.0 --port 8000
```

### 2. Import Collection
- Open Postman
- Click **Import** → **Upload Files**
- Select `MCP_Defining_Tools.postman_collection.json`

### 3. Run the Requests
Start with **"01. Discover Available Tools"** and work your way through!

## 🔍 Understanding the Requests

### 1. Tool Discovery
**Purpose**: Find out what tools the server provides

**What to expect**:
- Server returns list of available tools
- Each tool includes name, description, and parameter schema
- Should see `add` and `greet` tools

### 2. Calculator Tool Tests
**Purpose**: Test the `add` tool with different scenarios

**Variations**:
- **Basic Addition**: Simple positive numbers (5 + 7 = 12)
- **Large Numbers**: Test with bigger values (1000 + 2500 = 3500)
- **Negative Numbers**: Mixed positive/negative (-10 + 15 = 5)

### 3. Greeter Tool Tests
**Purpose**: Test the `greet` tool with different names

**Variations**:
- **Basic Greeting**: Standard name ("Student")
- **Different Names**: Try various names ("Alice", "Bob", etc.)
- **Edge Cases**: Empty names or special characters

### 4. Error Scenarios
**Purpose**: Understand how the server handles mistakes

**Error Types**:
- **Invalid Tool**: Calling a tool that doesn't exist
- **Missing Parameters**: Forgetting required arguments
- **Wrong Types**: Passing strings instead of numbers
- **Edge Cases**: Empty or unusual values

## 📋 Request Details

| Request | Tool | Purpose | Expected Result |
|---------|------|---------|----------------|
| **01** | - | Discover tools | List of `add` and `greet` tools |
| **02** | `add` | Basic addition | `12` |
| **03** | `add` | Large numbers | `3500` |
| **04** | `add` | Negative numbers | `5` |
| **05** | `greet` | Basic greeting | `"Hello, Student! Welcome..."` |
| **06** | `greet` | Different name | `"Hello, Alice! Welcome..."` |
| **07** | - | Invalid tool | Error response |
| **08** | `add` | Missing parameter | Validation error |
| **09** | `add` | Wrong type | Type error |
| **10** | `greet` | Empty name | `"Hello, ! Welcome..."` |

## 🎓 Learning Path

### For Beginners
1. **Start with Discovery**: Run request #01 to see available tools
2. **Try Basic Calls**: Run requests #02 and #05 for successful examples
3. **Experiment**: Change parameters in requests #03, #04, #06
4. **Learn from Errors**: Run requests #07-#10 to see error handling

### For Advanced Users
1. **Modify Parameters**: Edit request bodies to test edge cases
2. **Add New Tests**: Create requests for boundary conditions
3. **Analyze Schemas**: Study the tool schemas returned by discovery
4. **Compare Responses**: Notice differences between sync/async tools

## 🔧 Customization Tips

### Testing Your Own Values
- **Calculator**: Change `a` and `b` values in add tool requests
- **Greeter**: Modify the `name` parameter with different strings
- **Error Testing**: Try invalid parameter combinations

### Adding New Requests
1. Duplicate an existing request
2. Modify the parameters
3. Update the description
4. Test your changes

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Connection refused** | Make sure server is running on port 8000 |
| **404 Not Found** | Check the URL path is `/mcp` |
| **Invalid JSON** | Verify request body syntax |
| **Tool not found** | Ensure tool name matches exactly |

### Expected Error Responses
- **Invalid tool**: `{"error": {"code": -32601, "message": "Method not found"}}`
- **Missing parameter**: Validation error with details
- **Wrong type**: Type conversion error

## 🎯 Success Criteria

You've mastered this collection when you can:
- ✅ Discover all available tools
- ✅ Successfully call both `add` and `greet` tools
- ✅ Handle different parameter types and values
- ✅ Understand and interpret error responses
- ✅ Modify requests to test your own scenarios

## 🔗 Next Steps

After completing this collection:
1. **Try Other Examples**: Explore other MCP server examples
2. **Build Your Own**: Create a server with custom tools
3. **Advanced Features**: Learn about resources, prompts, and notifications
4. **Integration**: Connect MCP servers to AI applications

## 📚 Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) 