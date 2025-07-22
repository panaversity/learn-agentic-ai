# 04: [Dynamic Tool Filtering](https://openai.github.io/openai-agents-python/mcp/#dynamic-tool-filtering) with MCPServerStreamableHttp

## What Are We Learning? (The “Why”)

In this step, you’ll learn how to **dynamically control which tools your agent can see and use**—not just with a fixed list, but with custom logic that can change based on the agent, the server, or even the current situation.

- **Why is this important?**
  - Sometimes you want to show or hide tools based on who the user is, what the agent is doing, or other runtime conditions.
  - Dynamic filtering gives you fine-grained, context-aware control over your agent’s toolbox.
  - This is a “next step” after static filtering, and is essential for building smart, adaptive, and secure agentic systems.

---

## What’s the Big Idea?

- **Dynamic tool filtering** means you write a function that decides, for each tool, whether it should be available—using information about the agent, the server, and the current context.
- Your filter can be synchronous or asynchronous, and can use any logic you want.

---

## How Does It Work? (The “How”)

1. **Write a filter function** that takes a `ToolFilterContext` and a tool, and returns `True` (show the tool) or `False` (hide it).
2. **Pass your filter function** as the `tool_filter` when creating your MCP server client.
3. **The SDK will call your function** for each tool, every time it needs to know which tools are available.

---

## Step-by-Step Example

### 1. Import the context type:
```python
from agents.mcp import ToolFilterContext
```

### 2. Write your filter function:
```python
def custom_filter(context: ToolFilterContext, tool) -> bool:
    # Only allow tools that start with "mood"
    return tool.name.startswith("mood")
```

Or, for context-aware logic:
```python
def context_aware_filter(context: ToolFilterContext, tool) -> bool:
    # Only allow tools for a specific agent
    return context.agent.name == "MyMCPConnectedAssistant" and tool.name == "mood_from_shared_server"
```

Or, for async logic:
```python
async def async_filter(context: ToolFilterContext, tool) -> bool:
    # Example: check a database or external API before allowing the tool
    return await some_async_check(context, tool)
```

### 3. Use your filter when creating the MCP server client:
```python
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

mcp_params = MCPServerStreamableHttpParams(url="http://localhost:8001/mcp/")
async with MCPServerStreamableHttp(params=mcp_params, tool_filter=custom_filter, name="MyDynamicMCPServer") as mcp_server_client:
    # ... set up your agent and run as before ...
```

---

## What Should You Notice?

- The available tools can change depending on the agent, the server, or any other logic you put in your filter.
- This is much more flexible than static filtering, and lets you build smarter, more secure agents.

---

## Why Is This a Good Learning Step?

- **It’s adaptive:** Your agent’s toolbox can change as needed.
- **It’s powerful:** You can use any logic, including async checks or external data.
- **It’s real-world:** Most production systems need this kind of flexibility.

---

**In summary:**  
You’re learning how to give your agent a “smart menu” of tools that can change based on context—an essential skill for building advanced, real-world agentic systems.
