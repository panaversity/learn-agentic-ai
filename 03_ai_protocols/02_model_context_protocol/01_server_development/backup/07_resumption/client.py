import httpx
import json
import asyncio


async def test_mcp_step_by_step():
    """Test MCP requests one by one to isolate the issue."""
    
    print("🔧 MCP Debug Session")
    print("=" * 40)
    
    base_url = "http://localhost:8000/mcp/"
    
    # Initialize headers that will be shared across all requests
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"  # FastMCP requires BOTH formats
    }
    
    # Create a single client instance for all requests
    async with httpx.AsyncClient(timeout=10) as client:
        
        # Step 1: Test initialization
        print("1. Testing initialization...")
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "debug-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        print(f"   📤 Sending init headers: {headers}")
        print(f"   📤 Sending init message: {json.dumps(init_message, indent=2)[:200]}...")
        
        try:
            response = await client.post(base_url, json=init_message, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   📥 Response headers: {dict(response.headers)}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code != 200:
                print("   ❌ Initialization failed!")
                return
            else:
                print("   ✅ Initialization succeeded!")
                
                # Extract session ID for subsequent requests
                session_id = None
                
                # First, try to get session ID from response headers (server-provided)
                session_id = response.headers.get("mcp-session-id")
                
                if session_id:
                    print(f"   📋 Extracted Session ID: {session_id}")
                    # Add session ID to headers for all subsequent requests
                    headers["MCP-Session-ID"] = session_id
                else:
                    print("   ⚠️ No session ID found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        print()
        
        # Step 2: Test tools/list with different variations
        print("2. Testing tools/list...")
        
        # Variation 1: With empty params
        tools_message_v1 = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print(f"   📤 Full headers being sent: {headers}")
        print(f"   📤 Message being sent: {json.dumps(tools_message_v1, indent=2)}")
            
        try:
            response = await client.post(base_url, json=tools_message_v1, headers=headers)
            print(f"     Status: {response.status_code}")
            print(f"     📥 Response headers: {dict(response.headers)}")
            
            print(f"     Response: {response.text}...")
                    
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
        
        # Step 3: Test tools/call with different variations  
        print("3. Testing tools/call...")
        
        # Variation 1: Current structure
        call_message_v1 = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_forecast",
                "arguments": {
                    "city": "TestCity"
                }
            },
            "id": 4
        }

        
        try:
            response = await client.post(base_url, json=call_message_v1, headers=headers)
            print(f"     Status: {response.status_code}")
            print(f"     📥 Response headers: {dict(response.headers)}")
            
            print(f"     Response: {response.text}...")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        print()
        print("🎯 Debug complete!")


if __name__ == "__main__":
    asyncio.run(test_mcp_step_by_step()) 