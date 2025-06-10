import httpx
import json
import asyncio

class SimpleMCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp/"
    
    def _parse_sse_response(self, response_text: str):
        """Parse Server-Sent Events response to extract JSON data"""
        for line in response_text.strip().split('\n'):
            if line.startswith('data: '):
                json_part = line[6:]  # Remove 'data: ' prefix
                return json.loads(json_part)
        return {"error": "No data found in response"}
    
    async def _make_request(self, method: str, params: dict = None, request_id: str = "1"):
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.mcp_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return self._parse_sse_response(response.text)
    
    async def list_tools(self):
        """List all available tools"""
        return await self._make_request("tools/list", {}, "list_tools")
    
    async def call_tool(self, tool_name: str, arguments: dict = None):
        """Call a specific tool with arguments"""
        params = {
            "name": tool_name,
            "arguments": arguments or {}
        }
        return await self._make_request("tools/call", params, f"call_{tool_name}")
    
    async def list_resources(self):
        """List all available resources"""
        return await self._make_request("resources/list", {}, "list_resources")
    
    async def list_prompts(self):
        """List all available prompts"""
        return await self._make_request("prompts/list", {}, "list_prompts")

# Convenience functions for simple usage
async def mcp_list_tools(server_url: str = "http://localhost:8000"):
    """Quick function to list tools from an MCP server"""
    client = SimpleMCPClient(server_url)
    return await client.list_tools()

async def mcp_call_tool(tool_name: str, arguments: dict = None, server_url: str = "http://localhost:8000"):
    """Quick function to call a tool on an MCP server"""
    client = SimpleMCPClient(server_url)
    return await client.call_tool(tool_name, arguments)

# Example usage and testing
async def main():
    client = SimpleMCPClient()
    
    print("🔍 Hello MCP World!")
    print("=" * 50)
    
    # List available tools
    print("\n📋 Available Tools:")
    tools_response = await client.list_tools()
    
    if 'result' in tools_response and 'tools' in tools_response['result']:
        tools = tools_response['result']['tools']
        for tool in tools:
            print(f"  • {tool['name']}: {tool.get('description', 'No description')}")
    else:
        print(f"  Error: {tools_response}")
        return
    
    # Call the weather tool
    print("\n🌤️  Weather Forecast:")
    cities = ["Paris", "Tokyo", "New York"]
    
    for city in cities:
        forecast = await client.call_tool("get_forecast", {"city": city})
        
        if 'result' in forecast and 'content' in forecast['result']:
            weather_text = forecast['result']['content'][0]['text']
            print(f"  • {city}: {weather_text}")
        else:
            print(f"  • {city}: Error - {forecast}")

# Simple standalone functions for one-off usage
async def quick_example():
    """Example of using the convenience functions"""
    print("\n🚀 Quick Example:")
    
    # List tools using convenience function
    tools = await mcp_list_tools()
    print(f"Tools found: {len(tools.get('result', {}).get('tools', []))}")
    
    # Call tool using convenience function
    result = await mcp_call_tool("get_forecast", {"city": "London"})
    if 'result' in result:
        weather = result['result']['content'][0]['text']
        print(f"London weather: {weather}")

if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Run the quick example
    asyncio.run(quick_example())