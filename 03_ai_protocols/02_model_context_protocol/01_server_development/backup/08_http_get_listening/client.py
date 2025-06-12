import httpx
import json
import asyncio

SERVER_URL = "http://localhost:8000/mcp/"

async def listen_for_events():
    """
    Connects to the server with a GET request and waits for server-sent events.
    This function will run indefinitely until the server sends a message or it's cancelled.
    """
    print("[Listener]: Connecting to server to listen for events...")
    headers = {"Accept": "text/event-stream"}
    try:
        # We use a long timeout because we expect this connection to be open for a while
        async with httpx.AsyncClient(timeout=None) as client:
            # client.stream opens a connection and lets us read from it over time
            async with client.stream("GET", SERVER_URL, headers=headers) as response:
                print("[Listener]: ==> Connection established! Waiting for notifications...")
                # We loop over the response line by line as data arrives
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = json.loads(line[6:])
                        print("\n[Listener]: <<<=== Received a notification from the server!")
                        print(json.dumps(data, indent=2))
                        # For this demo, we'll exit after receiving one message.
                        break
    except httpx.ConnectError:
        print("\n[Listener]: ERROR - Could not connect to the server. Is it running?")
    except Exception as e:
        print(f"\n[Listener]: An error occurred: {e}")

async def trigger_event():
    """Calls a tool on the server via a POST request to make it send a notification."""
    print("[Trigger]:  Will call 'send_notification' tool in 3 seconds to trigger an event...")
    await asyncio.sleep(3) # Wait a few seconds to make the demo clearer
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "send_notification", "arguments": {"message": "Hello listeners, from the trigger!"}},
        "id": "trigger-1"
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SERVER_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print("[Trigger]:  ===> Event triggered successfully on the server!")
            else:
                print(f"[Trigger]:  ERROR - Server responded with {response.status_code}")
    except httpx.ConnectError:
        print("[Trigger]:  ERROR - Could not connect to the server.")


async def main():
    """
    Coordinates the listener and the trigger to demonstrate the full event loop.
    """
    print("--- HTTP GET / Server-Sent Events Demonstration ---")
    
    # asyncio.gather lets us run both our listener and our trigger concurrently.
    await asyncio.gather(
        listen_for_events(),
        trigger_event()
    )
    
    print("\n--- Demonstration complete ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient shut down.") 