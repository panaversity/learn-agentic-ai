import httpx
import json
import asyncio
from typing import Optional

class SimpleMCPClient:
    """MCP client focused on demonstrating resumption clearly."""
    
    def __init__(self, base_url: str = "http://localhost:8000/mcp/"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.last_event_id: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
    def extract_event_id_from_sse(self, sse_response: str) -> Optional[str]:
        """Extract event ID from SSE response for resumption tracking."""
        lines = sse_response.split('\n')
        
        # Look for explicit 'id: ' line in SSE format
        for line in lines:
            if line.startswith('id: '):
                event_id = line[4:].strip()
                print(f"📋 Found Event ID: {event_id}")
                return event_id

        return None
    
    def parse_sse_data(self, sse_response: str) -> Optional[dict]:
        """Parse data from SSE response."""
        for line in sse_response.split('\n'):
            if line.startswith('data: '):
                try:
                    return json.loads(line[6:])  # Remove 'data: ' prefix
                except json.JSONDecodeError as e:
                    print(f"Failed to parse SSE data: {e}")
                    return None
        return None
    
    async def initialize(self) -> bool:
        """Step 1: Initialize MCP connection (P1 - just get it working)"""
        print("🚀 Step 1: Initializing MCP connection...")
        
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize", 
            "params": {
                "protocolVersion": "2025-03-26",
                "clientInfo": {
                    "name": "simple-resumption-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "experimental": {},
                    "sampling": {}
                }
            },
            "id": 1
        }
        
        headers = self.headers.copy()
        
        # If resuming, add Last-Event-ID header
        if self.last_event_id:
            headers["Last-Event-ID"] = self.last_event_id
            print(f"🔄 Resuming from Event ID: {self.last_event_id}")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self.base_url, json=init_message, headers=headers)
                
                if response.status_code != 200:
                    print(f"❌ Initialize failed: {response.status_code}")
                    return False
                
                # Extract session ID
                self.session_id = response.headers.get("mcp-session-id")
                if self.session_id:
                    self.headers["mcp-session-id"] = self.session_id
                    print(f"✅ Session ID: {self.session_id}")
                
                # Track event ID for resumption
                event_id = self.extract_event_id_from_sse(response.text)
                if event_id:
                    self.last_event_id = event_id
                
                # Parse initialization result
                data = self.parse_sse_data(response.text)
                if data and 'result' in data:
                    print("✅ MCP initialized successfully!")
                    return True
                else:
                    print("❌ No result in initialization response")
                    return False
                    
        except Exception as e:
            print(f"❌ Initialize error: {e}")
            return False
    
    async def send_initialized_notification(self) -> bool:
        """Send the initialized notification to complete handshake"""
        print("📡 Sending initialized notification...")
        
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self.base_url, json=notification, headers=self.headers)
                
                if response.status_code in [200, 202]:
                    print("✅ Initialized notification sent")
                    return True
                else:
                    print(f"⚠️ Unexpected status: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Notification error: {e}")
            return False

    async def call_tool(self, tool_name: str, arguments: dict, timeout: int = 1) -> Optional[dict]:
        """Step 2: Call a tool (might fail due to server timeout)"""
        print(f"🔧 Calling tool: {tool_name} (timeout: {timeout}s)")
            
        call_message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 2
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.base_url, json=call_message, headers=self.headers)
                
                if response.status_code == 200:
                    # Track event ID for resumption
                    event_id = self.extract_event_id_from_sse(response.text)
                    if event_id:
                        self.last_event_id = event_id
                return response.text
                    
        except Exception as e:
            print(f"💥 Tool call error: {e}")
            return "ERROR"

    async def resume_and_retry(self, tool_name: str, arguments: dict) -> Optional[dict]:
        """Step 3: THE CORE CONCEPT - Resume connection and retry the tool call"""
        print(f"\n🔄 RESUMING connection and retrying {tool_name}...")
        
        # Save current state
        saved_event_id = self.last_event_id
        saved_session_id = self.session_id
        
        print(f"   → Saved Event ID: {saved_event_id}")
        print(f"   → Saved Session ID: {saved_session_id}")
        
        # Retry the tool call with longer timeout
        result = await self.call_tool(tool_name, arguments, timeout=10)
        return result        

async def main():
    """
    Demo the core resumption flow:
    1. Initialize once (P1 - just get it working)
    2. Call tool → Fails → Resume → Try again (THE MAIN POINT!)
    """
    client = SimpleMCPClient()
    
    # Step 1: Initialize (P1 - just get it working)
    print("🚀 Step 1: Initializing MCP connection...")
    await client.initialize()
    
    print("🚀 Step 2: Sending initialized notification...")
    await client.send_initialized_notification()
    
    # Step 2: THE MAIN POINT - Call tool that might break
    print("\n      RESUMPTION DEMO STARTS HERE")
    
    # Try to call a tool (the resume server has intentional 4s delay to cause timeout)
    result = await client.call_tool("get_forecast", {"city": "Tokyo"})
    
    print("🚀 Step 2 Result: ", result)
    
        
    # Step 3: Resume and retry - THIS IS THE CORE CONCEPT
    resumed_result = await client.resume_and_retry("get_forecast", {"city": "Tokyo"})
    print("🚀 Step 3 Result: ", resumed_result)
    
    print(f"\n" + "=" * 60)
    print("RESUMPTION CONCEPT SUMMARY:")
    print("1. ✅ Initialize once (don't repeat unnecessarily)")
    print("2. 🔧 Call tool → If breaks → Resume → Try again")
    print("3. 💡 Key insight: Resume preserves progress/state")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())