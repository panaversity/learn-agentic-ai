# MCP Server

readme.md (Detailed explanation of @mcp.tool(), using async def, leveraging docstrings for schemas and descriptions, and importantly, Tool Annotations like read-only/read-write as per recent spec changes.)

weather_example/ (Your current weather/ example, perhaps updated to showcase tool annotations.)

We will use [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk) for developing MCP Servers.

    uv init weather

    uv add "mcp[cli]"

added weather.py dummy server

Test it with the MCP Inspector:

    mcp dev weather.py

    MCP Inspector is up and running at http://localhost:5173 

Open the url in browser: http://localhost:5173

Select Tools Tab and list and run the tool.

Install [Claude Desktop](https://claude.ai/download)

You can install this weather server in Claude Desktop and interact with it right away by running: 

    mcp install weather.py


If you are a Mac user facing the error to integrate MCP with Claude desktop, then the chat below will help you.
[ChatGPT 03](https://chatgpt.com/share/67c64692-9374-8007-bedc-ca1cde76c95e)
