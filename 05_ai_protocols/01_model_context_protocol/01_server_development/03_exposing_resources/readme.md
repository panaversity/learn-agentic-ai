# MCP Server

We will use [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk) for developing MCP Servers.

    uv init server

    uv add "mcp[cli]"

added server.py dummy server by copying from here:

https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#quickstart

Test it with the MCP Inspector:

    mcp dev server.py

    MCP Inspector is up and running at http://localhost:5173 

Open the url in browser: http://localhost:5173

Select Resource Template and list and run the resource.

Install [Claude Desktop](https://claude.ai/download)

You can install this weather server in Claude Desktop and interact with it right away by running: 

    mcp install server.py





