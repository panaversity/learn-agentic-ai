import asyncio
import logging
from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)

# Enable detailed logging for educational purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AClientDemo:
    """
    Comprehensive A2A Client demonstration.

    Shows the complete A2A client workflow:
    1. Agent Discovery via Agent Cards
    2. Client initialization 
    3. Non-streaming message sending
    4. Streaming message communication
    5. Error handling patterns
    """

    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.agent_card: AgentCard = None
        self.client: A2AClient = None

    async def discover_agent(self, httpx_client: httpx.AsyncClient) -> None:
        """
        Step 1: Agent Discovery

        Fetch the agent's capabilities and metadata via its Agent Card.
        This is the foundation of A2A communication - knowing what the agent can do.
        """
        logger.info("🔍 === AGENT DISCOVERY ===")

        # Initialize A2A Card Resolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=self.agent_url,
        )

        # Fetch Agent Card from /.well-known/agent.json
        card_url = f"{self.agent_url}/.well-known/agent.json"
        logger.info(f"Fetching Agent Card from: {card_url}")

        try:
            self.agent_card = await resolver.get_agent_card()
            logger.info(f"✅ Discovered Agent: {self.agent_card.name}")
            logger.info(f"📝 Description: {self.agent_card.description}")
            logger.info(f"🚀 Capabilities: {self.agent_card.capabilities}")
            logger.info(
                f"🎯 Skills: {[skill.name for skill in self.agent_card.skills]}")

            # Show detailed skill information
            if self.agent_card.skills:
                for skill in self.agent_card.skills:
                    logger.info(
                        f"   Skill '{skill.name}': {skill.description}")
                    logger.info(f"   Examples: {skill.examples}")

        except Exception as e:
            logger.error(f"❌ Agent discovery failed: {e}")
            raise

    async def setup_client(self, httpx_client: httpx.AsyncClient) -> None:
        """
        Step 2: Initialize A2A Client

        Create a client instance configured with the discovered agent card.
        """
        logger.info("🔧 === CLIENT SETUP ===")

        if not self.agent_card:
            raise ValueError("Must discover agent first!")

        self.client = A2AClient(
            httpx_client=httpx_client,
            agent_card=self.agent_card
        )
        logger.info("✅ A2A Client initialized and ready to communicate")

    async def send_message(self, message_text: str) -> dict:
        """
        Step 3a: Non-Streaming Message (message/send)

        Send a message and wait for the complete response.
        Best for: Quick queries, simple request-response patterns.
        """
        logger.info("📤 === NON-STREAMING MESSAGE ===")
        logger.info(f"Sending: '{message_text}'")

        # Create message payload with proper A2A format
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    # Using simplified format (no 'kind' needed)
                    {'text': message_text}
                ],
                'messageId': uuid4().hex,
            },
        }

        # Create JSON-RPC request
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )

        try:
            # Send message and wait for response
            response = await self.client.send_message(request)
            logger.info("✅ Received response")

            # Extract response text for display
            response_data = response.model_dump(mode='json', exclude_none=True)
            if 'result' in response_data and 'parts' in response_data['result']:
                for part in response_data['result']['parts']:
                    if 'text' in part:
                        print(f"🤖 Agent: {part['text']}")

            return response_data

        except Exception as e:
            logger.error(f"❌ Message sending failed: {e}")
            raise

    async def send_streaming_message(self, message_text: str) -> None:
        """
        Step 3b: Streaming Message (message/stream)

        Send a message and receive real-time streaming updates.
        Best for: Long responses, real-time interaction, progressive results.
        """
        logger.info("🌊 === STREAMING MESSAGE ===")
        logger.info(f"Streaming: '{message_text}'")

        # Create message payload (same format as non-streaming)
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'text': message_text}
                ],
                'messageId': uuid4().hex,
            },
        }

        # Create streaming request
        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )

        try:
            # Send streaming message
            stream_response = self.client.send_message_streaming(
                streaming_request)

            logger.info("✅ Streaming started, processing chunks...")
            print("🌊 Streaming Response:")

            # Process streaming chunks in real-time
            chunk_count = 0
            full_response = ""

            async for chunk in stream_response:
                chunk_count += 1
                chunk_data = chunk.model_dump(mode='json', exclude_none=True)

                # Extract text from chunk if available
                if 'result' in chunk_data and 'parts' in chunk_data['result']:
                    for part in chunk_data['result']['parts']:
                        if 'text' in part:
                            text = part['text']
                            full_response += text
                            print(f"Chunk #{chunk_count}: {text}")

                # Brief pause to see streaming effect
                await asyncio.sleep(0.1)

            logger.info(
                f"✅ Streaming completed. Received {chunk_count} chunks")
            print(f"📄 Full Response: {full_response}")

        except Exception as e:
            logger.error(f"❌ Streaming failed: {e}")
            raise


async def main():
    """
    Main demo function showing complete A2A client workflow.

    This demonstrates the full lifecycle of A2A client communication:
    1. Discovery -> 2. Setup -> 3. Communication -> 4. Error handling
    """
    agent_url = 'http://localhost:8000'

    print("🚀 A2A Client Demo Starting...")
    print("📋 Make sure the agent server is running:")
    print("   cd 05_a2a_client && uv run agent_card.py")
    print()

    async with httpx.AsyncClient() as httpx_client:
        demo = A2AClientDemo(agent_url)

        try:
            # Step 1: Discover the agent
            await demo.discover_agent(httpx_client)
            print()

            # Step 2: Setup client
            await demo.setup_client(httpx_client)
            print()

            # Step 3a: Non-streaming messages
            print("=" * 50)
            await demo.send_message("Hello there!")
            await asyncio.sleep(1)

            await demo.send_message("How are you doing?")
            await asyncio.sleep(1)

            await demo.send_message("Tell me about yourself")
            await asyncio.sleep(1)

            # Step 3b: Streaming messages
            print("\n" + "=" * 50)
            await demo.send_streaming_message("Say goodbye in a friendly way")

            print("\n🎉 A2A Client demo completed successfully!")
            print("🔗 You've mastered the complete A2A client-server communication flow!")

        except httpx.ConnectError:
            print("\n❌ Connection failed!")
            print("🔧 Make sure the agent server is running:")
            print("   cd 05_a2a_client && uv run agent_card.py")

        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            logger.error(f"Full error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
