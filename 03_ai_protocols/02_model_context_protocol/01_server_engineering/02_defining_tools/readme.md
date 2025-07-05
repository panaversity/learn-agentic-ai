# 02: Defining Tools - Complete Tool Scenarios Guide

**Objective:** Learn how to create MCP tools that cover all major output types: simple primitives, structured data, and advanced content. This lesson is perfect for beginners who want to understand how tools work in MCP.

**Building on Lesson 01**: You learned that Tools are one of MCP's three building blocks. Now let's dive deep into what makes tools powerful and how to design them effectively.

### 🤔 What Are MCP Tools? (Extended Explanation)

**Simple Definition**: MCP Tools are **functions that AI can discover and call** to perform actions in the real world.

**The Magic**: Unlike regular function calls, MCP tools are:
- 🔍 **Discoverable**: AI can ask "what can you do?" and get a list
- 📝 **Self-Describing**: Each tool explains what it does and what parameters it needs
- 🔧 **Callable**: AI can execute tools and get structured responses
- 🌐 **Universal**: Works with any AI model that supports MCP

### 🏗️ MCP Tools vs. What You Know

| **If you're familiar with...** | **MCP Tools are like...** | **Key advantage** |
|-------------------------------|----------------------------|-------------------|
| **OpenAI Function Calling** | Function calling, but standardized | Works with any AI model, not just OpenAI |
| **REST API Endpoints** | API endpoints the AI can call | Built-in discovery and documentation |
| **Python Functions** | Functions with automatic AI-friendly wrapping | AI can find and use them automatically |
| **CLI Commands** | Commands the AI can run | Structured input/output, type safety |

### 🎯 Why Tools Matter for AI Development

**The Problem**: AI models can reason and plan, but they can't:
- Get real-time data (weather, news, prices)
- Perform calculations or data processing
- Interact with databases or APIs
- Take actions in external systems

**The MCP Tools Solution**:
- ✅ **Extend AI capabilities**: Give AI access to any function you can write
- ✅ **Type safety**: Parameters and responses are validated automatically
- ✅ **Rich responses**: Return simple data, complex objects, or rich content
- ✅ **Discoverability**: AI can explore and learn about available tools

### 🎯 What You'll Learn

By the end of this lesson, you'll understand:
- **Simple Tools**: Tools that return basic types (strings, numbers, lists)
- **Structured Tools**: Tools that return complex objects using Pydantic models
- **Advanced Tools**: Tools that return rich content with annotations
- **How MCP handles different return types automatically**

## 🛠️ Our Tool Server Scenarios

Our server demonstrates **5 essential tool patterns** that cover every major use case:

### **1. Simple List Tool (`list_cities`)**
```python
@mcp.tool()
def list_cities() -> list[str]:
    """Get a list of cities"""
    return ["London", "Paris", "Tokyo"]
    # MCP automatically wraps this as: {"result": ["London", "Paris", "Tokyo"]}
```
- **Returns:** A simple list of strings
- **MCP Magic:** Automatically wrapped in `{"result": ...}` format
- **Use Case:** When you need to return simple data types

### **2. Simple Number Tool (`get_temperature`)**
```python
@mcp.tool()
def get_temperature(city: str) -> float:
    """Get temperature as a simple float"""
    return 22.5
    # MCP automatically wraps this as: {"result": 22.5}
```
- **Returns:** A simple float number
- **MCP Magic:** Automatically wrapped for consistency
- **Use Case:** Calculator functions, simple measurements

### **3. Structured Data Tool (`get_weather`)**
```python
class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage") 
    condition: str
    wind_speed: float

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get structured weather data"""
    return WeatherData(
        temperature=22.5, humidity=65.0, 
        condition="partly cloudy", wind_speed=12.3
    )
```
- **Returns:** Rich structured object with validation
- **MCP Magic:** Automatically generates JSON schema from Pydantic model
- **Use Case:** APIs, complex data that needs validation

### **4. Advanced Content Tool (`add_numbers`)**
```python
@mcp.tool(structured_output=True)
def add_numbers(a: float, b: float) -> list[TextContent]:
    """Demonstrates advanced structured tool output with rich annotations"""
    result = a + b
    calculation_text = f"🧮 **Addition Calculation**\n**Result:** {result}"
    
    return [
        TextContent(
            type="text",
            text=calculation_text,
            annotations=Annotations(
                audience=["user", "assistant"],
                priority=1.0
            )
        )
    ]
```
- **Returns:** Rich content with metadata and annotations
- **MCP Magic:** Supports multiple content types and audience targeting
- **Use Case:** User interfaces, reports, rich displays

### **5. Multi-Content Tool (`analyze_data`)**
```python
@mcp.tool(structured_output=True)
async def analyze_data(data_type: str, sample_size: int = 100) -> list[TextContent | ImageContent]:
    """Demonstrates multi-content structured tool output"""
    # Returns multiple content items for different purposes
    return [
        TextContent(...),  # Summary report
        ImageContent(...)  # Chart or visualization
    ]
```
- **Returns:** Multiple content items in one response
- **MCP Magic:** Supports mixing text, images, and other content types
- **Use Case:** Dashboards, comprehensive reports, multi-media responses

## 🚀 Quick Start Guide

### **Step 1: Start the Server**
```bash
cd my_tools_server
uv add mcp uvicorn httpx pydantic
uv run uvicorn server:mcp_app --host 0.0.0.0 --port 8000 --reload
```

### **Step 2: Test with Client**
```bash
uv run python client.py
```

### **Step 3: Try Postman Collection**
Import `postman/MCP_Defining_Tools.postman_collection.json` and run the requests!

## 📊 Understanding Tool Output Types

