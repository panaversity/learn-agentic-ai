# Shared MCP Server

For examples in module `07_openai_agents_sdk_integration`, we will use a shared, standalone MCP server. This server is designed to be simple and provide a consistent target for our agent examples.

- **Location:** `05_ai_protocols/01_mcp/07_openai_agents_sdk_integration/shared_mcp_server/server_main.py`
- **To Run:**
  1.  Open a new terminal.
  2.  Navigate to the `shared_mcp_server` directory:
  ```bash
  cd 05_ai_protocols/01_mcp/07_openai_agents_sdk_integration/shared_mcp_server/
  ```
  3.  Execute the server script (using `uv run`):
      ```bash
      uv run python server.py
      ```
- **Server Details:**
  - It runs on `http://localhost:8001`.
  - Its MCP protocol endpoint is at `/mcp`. So, the full URL for clients is `http://localhost:8001/mcp`.
  - It exposes a tool named `greet_from_shared_server`.
  - It will log incoming requests to its console.
