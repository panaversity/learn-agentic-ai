import asyncio
import json
import httpx
from typing import Dict, Any
from httpx_sse import EventSource, aconnect_sse

from mcp.types import JSONRPCMessage, JSONRPCRequest, JSONRPCNotification, ClientCapabilities, Implementation

class MCPCompliantHTTPXClient:
    """MCP-compliant httpx client that follows official protocol patterns"""
    
    def __init__(self, url: str):
        self.url = url
        self.session_id: str | None = None
        self.request_headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        self.get_stream_task = None
    
    def _update_headers_with_session(self, base_headers: dict[str, str]) -> dict[str, str]:
        """Update headers with session ID if available (from streamable_http.py)"""
        headers = base_headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers
    
    async def start_get_stream(self, client: httpx.AsyncClient):
        """Start GET stream for server-initiated messages (like progress notifications)"""
        if not self.session_id:
            return
            
        print("    🔄 Starting GET stream for server notifications...")
        
        try:
            headers = self._update_headers_with_session(self.request_headers)
            
            async with aconnect_sse(
                client,
                "GET",
                self.url,
                headers=headers,
                timeout=httpx.Timeout(30.0, read=300.0)
            ) as event_source:
                print("    ✅ GET stream established")
                
                async for sse in event_source.aiter_sse():
                    if sse.event == "message":
                        try:
                            parsed = json.loads(sse.data)
                            
                            # Handle progress notifications from GET stream
                            if parsed.get("method") == "notifications/progress":
                                params = parsed.get("params", {})
                                progress = params.get("progress", 0)
                                total = params.get("total")
                                message = params.get("message", "Working...")
                                
                                if total:
                                    percentage = (progress / total) * 100
                                    progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
                                    print(f"    📊 [{progress_bar}] {percentage:.1f}% - {message}")
                                else:
                                    print(f"    📊 Progress: {progress} - {message}")
                                    
                        except json.JSONDecodeError as e:
                            print(f"    ❌ GET stream JSON decode error: {e}")
                            
        except Exception as e:
            print(f"    ⚠️  GET stream error: {e}")
    
    async def initialize_mcp(self, client: httpx.AsyncClient) -> str:
        """Initialize MCP connection using official protocol structures"""
        print("🔌 Initializing MCP connection (MCP-compliant)...")
        
        # Use exact MCP protocol structures
        init_request = JSONRPCRequest(
            jsonrpc="2.0",
            id=1,
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": ClientCapabilities(
                    experimental={},
                    sampling=None,
                    roots=None
                ).model_dump(exclude_none=True),
                "clientInfo": Implementation(
                    name="mcp-compliant-httpx-client",
                    version="1.0.0"
                ).model_dump()
            }
        )
        
        # Create JSONRPCMessage wrapper
        message = JSONRPCMessage(init_request)
        
        headers = self.request_headers.copy()
        
        response = await client.post(
            self.url, 
            json=message.model_dump(by_alias=True, mode="json", exclude_none=True),
            headers=headers
        )
        response.raise_for_status()
        
        # Extract session ID from response headers
        self.session_id = response.headers.get("mcp-session-id")
        print(f"✅ Connected! Session ID: {self.session_id}")
        return self.session_id
    
    async def send_initialized(self, client: httpx.AsyncClient):
        """Send initialized notification and start GET stream (like official client)"""
        initialized_notification = JSONRPCNotification(
            jsonrpc="2.0",
            method="notifications/initialized",
            params={}
        )
        
        message = JSONRPCMessage(initialized_notification)
        headers = self._update_headers_with_session(self.request_headers)
        
        response = await client.post(
            self.url,
            json=message.model_dump(by_alias=True, mode="json", exclude_none=True),
            headers=headers
        )
        
        if response.status_code == 202:
            print("✅ Initialized notification sent")
            
            # Start GET stream after initialization (like official client does)
            self.get_stream_task = asyncio.create_task(self.start_get_stream(client))
    
    async def call_tool_with_progress(self, client: httpx.AsyncClient, 
                                    tool_name: str, arguments: Dict[str, Any]):
        """Call MCP tool using exact official protocol patterns"""
        
        request_id = 3
        
        # Use exact MCP protocol structure for tool calls
        tool_request = JSONRPCRequest(
            jsonrpc="2.0",
            id=request_id,
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments,
                "_meta": {
                    "progressToken": request_id  # This should trigger progress!
                }
            }
        )
        
        message = JSONRPCMessage(tool_request)
        headers = self._update_headers_with_session(self.request_headers)
        
        print(f"\n🛠️ Calling tool: {tool_name} (MCP-compliant with GET stream)")
        print("-" * 60)
        
        # Use the same streaming pattern as official MCP client
        async with client.stream(
            "POST", 
            self.url,
            json=message.model_dump(by_alias=True, mode="json", exclude_none=True),
            headers=headers
        ) as response:
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code}")
                return None
            
            content_type = response.headers.get("content-type", "").lower()
            
            if "text/event-stream" in content_type:
                print("    🌊 Receiving SSE stream from POST...")
                
                # Use httpx-sse EventSource (same as official MCP client)
                event_source = EventSource(response)
                message_count = 0
                final_result = None
                
                async for sse in event_source.aiter_sse():
                    message_count += 1
                    
                    if sse.event == "message":
                        try:
                            parsed = json.loads(sse.data)
                            
                            print(f"🔍 RAW SSE message: {parsed}")
                            
                            # # Handle progress notifications from POST stream
                            # if parsed.get("method") == "notifications/progress":
                            #     params = parsed.get("params", {})
                            #     progress_token = params.get("progressToken")
                            #     progress = params.get("progress", 0)
                            #     total = params.get("total")
                            #     message = params.get("message", "Working...")
                                
                            #     if progress_token == request_id:
                            #         if total:
                            #             percentage = (progress / total) * 100
                            #             progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
                            #             print(f"    📊 POST [{progress_bar}] {percentage:.1f}% - {message}")
                            #         else:
                            #             print(f"    📊 POST Progress: {progress} - {message}")
                            
                            # # Handle final result
                            # elif "result" in parsed:
                            #     final_result = parsed["result"]
                            #     print(f"    ✅ Tool completed")
                            #     break
                           
                        except json.JSONDecodeError as e:
                            print(f"    ❌ JSON decode error: {e}")
                
                print(f"    📈 POST stream messages: {message_count}")
                
                # Give GET stream a moment to show progress
                await asyncio.sleep(0.5)
                
                return final_result
            
            else:
                # Handle JSON response
                content = await response.aread()
                try:
                    data = json.loads(content)
                    return data.get("result")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    return None
    
    async def cleanup(self):
        """Clean up resources"""
        if self.get_stream_task:
            self.get_stream_task.cancel()
            try:
                await self.get_stream_task
            except asyncio.CancelledError:
                pass

