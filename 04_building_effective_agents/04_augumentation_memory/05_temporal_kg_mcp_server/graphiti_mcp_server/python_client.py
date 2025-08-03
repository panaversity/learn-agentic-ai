import httpx
import asyncio
import json
import time

BASE_URL = "http://localhost:8000"

async def _make_request(tool_name: str, arguments: dict) -> dict:
    """Make a request to the MCP server"""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    headers = {"Accept": "application/json,text/event-stream"}
    
    time.sleep(5) # delay to avoid hitting llm rate limits
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
        for line in response.iter_lines():
            if line.startswith("data: "):
                line = line[6:]
                print(f"   <- Received data: {line[:100]}...")  # Print first 100 chars
                return json.loads(line)

async def ingest_data():
    
    print("=== Adding Episodes to Memory ===")
    
    # Add cloud expert information
    response1 = await _make_request("add_memory", {
        "name": "Cloud Expert Profile",
        "episode_body": "Sir Ameen Alam is a renowned cloud architect and AWS expert. He specializes in serverless technologies and has written extensively about cloud-native development. He prefers Azure for enterprise solutions.",
        "source": "text",
        "source_description": "expert introduction",
        "group_id": "default"
    })
    print("Added Ameen Alam episode:", json.dumps(response1, indent=2))

    # Add structured expert data
    expert_data = {
        "expert": {
            "name": "Ahmad Hassan",
            "title": "Senior Solutions Architect",
            "company": "Google Cloud",
            "specialties": ["AI/ML", "BigQuery", "GCP Architecture"]
        },
        "achievements": [
            {"type": "certification", "name": "Google Cloud Professional Architect", "year": 2023},
        ]
    }

    response2 = await _make_request("add_memory", {
        "name": "Expert Directory",
        "episode_body": json.dumps(expert_data),
        "source": "json",
        "source_description": "expert database",
        "group_id": "default"
    })
    print("Added Ahmad Hassan episode:", json.dumps(response2, indent=2))
    
    print("\n=== Searching for Facts ===")
    
async def search_data():
    """Demonstrate how to use the Graphiti MCP server"""
    # Search for cloud preferences
    facts1 = await _make_request("search_memory_facts", {
        "query": "Find top Cloud and database Experts",
        "max_facts": 5
    })
    print("Cloud Experts preferences:", json.dumps(facts1, indent=2))

    print("\n=== Searching for Nodes ===")
    
    # Find everything about specific experts
    nodes1 = await _make_request("search_memory_nodes", {
        "query": "Sir Ameen Alam",
        "max_nodes": 3
    })
    print("Ameen Alam profile:", json.dumps(nodes1, indent=2))
    

if __name__ == "__main__":
    asyncio.run(ingest_data())
    
    time.sleep(30)  # Ensure data is ingested before searching
    asyncio.run(search_data())

