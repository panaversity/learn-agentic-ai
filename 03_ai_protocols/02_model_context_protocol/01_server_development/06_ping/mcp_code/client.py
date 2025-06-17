import asyncio
import httpx
import json
import time
import sys
from typing import Optional, Dict, Any

class MCPPingClient:
    """MCP Client focused on ping utility testing and health monitoring."""
    
    def __init__(self, server_url: str = "http://localhost:8000/mcp/"):
        self.server_url = server_url
        self.session_id: Optional[str] = None
        
    async def initialize_mcp(self, client: httpx.AsyncClient) -> bool:
        """Initialize MCP connection and wait for completion."""
        print("🚀 [Step 1: Initialize MCP Connection]")
        
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "clientInfo": {
                    "name": "ping-test-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "experimental": {},
                    "sampling": {}
                }
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            # Send initialize request
            response = await client.post(self.server_url, json=init_payload, headers=headers)
            response.raise_for_status()
            
            # Get session ID
            self.session_id = response.headers.get("mcp-session-id")
            print(f"   ✅ MCP initialized successfully")
            if self.session_id:
                print(f"   📝 Session ID: {self.session_id}")
            
            # Send initialized notification and wait a moment
            await self.send_initialized(client)
            
            # Wait a bit to ensure initialization is complete
            await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ MCP initialization failed: {e}")
            return False
    
    async def send_initialized(self, client: httpx.AsyncClient):
        """Send initialized notification."""
        initialized_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"  # Must accept both
        }
        
        # Add session ID if available
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        try:
            response = await client.post(self.server_url, json=initialized_payload, headers=headers)
            if response.status_code == 202:
                print("   ✅ Initialized notification sent")
            else:
                print(f"   ⚠️  Initialized notification status: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Initialized notification failed: {e}")

    async def send_ping(self, client: httpx.AsyncClient, ping_id: str = None, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Send a ping request according to MCP specification.
        
        Args:
            client: HTTP client
            ping_id: Unique ID for the ping request
            timeout: Request timeout in seconds
            
        Returns:
            Dict with ping result and timing information
        """
        if not ping_id:
            ping_id = f"ping_{int(time.time() * 1000)}"
            
        # Create ping request according to specification
        ping_request = {
            "jsonrpc": "2.0",
            "id": ping_id,
            "method": "ping"
            # Note: No params object - per specification
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Add session ID if available
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        start_time = time.time()
        
        try:
            response = await client.post(
                self.server_url, 
                json=ping_request, 
                headers=headers,
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                # Parse response
                content_type = response.headers.get("content-type", "")
                if content_type.startswith("text/event-stream"):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = json.loads(line[6:])
                            break
                else:
                    data = response.json()
                
                # Check for errors first
                if "error" in data:
                    return {
                        "success": False,
                        "error": f"Server error: {data['error']['message']}",
                        "response_time_ms": response_time
                    }
                
                # Validate successful response according to specification
                if (data.get("jsonrpc") == "2.0" and 
                    data.get("id") == ping_id and 
                    "result" in data):
                    
                    return {
                        "success": True,
                        "response_time_ms": response_time,
                        "response": data,
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format",
                        "response": data,
                        "response_time_ms": response_time
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time_ms": response_time
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "response_time_ms": timeout * 1000
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }

    async def test_basic_ping(self, client: httpx.AsyncClient):
        """Test basic ping functionality."""
        print("\n🏓 [Test 1: Basic Ping Request/Response]")
        print("   Testing basic ping according to MCP specification...")
        
        result = await self.send_ping(client, "basic_test_1")
        print(f"   -> [RESPONSE]: {result}\n")
            
        return result["success"]

async def main():
    """Main function with test selection."""
     
    client = MCPPingClient()
    async with httpx.AsyncClient() as http_client:
        # Initialize MCP connection
        if not await client.initialize_mcp(http_client):
            print("❌ Failed to initialize MCP connection")
            sys.exit(1)
        
        # Run selected tests
        try:
            await client.test_basic_ping(http_client)
          
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
    
    print("\n🎉 MCP Ping testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 