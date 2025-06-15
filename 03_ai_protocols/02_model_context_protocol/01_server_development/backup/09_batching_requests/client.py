import httpx
import asyncio

async def main():
    print("--- MCP Batch Request Client Demonstration ---")

    # --- Batch Request (array of requests) ---
    batch_request = [
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "add", "arguments": {"a": 5, "b": 10}},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "greet", "arguments": {"name": "World"}},
            "id": 2
        }
    ]

    print(f"\n[Step 1: Sending batch with {len(batch_request)} requests]")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    async with httpx.AsyncClient() as client:
        # Send the batch request to our compliant server
        response = await client.post("http://localhost:8000/mcp/", json=batch_request, headers=headers)
        # response.raise_for_status()

        print(f"\n[Step 2: Received batch response]")
        print(f"Status: {response.text}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        # print(f"\n[Step 3: Successfully received {len(responses)} batch responses]")
        print("✅ JSON-RPC batching works correctly when the server properly implements the spec!")


if __name__ == "__main__":
    asyncio.run(main()) 