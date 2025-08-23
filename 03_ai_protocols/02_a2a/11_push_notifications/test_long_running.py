import asyncio
import httpx
from uuid import uuid4
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, Client
from a2a.types import Message, TextPart, PushNotificationConfig


async def main():
    # Set up HTTP client
    async with httpx.AsyncClient(timeout=2) as httpx_client:
        # Discover the agent card
        resolver = A2ACardResolver(
            base_url="http://localhost:8001", httpx_client=httpx_client)
        agent_card = await resolver.get_agent_card()
        print(f"Found agent: {agent_card}")

        # Create A2A client
        client: Client = ClientFactory(
            config=ClientConfig(httpx_client=httpx_client, streaming=True,
                                push_notification_configs=[
                                    PushNotificationConfig(
                                        url="http://localhost:9000/webhook"
                                    )
                                ]
                                )
        ).create(card=agent_card)

        # Create message
        message = Message(
            role="user",
            message_id=str(uuid4()),
            parts=[TextPart(text="Run a long processing task")]
        )

        # Send message with push notification config
        print("📡 Sending message with push notification config...")
        response = client.send_message(
            message
        )

        # Stream the response
        chunk_count = 0
        async for chunk in response:
            chunk_count += 1
            print(f"\n[CHUNK {chunk_count}]", chunk)
            # Optionally disconnect after a few chunks to simulate client disconnect
            if chunk_count >= 1:
                print(
                    "\n🔌 Simulating disconnect. Task will continue and webhook will notify on completion.")
                break

if __name__ == "__main__":
    asyncio.run(main())