async def main():
    """MCP-compliant httpx client demo with GET stream"""
    
    print("🚀 MCP-Compliant httpx Progress Demo (with GET stream)")
    print("=" * 70)
    
    url = "http://localhost:8000/mcp/"
    
    # Use official MCP HTTP client factory (same as official implementation)
    async with httpx.AsyncClient(
        headers=None,
        timeout=httpx.Timeout(30.0, read=300.0)
    ) as client:
        
        mcp_client = MCPCompliantHTTPXClient(url)
        
        try:
            # Follow exact MCP initialization sequence
            session_id = await mcp_client.initialize_mcp(client)
            if not session_id:
                print("❌ Failed to get session ID")
                return
            
            # Send initialized notification and start GET stream
            await mcp_client.send_initialized(client)
            
            # Give GET stream time to establish
            await asyncio.sleep(0.5)
            
            # Test scenarios with MCP-compliant requests
            scenarios = [
                {
                    "name": "📁 File Download (httpx + GET stream)",
                    "tool": "download_file",
                    "args": {"filename": "mcp-dataset.zip", "size_mb": 5}
                },
                {
                    "name": "🔄 Data Processing (httpx + GET stream)",
                    "tool": "process_data", 
                    "args": {"records": 20}
                }
            ]
            
            for scenario in scenarios:
                print(f"\n{scenario['name']}")
                
                result = await mcp_client.call_tool_with_progress(
                    client,
                    scenario["tool"], 
                    scenario["args"]
                )
                
                print("-" * 60)
                if result and "content" in result:
                    for content in result["content"]:
                        print(f"✅ Result: {content.get('text', 'No text content')}")
                else:
                    print("✅ Tool completed successfully")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await mcp_client.cleanup()
            
if __name__ == "__main__":
    asyncio.run(main()) 