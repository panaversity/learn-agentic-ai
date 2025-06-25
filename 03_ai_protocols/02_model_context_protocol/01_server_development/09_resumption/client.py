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
        self.client: Optional[httpx.AsyncClient] = None
        
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
        """Step 1: Initialize MCP connection (using persistent client)"""
        print("🚀 Step 1: Initializing MCP connection...")
        
        # Create persistent HTTP client for the entire session
        if not self.client:
            self.client = httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=300.0))
        
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
            response = await self.client.post(self.base_url, json=init_message, headers=headers)
            
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
            response = await self.client.post(self.base_url, json=notification, headers=self.headers)
            
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
        """Step 2: Call a tool using client.stream() (might fail due to server timeout)"""
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
            # Use longer timeout to capture at least one event from tool call stream
            # Even if the tool doesn't complete, we need the stream event ID for resumption
            temp_timeout = max(timeout, 3)  # At least 3 seconds to get stream started
            old_timeout = self.client._timeout
            self.client._timeout = httpx.Timeout(temp_timeout)
            
            # Use client.stream() like the official MCP client
            async with self.client.stream(
                "POST",
                self.base_url,
                json=call_message,
                headers=self.headers
            ) as response:
                
                # Restore original timeout
                self.client._timeout = old_timeout
                
                if response.status_code != 200:
                    print(f"❌ Tool call failed: {response.status_code}")
                    return "ERROR"
                
                print(f"🔧 Tool call response headers: {dict(response.headers)}")
                
                # Check if we have SSE stream
                content_type = response.headers.get("content-type", "").lower()
                if "text/event-stream" in content_type:
                    print("🌊 Tool call returned SSE stream")
                    # CRITICAL: Wait for at least the first event to capture the stream event ID
                    from httpx_sse import EventSource
                    event_source = EventSource(response)
                    
                    # Try to get at least one event for the correct stream event ID
                    event_received = False
                    async for sse in event_source.aiter_sse():
                        print(f"🔧 Tool call SSE event: '{sse.event}', id: '{sse.id}', data: '{sse.data[:100]}...'")
                        
                        # Track event ID for resumption - THIS IS CRITICAL
                        if sse.id:
                            self.last_event_id = sse.id
                            print(f"🔧 ✅ Captured TOOL CALL Event ID: {sse.id}")
                            event_received = True
                        
                        # For demonstration, timeout after capturing the event ID
                        if event_received and timeout <= 5:
                            print("🔧 ⏰ Simulating timeout after capturing event ID for resumption demo")
                            break
                    
                    if not event_received:
                        print("🔧 ⚠️ No events received from tool call stream - resumption may not work")
                
                return "TIMEOUT_DEMO"
                
        except Exception as e:
            # Restore original timeout in case of error
            self.client._timeout = old_timeout
            print(f"💥 Tool call error: {e}")
            print(f"🔧 Last Event ID before error: {self.last_event_id}")
            return "ERROR"

    async def resume_get_stream(self) -> Optional[str]:
        """Use HTTP GET with Last-Event-ID for TRUE MCP resumption (no new calls)"""
        print(f"🔄 Starting TRUE MCP resumption via GET with Last-Event-ID...")
        
        headers = self.headers.copy()
        if self.last_event_id:
            headers["Last-Event-ID"] = self.last_event_id
            print(f"   → Using Last-Event-ID: {self.last_event_id}")
            print(f"   → MCP Spec: GET request should replay events, NOT make new calls")
        
        try:
            print(f"   → GET {self.base_url} (TRUE resumption)")
            
            # Use HTTP GET with ONLY Last-Event-ID header (MCP spec compliant)
            # NO JSON body - server should replay events from event store
            async with self.client.stream(
                "GET",
                self.base_url,
                headers=headers
            ) as response:
                
                print(f"   → Response status: {response.status_code}")
                print(f"   → Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    print(f"❌ GET resumption failed: {response.status_code}")
                    return None
                
                content_type = response.headers.get("content-type", "").lower()
                
                if "text/event-stream" in content_type:
                    print("✅ GET SSE stream established for resumption")
                    
                    # Use EventSource like the official client
                    from httpx_sse import EventSource
                    event_source = EventSource(response)
                    
                    # Add timeout to prevent hanging
                    result_found = False
                    timeout_seconds = 10
                    
                    async def wait_for_result():
                        nonlocal result_found
                        async for sse in event_source.aiter_sse():
                            print(f"   → Received SSE event: '{sse.event}', id: '{sse.id}', data: '{sse.data[:100]}...'")
                            
                            if sse.event == "message":
                                try:
                                    parsed = json.loads(sse.data)
                                    print(f"   → Parsed SSE data: {parsed}")
                                    
                                    # Track event ID
                                    if sse.id:
                                        self.last_event_id = sse.id
                                        print(f"   → Updated Event ID: {sse.id}")
                                    
                                    # Handle result from resumption
                                    if "result" in parsed:
                                        print("✅ Got result from resumption!")
                                        result_found = True
                                        return json.dumps(parsed)
                                        
                                    # Handle other message types
                                    elif parsed.get("method"):
                                        print(f"   → Method: {parsed.get('method')}")
                                        
                                except json.JSONDecodeError as e:
                                    print(f"❌ SSE JSON decode error: {e}")
                            
                            # Handle other event types
                            elif sse.event:
                                print(f"   → Non-message event: {sse.event}")
                        
                        return None
                    
                    # Wait for result with timeout
                    try:
                        result = await asyncio.wait_for(wait_for_result(), timeout=timeout_seconds)
                        if result:
                            return result
                    except asyncio.TimeoutError:
                        print(f"⏰ SSE stream timed out after {timeout_seconds} seconds")
                    
                    if not result_found:
                        print("⚠️ SSE stream ended without receiving result")
                    return None
                
                else:
                    # Handle JSON response
                    print("✅ GET stream with JSON response")
                    content = await response.aread()
                    response_text = content.decode('utf-8')
                    print(f"   → Response text: {response_text[:200]}...")
                    
                    # Track any new event ID
                    event_id = self.extract_event_id_from_sse(response_text)
                    if event_id:
                        self.last_event_id = event_id
                    
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(response_text)
                        if "result" in parsed:
                            print("✅ Got JSON result from resumption!")
                            return response_text
                    except json.JSONDecodeError:
                        pass
                    
                    # Try to parse SSE data
                    data = self.parse_sse_data(response_text)
                    if data and 'result' in data:
                        print("✅ Got SSE result from resumption!")
                        return response_text
                    
                    # Return the raw response
                    print("✅ Got raw response from resumption!")
                    return response_text
                
        except Exception as e:
            print(f"💥 GET stream resumption error: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    async def resume_and_retry(self, tool_name: str, arguments: dict) -> Optional[dict]:
        """Step 3: TRUE MCP RESUMPTION - Replay events, don't make new calls"""
        print(f"\n🔄 RESUMING connection for {tool_name} (MCP spec compliant)...")
        
        # Save current state
        saved_event_id = self.last_event_id
        saved_session_id = self.session_id
        
        print(f"   → Saved Event ID: {saved_event_id}")
        print(f"   → Saved Session ID: {saved_session_id}")
        print(f"   → MCP Spec: GET with Last-Event-ID should replay cached events")
        
        if saved_event_id:
            print(f"🔄 Resuming from Event ID: {saved_event_id}")
        else:
            print("❌ No Event ID to resume from")
            return None
        
        # Use HTTP GET with Last-Event-ID to replay events (MCP spec)
        result = await self.resume_get_stream()
        return result

    async def cleanup(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            print("🧹 HTTP client closed")

async def main():
    """
    Demo TWO approaches to MCP resumption:
    1. PRACTICAL: POST + Last-Event-ID (works with current server)
    2. SPEC-COMPLIANT: GET + Last-Event-ID (requires complete MCP implementation)
    """
    client = SimpleMCPClient()
    
    try:
        # Step 1: Initialize
        print("🚀 Step 1: Initializing MCP connection...")
        await client.initialize()
        
        print("🚀 Step 2: Sending initialized notification...")
        await client.send_initialized_notification()
        
        # Step 2: Tool call that will timeout
        print("\n" + "=" * 60)
        print("      MCP RESUMPTION DEMO")
        print("=" * 60)
        
        # Test the tool call to capture its stream event ID
        print("🔧 Testing get_forecast tool to capture event ID...")
        result = await client.call_tool("get_forecast", {"city": "Tokyo"}, timeout=5)  # Longer timeout to capture event
        print("🚀 Tool call result: ", result)
        print(f"🔧 Event ID from tool call: {client.last_event_id}")
        
        # Wait for server to complete task
        print("⏰ Waiting 7 seconds for server to complete the 6-second tool execution...")
        await asyncio.sleep(7)
        
        # Approach 1: SPEC-COMPLIANT (GET + Last-Event-ID)
        print("\n" + "-" * 60)
        print("APPROACH 1: MCP SPEC-COMPLIANT (GET + Last-Event-ID)")
        print("-" * 60)
        spec_result = await client.resume_and_retry("get_forecast", {"city": "Tokyo"})
        print("🚀 Spec-compliant result: ", spec_result)
        

    
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())