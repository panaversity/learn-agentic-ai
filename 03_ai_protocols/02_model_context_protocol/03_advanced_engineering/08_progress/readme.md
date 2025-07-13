# 📊 08: MCP Progress Notifications

> **Analogy:** Imagine ordering a pizza. A bad service just tells you "Order received" and you wait anxiously. A great service gives you real-time updates: "Making dough," "Adding toppings," "In the oven," "Out for delivery!" You feel informed and confident. MCP Progress Notifications do the same for long-running digital tasks.

This lesson shows you how to turn a silent, long-running operation into a transparent, real-time experience using MCP's progress notification system.

## 🎯 What You Will Learn

-   **Server-Side**: How to send `notifications/progress` from a tool to report on its status.
-   **Client-Side**: How to receive those notifications and display them to a user (e.g., as a progress bar).
-   **Protocol-Level**: How `progressToken` is used in a request's `_meta` field to link a tool call to its stream of progress updates.
-   **Interactive Testing**: How to see the raw progress events stream back in real-time using Postman.

---

## ▶️ How to Run This Example

You can explore this example in two ways: using the simple Python client or interacting directly with the server via the Postman collection.

### 1. Start the Server

First, open a terminal in the `02_server_engineering/08_progress/mcp_code` directory and run:

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn server:mcp_app --reload
```

The server is now running and listening on `http://localhost:8000`.

### 2. Choose Your Client

#### A) Run the Python Client

In a **new terminal**, run the Python client:

```bash
# (In the same mcp_code directory)
uv run client.py
```

**What to Expect:**
You will see the client connect, list the tools, and then run two scenarios. For each scenario, a real-time progress bar will appear and update until the task is complete.

```
📁 File Download
----------------------------------------
    📊 [████████████░░░░░░░░] 60.0% - Downloading dataset.zip... 60.0%
    📊 [████████████████░░░░] 80.0% - Downloading dataset.zip... 80.0%
    ...
```

#### B) Use the Postman Collection

This is a great way to see the raw protocol messages.

1.  **Import**: Import the `postman/MCP_Progress_Notifications.postman_collection.json` file into Postman.
2.  **Run in Order**:
    -   `1. Connection Lifecycle` -> `Initialize Connection`: Establishes the session.
    -   `1. Connection Lifecycle` -> `Send Initialized Notification`: Tells the server you're ready.
    -   `2. Long-Running Tools` -> `Call 'download_file' with Progress`: This is the key request!

**What to Expect:**
When you send the `download_file` request, the response will be a `text/event-stream`. Postman will show you the `notifications/progress` JSON objects arriving one by one, followed by the final `result`.

---

## 🧠 Key Concepts

### Server: Reporting Progress (`server.py`)

The server's tool uses the `ctx` (Context) object provided by `FastMCP` to easily report progress without worrying about tokens.

```python
@mcp.tool()
async def download_file(filename: str, size_mb: int, ctx: Context) -> str:
    # ... setup ...
    for chunk in range(total_chunks + 1):
        # The magic is here! Just report progress on the context.
        await ctx.report_progress(
            progress=chunk,
            total=total_chunks,
            message=f"Downloading {filename}..."
        )
        await asyncio.sleep(0.1)
    return "Download complete"
```

### Client: Handling Progress (`client.py`)

The high-level `ClientSession` makes handling progress trivial. You just pass a callback function. The library handles the token and notification routing for you.

```python
async def progress_handler(progress: float, total: float | None, message: str | None):
    # ... logic to draw a progress bar ...
    print(f"📊 [{progress_bar}] {percentage:.1f}% - {message}")

# The magic is here! Just pass the handler to the call.
result = await session.call_tool(
    "download_file",
    {"filename": "dataset.zip", "size_mb": 5},
    progress_callback=progress_handler
)
```

### Protocol: The `progressToken`

Under the hood, the client and server are exchanging a `progressToken`. The client sends it in the `_meta` field of its request, telling the server "I want progress updates for this specific job."

Here is what the Postman collection sends, which is what the Python client does automatically:

```json
{
    "jsonrpc": "2.0",
    "id": 101,
    "method": "tools/call",
    "params": {
        "name": "download_file",
        "arguments": { "...": "..." },
        "_meta": {
            "progressToken": 101 // Link this call to progress updates
        }
    }
}
```

The server then sends back notifications tagged with the same token.

```json
{
    "jsonrpc": "2.0",
    "method": "notifications/progress",
    "params": {
        "progressToken": 101, // This update is for request #101
        "progress": 5,
        "total": 10,
        "message": "Downloading..."
    }
}
```

---

## 💡 Try It Yourself

1.  **Change the Speed**: In `server.py`, modify the `asyncio.sleep()` duration in the tools. How does this affect the user experience?
2.  **Unknown Total**: Modify the `process_data` tool to *not* provide a `total` in `ctx.report_progress`. How does the Python client's `progress_handler` behave?
3.  **Add a New Tool**: Create a new tool in `server.py` that simulates a multi-step installation process with different messages but no percentage. Update `client.py` to call it.