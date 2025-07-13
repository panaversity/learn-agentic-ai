import json
from mcp.types import CallToolResult, Tool
from mcp_client import MCPClient

from agents.tool_context import ToolContext

class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools = tool_models if tool_models else []
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> MCPClient | None:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None


    @classmethod
    def execute_tool_dynamically(cls, tool_name, mcp_client: MCPClient):
        """Execute a simulated database query."""
        async def execute_tool(ctx: ToolContext, args: str) -> CallToolResult:
            parsed_args = json.loads(args)
            result = await mcp_client.call_tool(tool_name, parsed_args)
            return result
        
        return execute_tool
