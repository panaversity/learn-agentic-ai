import httpx
import json
import asyncio
from typing import Optional

class SessionAwareClient:
    """
    A stateful MCP client that handles session management automatically.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.mcp_endpoint = f"{base_url}/mcp/"
        self.session_id: Optional[str] = None
        self.http_client = httpx.AsyncClient()

    async def _request(self, method: str, params: dict = None):
        """Constructs and sends a JSON-RPC request, handling the session ID."""
        
        # --- Session Logic ---
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            # If we have a session ID, we must include it in the header.
            headers["Mcp-Session-Id"] = self.session_id
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            print(f"   -> Sending '{method}' request...")
            if self.session_id:
                print(f"      (Using Session ID: {self.session_id[:8]}...)")
            else:
                print("      (No Session ID yet)")

            response = await self.http_client.post(self.mcp_endpoint, json=payload, headers=headers)
            response.raise_for_status()

            # --- Session Logic ---
            # After the request, we check the response headers for a session ID.
            # The server will always send one back.
            received_id = response.headers.get("mcp-session-id")
            if received_id and self.session_id != received_id:
                print(f"   -> Received new Session ID: {received_id[:8]}...")
                self.session_id = received_id
            
            # The server sends back SSE, so we parse it to get the JSON data
            for line in response.text.strip().split('\n'):
                if line.startswith('data: '):
                    return json.loads(line[6:])
            return {"error": "No data found in SSE response"}

        except Exception as e:
            print(f"   -> An error occurred: {e}")
            return {"error": str(e)}

    async def call_tool(self, name: str, arguments: dict = None):
        """A helper to make a 'tools/call' request."""
        return await self._request("tools/call", {"name": name, "arguments": arguments or {}})

async def main():
    """A step-by-step demonstration of a session-aware client."""
    print("--- MCP Session Management Client Demonstration ---")
    
    # We create one client instance and reuse it for all requests.
    # This allows it to remember the session ID.
    client = SessionAwareClient()

    print("\n[Step 1: First tool call]")
    print("We call 'increment_counter'. The client has no session ID yet.")
    response1 = await client.call_tool("increment_counter")
    result1 = response1.get('result', {}).get('content', [{}])[0].get('text')
    print(f"   -> Success! The server returned counter: {result1}")
    
    print("\n[Step 2: Second tool call]")
    print("We call the same tool again. Now the client will send the session ID it just received.")
    response2 = await client.call_tool("increment_counter")
    result2 = response2.get('result', {}).get('content', [{}])[0].get('text')
    print(f"   -> Success! The server returned counter: {result2}")
    
    print("\n[Step 3: Third tool call]")
    print("Let's do it one more time to be sure.")
    response3 = await client.call_tool("increment_counter")
    result3 = response3.get('result', {}).get('content', [{}])[0].get('text')
    print(f"   -> Success! The server returned counter: {result3}")

    print("\n--- Demonstration Complete ---")
    print("Notice how the server remembered our counter and increased it from 1 to 3.")
    print("This is only possible because the client and server are both using the Session ID.")

if __name__ == "__main__":
    asyncio.run(main()) 