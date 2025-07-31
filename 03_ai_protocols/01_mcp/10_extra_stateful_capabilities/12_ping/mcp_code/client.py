import asyncio
import httpx
import json
import time

SERVER_URL = "http://localhost:8000/mcp/"


async def main():
    """Initializes an MCP session and sends a single ping request."""
    print("MCP Ping Client Example")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Initialize session
        print("\n🚀 Initializing MCP session...")
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "clientInfo": {"name": "simple-ping-client", "version": "1.0.0"},
                "capabilities": {},
            },
            "id": 1,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        try:
            response = await client.post(SERVER_URL, json=init_payload, headers=headers)
            response.raise_for_status()

            session_id = response.headers.get("mcp-session-id")
            if not session_id:
                print("❌ Error: Mcp-Session-Id header not found in response.")
                return

            # The response body for initialize can be an SSE stream
            init_response_text = response.text
            if "data: " in init_response_text:
                data_line = init_response_text.split("data: ")[1]
                init_result = json.loads(data_line)
                print(
                    f"✅ Session initialized. Server info: {init_result.get('result', {}).get('serverInfo')}"
                )
            else:
                print("✅ Session initialized (no data in response).")

            print(f"   Session ID: {session_id}")

        except httpx.RequestError as e:
            print(f"❌ Initialization failed: {e}")
            return

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": session_id,
            "MCP-Protocol-Version": "2025-06-18",
        }

        # 2. Send 'initialized' notification
        initialized_payload = {"jsonrpc": "2.0",
                               "method": "notifications/initialized"}
        response = await client.post(SERVER_URL, json=initialized_payload, headers=headers)
        if response.status_code == 202:
            print("✅ Sent 'initialized' notification.")
        else:
            print(
                f"⚠️ 'initialized' notification returned status {response.status_code}")

        await asyncio.sleep(0.1)  # Give server a moment to process

        # 3. Send Ping
        print("\n🏓 Sending ping...")
        ping_id = "ping-1"
        ping_payload = {"jsonrpc": "2.0", "id": ping_id, "method": "ping"}

        start_time = time.time()
        try:
            response = await client.post(SERVER_URL, json=ping_payload, headers=headers)
            response.raise_for_status()

            end_time = time.time()
            rtt_ms = (end_time - start_time) * 1000

            # The ping response can also be an SSE stream or plain JSON
            pong_data_text = response.text
            if "data: " in pong_data_text:
                data_line = pong_data_text.split("data: ")[1]
                pong_result = json.loads(data_line)
            else:
                pong_result = response.json()

            print(f"✅ Pong received in {rtt_ms:.2f} ms")
            print(f"   Response: {json.dumps(pong_result)}")

            if pong_result.get("id") != ping_id or "result" not in pong_result:
                print("❌ Invalid pong response format.")

        except httpx.RequestError as e:
            print(f"❌ Ping failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
