# MCP Prompt

MCP servers can also provide prompts that can be used to dynamically generate agent instructions. This allows you to create reusable instruction templates that can be customized with parameters.

MCP servers that support prompts provide two key methods:
- list_prompts(): Lists all available prompts on the server
- get_prompt(name, arguments): Gets a specific prompt with optional parameters

This example uses a local MCP prompt server in [server.py](server.py).

Run the example:

1. Start MCP Server

```bash
uv run python server.py
```

2. Start Agent
```bash
uv run python main.py
```

## Details

The step uses mcp prompt that provides user-controlled prompts that generate agent instructions. MCP server exposes prompts like `generate_code_review_instructions` that take parameters such as focus area and programming language. The agent calls these prompts to dynamically generate its system instructions based on user-provided parameters.

## Workflow

The example demonstrates two key functions:

1. **`show_available_prompts`** - Lists all available prompts on the MCP server, showing users what prompts they can select from. This demonstrates the discovery aspect of MCP prompts.

2. **`demo_code_review`** - Shows the complete user-controlled prompt workflow:
   - Calls `generate_code_review_instructions` with specific parameters (focus: "security vulnerabilities", language: "python")
   - Uses the generated instructions to create an Agent with specialized code review capabilities
   - Runs the agent against vulnerable sample code (command injection via `os.system`)
   - The agent analyzes the code and provides security-focused feedback using available tools

This pattern allows users to dynamically configure agent behavior through MCP prompts rather than hardcoded instructions. 