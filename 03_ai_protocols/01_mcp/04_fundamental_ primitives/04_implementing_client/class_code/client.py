from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession, types
import asyncio
from contextlib import AsyncExitStack

class MCPClient:
    def __init__(self, url):
        self.url = url
        self.stack = AsyncExitStack()
        self._sess = None
        
    async def __aenter__(self):
        read, write, _ = await self.stack.enter_async_context(
            streamablehttp_client(self.url)
        )
        self._sess = await self.stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._sess.initialize()
        return self
        
    async def __aexit__(self, *args):
        await self.stack.aclose()
    
    async def list_tools(self) -> types.Tool:
        return (await self._sess.list_tools()).tools
    
    async def call_tool(self, tool_name, *args, **kwargs):
        return await self._sess.call_tool(tool_name, *args, **kwargs)
    
    async def resources(self):
        return await self._sess.resources()
async def main():
    async with MCPClient("http://localhost:8000/mcp") as client:
        tools = await client.list_tools()
        print(tools, " tools")
        # for tool in tools:
        #     print(tool)
asyncio.run(main())