### **Auto-Wrapped Primitives**
When your tool returns simple types, MCP automatically wraps them:

| Your Return | MCP Response |
|-------------|--------------|
| `"hello"` | `{"result": "hello"}` |
| `42` | `{"result": 42}` |
| `[1, 2, 3]` | `{"result": [1, 2, 3]}` |
| `True` | `{"result": true}` |

### **Structured Output (Pydantic Models)**
When you return Pydantic models, MCP creates rich schemas:

```python
# Your model
class User(BaseModel):
    name: str
    age: int
    email: str | None = None

# MCP generates schema automatically and validates output
```

### **Advanced Content (TextContent/ImageContent)**
For rich user interfaces and complex displays:

```python
# Multiple content items with metadata
return [
    TextContent(type="text", text="Summary...", annotations={...}),
    ImageContent(type="image", data=chart_data, mimeType="image/png")
]
```

## 🧪 Testing Each Tool Type

### **1. Simple Tools**
```bash
# Test list_cities
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_cities", "arguments": {}}, "id": 1}'

# Expected: {"result": ["London", "Paris", "Tokyo"]}
```

### **2. Structured Tools**  
```bash
# Test get_weather
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "London"}}, "id": 1}'

# Expected: Rich WeatherData object with temperature, humidity, etc.
```

### **3. Advanced Tools**
```bash
# Test add_numbers
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "add_numbers", "arguments": {"a": 10, "b": 5}}, "id": 1}'

# Expected: Rich TextContent with annotations
```

## 📁 Project Structure

```
02_defining_tools/
├── my_tools_server/
│   ├── server.py      # Main server with 5 tool scenarios
│   └── client.py      # Demo client that tests all tools
├── postman/
│   ├── MCP_Defining_Tools.postman_collection.json  # Test collection
│   └── README.md      # Postman testing guide
└── readme.md          # This guide
```

## 🔍 Expected Client Output

When you run `uv run python client.py`, you'll see:

```
--- MCP Tool Client Demonstration ---

[Step 1: Initializing Session]
   -> Success! Connected to: my-tools-server
   -> Protocol version: 2025-06-18

[Step 2: Discovering Tools]
   -> Success! Server has 5 tools:
      - list_cities: Get a list of cities
      - get_temperature: Get temperature as a simple float  
      - get_weather: Get structured weather data
      - add_numbers: Demonstrates BASIC structured tool output
      - analyze_data: Demonstrates MULTI-CONTENT structured tool output

[Step 3: Testing Simple Tools (Auto-wrapped Results)]
Testing list_cities...
   -> Cities: {'result': ['London', 'Paris', 'Tokyo']}
Testing get_temperature...
   -> Temperature: {'result': 22.5}

[Step 4: Testing Pydantic Model Tool (Structured Output)]
Testing get_weather...
   -> Weather Data: {'temperature': 22.5, 'humidity': 65.0, 'condition': 'partly cloudy', 'wind_speed': 12.3}

[Step 5: Testing Advanced Structured Output (TextContent)]
Testing add_numbers...
   -> Content 1: 🧮 **Addition Calculation**
                 **Result:** 42.8
   -> Annotations: {'audience': ['user', 'assistant'], 'priority': 1.0}

[Step 6: Testing Multi-Content Tool]
Testing analyze_data...
   -> Received 2 content items:
   -> Item 1 (text): 📊 **Data Analysis Report**...
   -> Item 2 (image): [Image content with metadata]

--- Demonstration Complete ---
```

## 🎓 Key Learning Points

### **✅ Tool Return Types**
- **Simple types** (str, int, float, list, bool) are auto-wrapped in `{"result": value}`
- **Pydantic models** become structured output with automatic schema generation
- **TextContent/ImageContent lists** enable rich, multi-part responses

### **✅ When to Use Each Type**
- **Simple returns**: Basic calculations, lookups, simple operations
- **Structured returns**: APIs, validated data, complex objects
- **Advanced content**: User interfaces, reports, rich displays

### **✅ MCP Magic**
- Automatic schema generation from type hints
- Built-in validation for Pydantic models  
- Consistent JSON-RPC response formatting
- Support for async and sync functions

## 🔄 Tool Development Workflow

1. **Start Simple**: Begin with basic return types to test your logic
2. **Add Structure**: Use Pydantic models when you need validation
3. **Enhance Experience**: Add TextContent for rich user experiences
4. **Test Everything**: Use the client and Postman to verify behavior

## 🚧 Common Gotchas

### **Type Hints Are Required**
```python
# ❌ Won't work - no type hints
@mcp.tool()
def bad_tool(x):
    return x

# ✅ Works - proper type hints
@mcp.tool()
def good_tool(x: str) -> str:
    return x
```

### **Pydantic vs Regular Classes**
```python
# ✅ Works - Pydantic model with proper annotations
class User(BaseModel):
    name: str
    age: int

# ❌ Won't work - regular class without type hints
class BadUser:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

## 🎯 Next Steps

After mastering this lesson:
- **Lesson 03**: Learn about resources (data that tools can reference)
- **Lesson 04**: Explore prompt templates for AI interactions
- **Advanced Topics**: Error handling, async tools, tool composition

## 💡 Pro Tips

1. **Use Pydantic for APIs**: When your tool talks to external services
2. **Use TextContent for UIs**: When humans will see the output
3. **Start simple, add complexity**: Begin with basic returns, enhance later
4. **Test with Postman**: Visual testing makes debugging easier
5. **Check the auto-generated schemas**: MCP creates OpenAPI-style schemas automatically

This lesson gives you everything you need to build tools that handle any scenario. The patterns here will work for simple calculators all the way up to complex AI-powered applications!