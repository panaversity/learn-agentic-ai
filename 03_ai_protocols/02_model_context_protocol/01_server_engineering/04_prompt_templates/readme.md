# 💬 MCP Prompt Templates Server - 2025-06-18 Compliant

> **🎯 Educational Focus**: This lesson demonstrates **prompt templates** - one of MCP's core capabilities for creating structured AI prompts with dynamic parameters.

**Building on Previous Lessons**: You've learned about Tools (actions) and Resources (data). Now let's explore **Prompt Templates** - **reusable conversation patterns** that guide AI interactions.

### 🤔 What Are MCP Prompt Templates? (Simple Explanation)

**Simple Definition**: MCP Prompt Templates are **pre-written conversation starters** with placeholders that AI can customize and use.

**Real-World Analogy**: Think of prompt templates like:
- 📝 **Email templates** - You have a structure, just fill in the details
- 🗣️ **Conversation scripts** - Actors have lines, but they adapt to the scene
- 📋 **Form letters** - Standard format with personalized information
- 🎭 **Mad Libs** - Fixed story with blanks to fill in

### 🏗️ MCP Prompt Templates vs. What You Know

| **If you're familiar with...** | **MCP Prompt Templates are like...** | **Key advantage** |
|-------------------------------|---------------------------------------|-------------------|
| **System Prompts in OpenAI** | System prompts, but reusable and shareable | Works across all AI platforms |
| **Email Templates** | Email templates with dynamic content | Designed specifically for AI conversations |
| **Jinja2/Handlebars Templates** | Template engines for text generation | Built-in parameter validation |
| **Function Documentation** | API docs that explain how to interact | AI can discover and use automatically |

### 🎯 Why Prompt Templates Matter

**The Problem**: Writing effective AI prompts is:
- ⏰ **Time-consuming**: Crafting the perfect prompt takes effort
- 🔄 **Repetitive**: Same patterns used over and over
- 📚 **Hard to remember**: Complex prompts are difficult to recall
- 👥 **Not shareable**: Each team member writes their own variations

**The MCP Prompt Templates Solution**:
- ✅ **Reusable**: Write once, use everywhere
- ✅ **Parameterized**: Customize for specific situations
- ✅ **Discoverable**: AI can find and choose appropriate templates
- ✅ **Consistent**: Standardized quality across all interactions

### 🔗 How Prompt Templates Work With Tools and Resources

**The Complete MCP Ecosystem**:
1. 📚 **Resources** provide context and data
2. 💬 **Prompt Templates** structure the conversation
3. 🔧 **Tools** enable AI to take actions
4. 🤖 **AI** combines everything to provide intelligent responses



This implementation is **fully compliant with the 2025-06-18 MCP Prompts specification** and provides both simple educational prompts and advanced parametric templates.

## 🌟 What You'll Learn

### **Core MCP Prompts Concepts**
- **Prompt Discovery**: Using `prompts/list` to find available templates
- **Prompt Generation**: Using `prompts/get` to create customized prompts
- **Parameter Handling**: Dynamic prompt customization with type validation
- **2025-06-18 Features**: Title fields, enhanced metadata, and capabilities declaration

## 🚀 Quick Start

### **Terminal 1: Start the Enhanced Server**
```bash
cd my_prompts_server
uv add mcp uvicorn httpx
uv run uvicorn server:mcp_app --host 0.0.0.0 --port 8000 --reload
```

### **Terminal 2: Test with Client**
```bash
uv run python client.py
```

### **Postman Testing (Recommended)**
1. Import: `postman/MCP_Prompt_Templates.postman_collection.json`
2. Test educational prompts and error handling scenarios
3. Explore advanced parametric templates

## 📋 2025-06-18 Specification Coverage

✅ **Core Features (5/5)**
- Prompt definitions with `@mcp.prompt()` decorators
- Prompt discovery via `prompts/list`
- Prompt generation via `prompts/get`
- Parameter validation
- Error handling for invalid prompts/parameters

## 📚 Available Prompt Templates

### **🎓 Educational Prompts (Simple)**
Perfect for learning MCP basics and Postman testing:

#### **`summarize`** - Basic Text Summarization
- **Purpose**: Simple educational summarization
- **Parameters**: `text` (required)
- **Returns**: Single formatted message
- **Use Case**: Learning prompt basics, Postman compatibility

#### **`debug_error`** - Simple Debugging Help
- **Purpose**: Basic debugging conversation starter
- **Parameters**: `error_message`, `code_snippet` (both required)
- **Returns**: Multi-message conversation structure
- **Use Case**: Understanding conversation patterns

## 🔗 Integration Examples

### **Real-World Applications**
- **Content Management**: Automated summarization of documents and articles
- **Developer Tools**: Code review and debugging assistance
- **Educational Platforms**: Adaptive learning conversations
- **Business Intelligence**: Analysis and reporting automation
- **Technical Writing**: Documentation generation and review

### **Architecture Patterns**
- **Microservices**: Prompt servers as specialized services
- **AI Pipelines**: Multi-stage prompt processing workflows
- **Knowledge Bases**: Dynamic prompt generation from data
- **User Interfaces**: Interactive prompt builders and testers

## 💡 Pro Tips

1. **Start Simple**: Begin with basic `summarize` and `debug_error` prompts
2. **Parameter Design**: Use clear, intuitive parameter names and validation
3. **Error Messages**: Provide helpful validation errors for debugging
4. **Documentation**: Include comprehensive help and examples
5. **Testing**: Use Postman collection for systematic testing
6. **Resource Integration**: Leverage MCP resources for dynamic content
7. **Conversation Design**: Structure multi-message flows logically
8. **Performance**: Consider prompt generation speed and complexity

This implementation demonstrates the full power of MCP prompt templates while maintaining educational clarity and 2025-06-18 specification compliance!
