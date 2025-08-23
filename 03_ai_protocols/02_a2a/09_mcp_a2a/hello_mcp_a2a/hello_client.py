import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, Client
from a2a.types import Message, TextPart

async def main():
    # Discover your calendar agent
    try:
        async with httpx.AsyncClient(timeout=300) as httpx_client:
            
            resolver = A2ACardResolver(base_url="http://localhost:8000/a2a/", httpx_client=httpx_client)
            agent_card = await resolver.get_agent_card()
            print(f"Found agent: {agent_card}")

            # Create A2A client with discovered agent cards
            client: Client = ClientFactory(config=ClientConfig(httpx_client=httpx_client, streaming=False)).create(card=agent_card)

            # Create message with proper structure
            message = Message(
                role="user",
                message_id="123",
                parts=[TextPart(text="What is current ETH Rate and shall I get them?")]
            )

            response = client.send_message(message)
            async for chunk in response:
                print("CHUNK", chunk)

    except Exception as e:
        print(f"Error fetching agent cards: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())