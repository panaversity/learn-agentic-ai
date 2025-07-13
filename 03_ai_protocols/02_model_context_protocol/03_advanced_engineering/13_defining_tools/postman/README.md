# 🧰 MCP Defining Tools - Postman Testing Guide

This Postman collection demonstrates **all 5 essential MCP tool patterns** that every developer should know. Perfect for beginners learning how different tool return types work in MCP!

## 🎯 What You'll Test

### **5 Essential Tool Patterns**
1. **Simple List Tool** (`list_cities`) - Auto-wrapped primitives
2. **Simple Number Tool** (`get_temperature`) - Auto-wrapped floats  
3. **Structured Data Tool** (`get_weather`) - Pydantic models
4. **Rich Content Tool** (`add_numbers`) - TextContent with annotations
5. **Multi-Content Tool** (`analyze_data`) - Multiple content items

### **Plus Error Scenarios**
- Invalid tool names
- Missing required parameters
- Wrong parameter types

## 🚀 Quick Start (3 Steps)

### **Step 1: Start the Server**
```bash
cd my_tools_server
uv add mcp uvicorn httpx pydantic
uv run uvicorn server:mcp_app --host 0.0.0.0 --port 8000 --reload
```

### **Step 2: Import Collection**
- Open Postman
- Click **Import** → **Upload Files** 
- Select `MCP_Defining_Tools.postman_collection.json`

### **Step 3: Run Tests**
Start with **"01. Initialize Session"** and work through all 11 requests!

## 📋 Request Guide (Run in Order!)

| # | Request Name | Tool | What It Tests | Expected Result |
|---|--------------|------|---------------|------------------|
| **01** | Initialize Session | - | MCP session setup | Session established |
| **02** | Send Initialized | - | Complete initialization | Ready for operations |
| **03** | Discover Tools | - | Tool discovery | List of 5 tools |
| **04** | Simple List Tool | `list_cities` | Auto-wrapped list | `{"result": ["London", "Paris", "Tokyo"]}` |
| **05** | Simple Primitive | `get_temperature` | Auto-wrapped float | `{"result": 22.5}` |
| **06** | Structured Data | `get_weather` | Pydantic model | Rich WeatherData object |
| **07** | Rich Content | `add_numbers` | TextContent + annotations | Formatted content with metadata |
| **08** | Multi-Content | `analyze_data` | Multiple content items | Array of TextContent/ImageContent |
| **09** | Error: Invalid Tool | - | Error handling | Tool not found error |
| **10** | Error: Missing Param | `get_temperature` | Parameter validation | Missing parameter error |
| **11** | Error: Wrong Type | `add_numbers` | Type validation | Type conversion error |

## 🔍 Understanding Each Response Type

### **1. Auto-Wrapped Primitives (Requests 04-05)**
When tools return simple types, MCP wraps them automatically:

```json
// Request 04: list_cities
{
  "result": ["London", "Paris", "Tokyo"]
}

// Request 05: get_temperature  
{
  "result": 22.5
}
```

**Key Learning**: Simple return types are consistent across all MCP tools.

### **2. Structured Data (Request 06)**
Pydantic models return rich, validated objects:

```json
// Request 06: get_weather
{
  "temperature": 22.5,
  "humidity": 65.0, 
  "condition": "partly cloudy",
  "wind_speed": 12.3
}
```

**Key Learning**: No `{"result": ...}` wrapper for structured data.

### **3. Rich Content (Request 07)**
TextContent enables rich user experiences:

```json
// Request 07: add_numbers
{
  "content": [
    {
      "type": "text",
      "text": "🧮 **Addition Calculation**\n**Result:** 42.8",
      "annotations": {
        "audience": ["user", "assistant"],
        "priority": 1.0
      }
    }
  ]
}
```

**Key Learning**: Content arrays support rich formatting and metadata.

### **4. Multi-Content (Request 08)**
Multiple content items in one response:

```json
// Request 08: analyze_data
{
  "content": [
    {
      "type": "text", 
      "text": "📊 **Data Analysis Report**...",
      "annotations": {...}
    },
    {
      "type": "image",
      "data": "",
      "mimeType": "text/plain",
      "annotations": {...}
    }
  ]
}
```

**Key Learning**: Single tool can return multiple content types.

## 🎓 Learning Objectives

After completing this collection, you'll understand:

### **✅ Tool Return Types**
- When MCP auto-wraps responses vs. returns structured data
- How Pydantic models become structured output
- How TextContent enables rich user interfaces

### **✅ MCP Request Flow**
- Proper session initialization sequence
- How tool discovery works
- Error handling and validation

### **✅ Practical Applications**
- Simple tools: calculators, lookups, basic operations
- Structured tools: APIs, validated data, complex objects  
- Rich content: user interfaces, reports, dashboards

## 🔧 Customization Ideas

### **Try Different Values**
```json
// Experiment with get_temperature
{"city": "Tokyo"}
{"city": "New York"}

// Test add_numbers with different numbers
{"a": 100, "b": 200}
{"a": -5.5, "b": 3.14}

// Vary analyze_data parameters
{"data_type": "users", "sample_size": 1000}
{"data_type": "performance", "sample_size": 50}
```

### **Create New Requests**
1. Duplicate any request
2. Modify parameters
3. Update the description
4. Test your changes!

## 🐛 Troubleshooting

### **Connection Issues**
| Problem | Solution |
|---------|----------|
| **Connection refused** | Start server: `uvicorn server:mcp_app --port 8000` |
| **404 Not Found** | Check URL is `http://localhost:8000/mcp` |
| **Timeout** | Server might be starting - wait 10 seconds |

### **Expected Error Responses**
```json
// Invalid tool (Request 09)
{
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}

// Missing parameter (Request 10)  
{
  "error": {
    "code": -32602,
    "message": "Invalid params"
  }
}

// Wrong type (Request 11)
{
  "error": {
    "code": -32602, 
    "message": "Type validation error"
  }
}
```

## 🎯 Success Criteria

You've mastered MCP tools when you can:
- ✅ Run all 11 requests successfully
- ✅ Understand the 4 different response patterns
- ✅ Explain when to use each tool type
- ✅ Modify requests to test your own scenarios
- ✅ Interpret both success and error responses

## 🔗 What's Next?

After mastering this collection:
1. **Lesson 03**: Learn about MCP resources (data that tools reference)
2. **Lesson 04**: Explore prompt templates for AI interactions
3. **Build Your Own**: Create tools for your specific use cases
4. **Advanced Features**: Error handling, async tools, complex workflows

## 💡 Pro Tips

1. **Always start with initialization**: Requests 01-02 are mandatory
2. **Watch the response structure**: Notice how different return types are formatted
3. **Use Postman's JSON viewer**: Makes complex responses easier to read
4. **Test error scenarios**: Understanding failures helps debug real applications
5. **Experiment with parameters**: Try edge cases and different values

## 📚 Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Pydantic Models Guide](https://docs.pydantic.dev/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

This collection gives you hands-on experience with every major MCP tool pattern. Master these basics and you'll be ready to build any kind of MCP tool! 