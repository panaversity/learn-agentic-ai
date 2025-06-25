# MCP Request Cancellation Module

This module demonstrates **proper** request cancellation in MCP servers using the protocol's built-in capabilities, rather than manual task tracking.

## Key Concepts

### MCP-Native Cancellation vs Manual Tracking

**❌ Wrong Approach (Manual):**
- Manually track tasks in dictionaries
- Implement custom cancellation logic
- Handle request IDs ourselves

**✅ Correct Approach (MCP-Native):**
- Use MCP's built-in `Context` for request management
- Rely on `asyncio.CancelledError` for cancellation
- Leverage MCP's session and request lifecycle

## How MCP Cancellation Works

1. **Request Context**: Each tool call gets a `Context` with unique `request_id`
2. **Asyncio Integration**: MCP uses asyncio's cancellation mechanism
3. **Automatic Cleanup**: MCP handles session and request lifecycle
4. **Progress Reporting**: Built-in `ctx.report_progress()` method

## Files

### `server.py`
Clean MCP server demonstrating proper cancellation patterns:
- Uses `Context` parameter injection
- Handles `asyncio.CancelledError` gracefully
- Reports progress via `ctx.report_progress()`
- Logs via `ctx.info()`, `ctx.warning()`, etc.

### `client.py` 
MCP protocol client for testing the server.

### `httpx_client.py`
Simple HTTP client for quick testing.

### `simple_demo.py`
Conceptual demo showing pure asyncio cancellation (no MCP).

## Tools Available

1. **`process_large_file`** - Long-running task with progress reporting
2. **`get_request_status`** - Check status of current request
3. **`quick_task`** - Fast task for testing
4. **`simulate_network_request`** - Network operation with timeout

## Running the Demo

### Terminal 1: Start Server
```bash
cd mcp_code
uv run server.py
```

### Terminal 2: Test with HTTP Client
```bash
# Quick test
uv run httpx_client.py quick

# Long-running task
uv run httpx_client.py process
```

### Terminal 3: Full MCP Client
```bash
uv run client.py
```

## Key Improvements Over Manual Tracking

### Before (Manual):
```python
# ❌ Manual task tracking
active_tasks: dict[str, asyncio.Task] = {}
task_results: dict[str, str] = {}

@server.tool()
async def my_tool(param: str) -> str:
    request_id = str(time.time())  # Manual ID
    current_task = asyncio.current_task()
    active_tasks[request_id] = current_task
    # ... manual cleanup
```

### After (MCP-Native):
```python
# ✅ MCP-native approach
@server.tool()
async def my_tool(param: str, ctx: Context = None) -> str:
    if ctx:
        request_id = ctx.request_id  # Automatic
        await ctx.info(f"Starting task {request_id}")
    
    try:
        await asyncio.sleep(5)  # Cancellation point
        return "Done"
    except asyncio.CancelledError:
        if ctx:
            await ctx.warning("Task was cancelled")
        raise  # Re-raise for proper handling
```

## Learning Objectives

1. **Understand MCP's built-in request lifecycle**
2. **Use Context injection properly**
3. **Handle asyncio cancellation gracefully**
4. **Leverage MCP's progress and logging features**
5. **Avoid reinventing protocol-level functionality**

## Why This Approach is Better

1. **Simpler Code**: No manual tracking dictionaries
2. **More Reliable**: Uses MCP's tested request management
3. **Better Integration**: Works seamlessly with MCP clients
4. **Proper Separation**: Application logic vs protocol concerns
5. **Future-Proof**: Aligns with MCP specification evolution

## Next Steps

- Explore MCP's other built-in features (resources, prompts)
- Learn about MCP session management
- Study the FastMCP server architecture
- Build production-ready cancellable tools
