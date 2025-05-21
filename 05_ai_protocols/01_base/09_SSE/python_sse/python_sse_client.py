from dataclasses import dataclass
import httpx
import asyncio
import json
import time

DEFAULT_SSE_URL = "http://127.0.0.1:8001/sse_stream"
DEFAULT_POST_URL = "http://127.0.0.1:8001/send_message"

async def parse_sse_stream(response: httpx.Response):
    """Parse SSE stream into event dictionaries."""
    current_event = {}
    async for line in response.aiter_lines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(":"):
            yield {"event": "keep_alive", "data": None}
            continue
        if line.startswith("event:"):
            current_event["event"] = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data = json.loads(line[len("data:"):].strip())
            current_event["data"] = data
            yield current_event
            current_event = {}

@dataclass
class SSEClient:
    sse_url: str
    post_url: str
    session_id: str | None = None
    client: httpx.AsyncClient = None
    listening: bool = False

    @classmethod
    def create(cls, sse_url: str = DEFAULT_SSE_URL, post_url: str = DEFAULT_POST_URL) -> 'SSEClient':
        """Create an SSEClient with default or custom URLs and initialize HTTP client."""
        return cls(
            sse_url=sse_url,
            post_url=post_url,
            client=httpx.AsyncClient(timeout=None)
        )

    async def start(self):
        """Start listening to SSE stream."""
        self.listening = True
        try:
            async with self.client.stream("GET", self.sse_url) as response:
                response.raise_for_status()
                async for event in parse_sse_stream(response):
                    if not self.listening:
                        break
                    if event.get("event") == "connection_confirmation":
                        self.session_id = event["data"]["sessionId"]
                        print(f"Received SSE event: Connected, Session ID: {self.session_id}")
                    elif event.get("event") == "message_receipt":
                        print(f"Received SSE event: Server confirmed: {event['data']['confirmation']}")
                    elif event.get("event") == "ai_agent_message":
                        timestamp = time.strftime("%H:%M:%S", time.localtime(event['data']['timestamp']))
                        print(f"Received SSE event: AI Agent [{event['data']['agent_id']}]: {event['data']['message']} (Status: {event['data']['status']}, Time: {timestamp})")
                    elif event.get("event") == "keep_alive":
                        print("Received SSE keep-alive")
        except httpx.HTTPError as e:
            if not self.listening:
                print("SSE stream closed gracefully.")
            else:
                print(f"SSE connection error: {e}")
                self.listening = False

    async def send_message(self, message: str) -> bool:
        """Send message to server via POST."""
        if not self.session_id:
            print("No session ID. Connect first.")
            return False
        try:
            response = await self.client.post(
                f"{self.post_url}?session_id={self.session_id}&message={message}"
            )
            response.raise_for_status()
            print(f"Sent POST message: {response.json()['status']}")
            return True
        except httpx.HTTPError as e:
            print(f"Failed to send POST message: {e}")
            return False

    async def stop(self):
        """Stop listening and clean up."""
        self.listening = False
        await asyncio.sleep(0.1)  # Allow stream loop to exit
        await self.client.aclose()
        print("Client stopped.")

async def main():
    client = SSEClient.create()
    print("Starting SSE client...")
    task = asyncio.create_task(client.start())
    await asyncio.sleep(1)  # Wait for connection
    if client.session_id:
        await client.send_message("Hello, server!")
        await asyncio.sleep(10)  # Run longer to observe AI agent messages
    await client.stop()
    await task

if __name__ == "__main__":
    asyncio.run(main())