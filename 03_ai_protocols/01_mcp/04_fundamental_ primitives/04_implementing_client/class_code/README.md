# MCP ClientSession Learning Project

This repository contains code examples and learning materials from our **Class-04: Model Context Protocol - Implementing Core MCP Client** session.

## 📺 Class Recording

**YouTube Live Session:** [Class-04: Model Context Protocol - Implementing Core MCP Client](https://www.youtube.com/live/0DYPJyfmR1E?si=mRJQsvn0g2B7nZJA)

## 🎯 Learning Objectives

This project demonstrates the progressive learning approach for understanding Model Context Protocol (MCP) client implementation:

1. **Python Basics** - Understanding async/await and context managers
2. **Simple Server-Sent Events** - Basic HTTP streaming with requests
3. **Proper MCP Client** - Full MCP client implementation

## 📁 Project Structure

```
mcp_client/
├── main.py          # Python basics - async context managers
├── dump.py          # Simple SSE example using requests
├── client.py        # Proper MCP client implementation
├── pyproject.toml   # Project dependencies
├── data.txt         # Sample data file
├── out.txt          # Output file
└── README.md        # This file
```

## 🚀 Learning Progression

### 1. Python Basics (`main.py`)

**Topics Covered:**
- Async/await syntax
- Context managers (`async with`)
- `AsyncExitStack` for managing multiple async contexts
- Custom async context manager classes

**Key Concepts:**
```python
# Basic async context manager
async def get_connection(name):
    class Ctx():
        async def __aenter__(self):
            print(f"ENTER... {name}")
            return name
        async def __aexit__(self, exc_type, exc, tb):
            print(f"EXIT! {name}")
    return Ctx()

# Using AsyncExitStack for multiple contexts
async with AsyncExitStack() as stack:
    a = await stack.enter_async_context(await get_connection("A"))
    b = await stack.enter_async_context(await get_connection("B"))
```

### 2. Server-Sent Events (`dump.py`)

**Topics Covered:**
- HTTP streaming with `requests`
- JSON-RPC 2.0 protocol
- Processing streaming responses
- Basic MCP communication

**Key Concepts:**
```python
# Streaming HTTP request
response = requests.post(URL, json=PAYLOAD, headers=HEADERS, stream=True)

# Processing streaming response
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### 3. Proper MCP Client (`client.py`)

**Topics Covered:**
- MCP ClientSession implementation
- Tool listing and calling
- Resource management
- Proper async context management

**Key Concepts:**
```python
class MCPClient:
    async def __aenter__(self):
        read, write, _ = await self.stack.enter_async_context(
            streamablehttp_client(self.url)
        )
        self._sess = await self.stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._sess.initialize()
        return self
    
    async def list_tools(self) -> types.Tool:
        return (await self._sess.list_tools()).tools
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.13 or higher
- An MCP server running on `http://localhost:8000/mcp`

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mcp_client
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

    **OR**

   ```bash
   pip install -e .
   ```

3. **Run examples:**

   **Python Basics:**
   ```bash
   python main.py
   ```

   **SSE Example (uncomment in dump.py):**
   ```bash
   python dump.py
   ```

   **MCP Client:**
   ```bash
   python client.py
   ```

## 📚 Dependencies

- `mcp>=1.12.1` - Model Context Protocol library
- `requests>=2.32.4` - HTTP library for streaming

## 🎓 Learning Outcomes

After completing this project, students will understand:

1. **Async Programming in Python**
   - Context managers and async context managers
   - Managing multiple async resources
   - Proper cleanup and resource management

2. **HTTP Streaming**
   - Server-Sent Events (SSE)
   - JSON-RPC 2.0 protocol
   - Streaming HTTP responses

3. **MCP Client Implementation**
   - MCP ClientSession usage
   - Tool discovery and invocation
   - Proper client lifecycle management

## 🔗 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

## 📝 Notes

This project is designed for educational purposes and demonstrates the progressive learning approach from basic Python concepts to full MCP client implementation. Each file builds upon the previous concepts, making it easier for students to understand the complete picture.

---
  
**Class:** Class-04: Model Context Protocol - Implementing Core MCP Client  
**Date:** 24 July 2025 
**YouTube:** [https://www.youtube.com/live/0DYPJyfmR1E?si=mRJQsvn0g2B7nZJA](https://www.youtube.com/live/0DYPJyfmR1E?si=mRJQsvn0g2B7nZJA)
