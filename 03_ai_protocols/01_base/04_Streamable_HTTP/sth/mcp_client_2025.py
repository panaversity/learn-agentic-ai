from dataclasses import dataclass
import httpx
import asyncio
import json
import uuid

MCP_SERVER_URL = "http://127.0.0.1:8002/mcp"

@dataclass
class MCPClient:
    base_url: str
    client: httpx.AsyncClient | None = None
    listening: bool = False

    @classmethod
    def create(cls, base_url: str = MCP_SERVER_URL):
        """Create an MCP client with an HTTP client."""
        return cls(base_url=base_url, client=httpx.AsyncClient(timeout=None))

    async def parse_chunked_stream(self, response: httpx.Response, label: str):
        """Parse chunked stream into JSON-RPC messages."""
        buffer = ""
        async for chunk in response.aiter_text():
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:
                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError:
                        print(f"Client: Invalid JSON in chunk: {line}")
                        continue

    async def start(self):
        """Start listening to GET chunked stream with reconnection."""
        self.listening = True
        retries = 0
        max_retries = 3
        while retries < max_retries and self.listening:
            try:
                headers = {"Accept": "application/json"}
                async with self.client.stream("GET", self.base_url, headers=headers) as response:
                    response.raise_for_status()
                    async for message in self.parse_chunked_stream(response, "GET"):
                        if not self.listening:
                            break
                        print(f"Client: GET Message: {json.dumps(message)}")
                    retries = 0
            except httpx.HTTPError as e:
                if not self.listening:
                    print("Client: Stream closed gracefully")
                    break
                print(f"Client: GET error: {e}")
                retries += 1
                if retries < max_retries:
                    await asyncio.sleep(2 ** retries)
                else:
                    print("Client: Max retries reached")
                    self.listening = False

    async def initialize(self):
        """Initialize MCP connection."""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"clientCapabilities": ["basic"]},
            "id": request_id
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            if response.headers.get("content-type") == "application/json":
                data = response.json()
                if data.get("id") == request_id and "result" in data:
                    print("Client: Initialized")
                    return True
            print("Client: Initialization failed")
            return False
        except httpx.HTTPError as e:
            print(f"Client: Initialization error: {e}")
            return False

    async def send_request(self, method: str, params: dict | None = None):
        """Send a JSON-RPC request."""
        request_id = str(uuid.uuid4())
        payload = {"jsonrpc": "2.0", "method": method, "id": request_id}
        if params:
            payload["params"] = params
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            if method == "start_streaming":
                async with self.client.stream("POST", self.base_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for message in self.parse_chunked_stream(response, f"POST_{request_id}"):
                        print(f"Client: POST Message: {json.dumps(message)}")
                        if message.get("id") == request_id and "result" in message:
                            return message["result"]
                    print("Client: No result received from stream")
                    return None
            else:
                response = await self.client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                print(f"Client: JSON Response: {json.dumps(data)}")
                return data.get("result")
        except httpx.HTTPError as e:
            print(f"Client: Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Client: JSON decode error: {e}")
            return None

    async def send_notification(self, method: str, params: dict | None = None):
        """Send a JSON-RPC notification."""
        payload = {"jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            if response.status_code == 202:
                print(f"Client: Notification {method} accepted")
                return True
            print(f"Client: Notification error: {response.status_code}")
            return False
        except httpx.HTTPError as e:
            print(f"Client: Notification error: {e}")
            return False

    async def close(self):
        """Close the client."""
        self.listening = False
        await self.client.aclose()
        print("Client: Closed")

async def main():
    client = MCPClient.create()
    if not await client.initialize():
        print("Failed to initialize")
        return
    task = asyncio.create_task(client.start())
    await asyncio.sleep(1)
    await client.send_request("echo", {"message": "Hello"})
    await client.send_request("start_streaming", {"details": "Stream data"})
    await client.send_notification("update", {"status": "active"})
    await asyncio.sleep(5)
    await client.close()
    await task

if __name__ == "__main__":
    asyncio.run(main())