import httpx
import json
import asyncio
from typing import Optional

class ResilientClient:
    """
    A stateful client that handles session IDs and can resume a broken stream.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.mcp_endpoint = f"{base_url}/mcp/"
        self.session_id: Optional[str] = None
        self.last_event_id: Optional[str] = None
        self.http_client = httpx.AsyncClient()

    async def _get_session_id(self):
        """Ensures we have a session ID from the server before proceeding."""
        if self.session_id:
            return
        
        print("[Client]: No session ID found. Sending initial request to get one.")
        # We can use any valid MCP call to establish a session. 'tools/list' is harmless.
        await self._request("tools/list")
        if self.session_id:
            print(f"[Client]: Session established. ID: {self.session_id[:8]}...")
        else:
            raise ConnectionError("Could not establish a session with the server.")

    async def listen_with_simulated_disconnect(self):
        """Connects, listens for a few events, then simulates a disconnect and reconnects."""
        
        # --- First Connection ---
        print("\n[Phase 1: Initial Connection]")
        connect_headers = {"Accept": "text/event-stream", "Mcp-Session-Id": self.session_id}
        
        try:
            messages_received = 0
            async with self.http_client.stream("GET", self.mcp_endpoint, headers=connect_headers, timeout=5) as response:
                print("[Client]:   Listener connected. Waiting for messages...")
                async for line in response.aiter_lines():
                    if line.startswith("id:"):
                        self.last_event_id = line[4:]
                        print(f"[Client]:   Received message with ID: {self.last_event_id}")
                    elif line.startswith("data:"):
                        messages_received += 1
                        if messages_received >= 2:
                            print("[Client]:   Simulating disconnect after receiving 2 messages.")
                            break # Exiting the loop simulates the client disconnecting
            
        except httpx.TimeoutException:
            print("[Client]:   Connection timed out, which is expected if no messages arrived.")
        except Exception as e:
            print(f"[Client]:   An error occurred during initial connection: {e}")

        print(f"\n[Client]: Disconnected. Last event ID received was: {self.last_event_id}")
        await asyncio.sleep(1)

        # --- Second Connection (Resuming) ---
        print("\n[Phase 2: Reconnecting with Resumption]")
        resume_headers = {"Accept": "text/event-stream", "Mcp-Session-Id": self.session_id}
        if self.last_event_id:
            resume_headers["Last-Event-ID"] = self.last_event_id
            print(f"[Client]:   Sending 'Last-Event-ID: {self.last_event_id}' header.")
        
        try:
            async with self.http_client.stream("GET", self.mcp_endpoint, headers=resume_headers, timeout=5) as response:
                print("[Client]:   Resumed connection. Waiting for remaining messages...")
                async for line in response.aiter_lines():
                    if line.startswith("id:"):
                        self.last_event_id = line[4:]
                        print(f"[Client]:   Received resumed message with ID: {self.last_event_id}")
        except httpx.TimeoutException:
             print("[Client]:   Connection timed out. All messages likely received.")
        except Exception as e:
            print(f"[Client]:   An error occurred during resumption: {e}")
            
    async def _request(self, method: str, params: dict = None):
        """A standard request helper that also manages session ID."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": "req-1"}
        
        response = await self.http_client.post(self.mcp_endpoint, json=payload, headers=headers)
        received_id = response.headers.get("mcp-session-id")
        if received_id:
            self.session_id = received_id
        
        # We don't need the body for this example, just the session ID.
        return {}


async def main():
    """Demonstrates the full stream resumption flow."""
    print("--- MCP Stream Resumption Client Demonstration ---")
    client = ResilientClient()

    # 1. Establish a session so the server knows who we are.
    await client._get_session_id()

    # 2. In parallel, start listening AND trigger the message burst.
    # This ensures the listener is ready when the messages arrive.
    print("\n[Client]: Starting listener and triggering message burst simultaneously.")
    await asyncio.gather(
        client.listen_with_simulated_disconnect(),
        client._request("tools/call", {"name": "send_burst"})
    )

    print("\n--- Demonstration Complete ---")
    print("Notice how the client received all messages, even after disconnecting and reconnecting.")

if __name__ == "__main__":
    asyncio.run(main()) 