from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession, types
import asyncio
from contextlib import AsyncExitStack
from typing import Any
from pydantic import AnyUrl
import json

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
    
    async def list_tools(self) -> list[types.Tool]:
        assert self._sess, "Session not available."
        return (await self._sess.list_tools()).tools
    
    async def list_resouces(self) -> list[types.Resource]:
        assert self._sess, "Session not available."
        result:types.ListResourcesResult = await self._sess.list_resources()
        return result.resources

    async def list_resource_templates(self) -> list[types.ResourceTemplate]:
        assert self._sess, "Session not available."
        result: types.ListResourceTemplatesResult = await self._sess.list_resource_templates()
        # print("LIST RESOURCE TEMPLATES", result.__dict__)
        return result.resourceTemplates

    async def read_resources(self, uri: str) -> types.ReadResourceResult:
        assert self._sess, "Session not available."
        result = await self._sess.read_resource(AnyUrl(uri))
        # print("READ RECOURSES DICT", result.__dict__)
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                try:
                    return json.loads(resource.text)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
        return resource.text
        
async def main():
    async with MCPClient("http://localhost:8000/mcp") as client:
        # tools = await client.list_tools()
        # print(tools, " tools")
        
        # resources = await client.list_resouces()
        # print(resources[0].uri, " resources")

        # data = await client.read_resources(resources[0].uri)
        # print(data, " data")

        # for r in resources:
        #     data = await client.read_resources(r.uri)
        #     print(f"Resource URI: {r.uri}")
        #     print(f"Data: {data}")
        template = await client.list_resource_templates()
        intro_uri = template[0].uriTemplate.replace("{doc_name}", "intro")
        data = await client.read_resources(intro_uri)
        print("Intro Document:", data)


asyncio.run(main())