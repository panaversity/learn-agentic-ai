import httpx
import json

async def main():
    # Method 1: Direct A2A endpoint (JSON-RPC 2.0)
    async with httpx.AsyncClient() as client:
        discovery_response = await client.get("http://localhost:8000/.well-known/agent-card.json")
        agent_card = discovery_response.json()
        print("\n\nAgent Card:\n\n", json.dumps(agent_card, indent=2), "\n\n")

        response = await client.post("http://localhost:8000", json={
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    'messageId': '123', 
                    'metadata': None, 
                    'parts': [{'kind': 'text', 'metadata': None, 'text': 'Schedule a team meeting for tomorrow at 2 PM'}], 
                    'referenceTaskIds': None, 
                    'role': 'user', 
                    'taskId': None
                    }
            },
            "id": "req-123"
        })
        result = response.json()
        print("\n\nRES\n\n", result)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())