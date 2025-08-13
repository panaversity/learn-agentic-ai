#!/usr/bin/env python3
"""
Simple CLI client to interact with the Table Tennis Coordinator A2A server.
"""

import asyncio
import httpx
import json
from datetime import datetime

async def send_message(message: str, server_url: str = "http://localhost:8000"):
    """Send a message to the coordinator agent."""
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": f"cli-{datetime.now().timestamp()}"
            }
        },
        "id": f"cli-request-{datetime.now().timestamp()}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(server_url, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the response text from artifacts
                if "result" in result and "artifacts" in result["result"]:
                    artifacts = result["result"]["artifacts"]
                    if artifacts and len(artifacts) > 0:
                        # Get the first artifact's parts
                        first_artifact = artifacts[0]
                        if "parts" in first_artifact:
                            parts = first_artifact["parts"]
                            if parts and len(parts) > 0:
                                first_part = parts[0]
                                if "text" in first_part:
                                    return first_part["text"]
                        return f"Unexpected artifact structure: {json.dumps(first_artifact, indent=2)}"
                    else:
                        return "No artifacts found in response"
                else:
                    return f"Unexpected response structure: {json.dumps(result, indent=2)}"
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Connection error: {str(e)}"

async def main():
    print("🏓 Table Tennis Coordinator CLI")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 🏓")
                break
                
            if not user_input:
                continue
                
            print("Coordinator: Thinking...")
            response = await send_message(user_input)
            print(f"Coordinator: {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 🏓")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())