import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, RunResult
from agents.tool import FunctionTool
from mcp.types import Tool
from core.tools import ToolManager
from mcp_client import MCPClient

async def convert_to_sdk_tool(tools_schema: list[Tool], mcp_clients: dict[str, MCPClient]) -> list[FunctionTool]:
    converted_tools = []
    for tool in tools_schema:
            client = await ToolManager._find_client_with_tool(
                list(mcp_clients.values()), tool.name
            )
            if client:
                converted_tools.append(
                    FunctionTool(
                        name=tool.name,
                        description=tool.description or "",
                        params_json_schema=tool.inputSchema,
                        on_invoke_tool=ToolManager.execute_tool_dynamically(tool.name, client)
                    )
                )
            else:
                raise ValueError(f"No client found for tool: {tool.name}")
    
    return converted_tools


class AgentService:
    def __init__(self, model: str, api_key: str, base_url: str | None = None, clients=None):
        self.model = model
        self.api_key = api_key
        self.messages = []

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )

        self.agent = Agent(
            name="Assistant",
            instructions="You are a helpful AI assistant that can use tools to answer questions.",
            model=OpenAIChatCompletionsModel(
                model=model,
                openai_client=self.client
            ),
        )

    async def chat(
        self,
        query: str,
        system=None,
        mcp_clients: dict[str, MCPClient] = {},
    ) -> RunResult:
        if system:
            self.agent.instructions = system

        tools = await ToolManager.get_all_tools(mcp_clients)
        
        if tools:
            self.agent.tools = await convert_to_sdk_tool(tools, mcp_clients) or []  # type: ignore

        self.messages.append({"role": "user", "content": query})
        
        result = await Runner.run(
            self.agent,
            self.messages
        )
        
        self.messages = result.to_input_list()

        return result
