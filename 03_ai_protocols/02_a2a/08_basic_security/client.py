import logging
import httpx

from typing import Any
from uuid import uuid4

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:8001/a2a'
    # API key issued out-of-band (for demo; obtain securely in production)
    API_KEY = "secure-api-key-123"

    async with httpx.AsyncClient(headers={"X-API-Key": API_KEY}) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        logger.info(
            f'Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}'
        )
        final_agent_card_to_use: AgentCard = await resolver.get_agent_card()
        logger.info('Successfully fetched public agent card')

        # Initialize A2AClient with API key in headers
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=final_agent_card_to_use,
        )
        logger.info('A2AClient initialized.')

        # Send initial query
        send_message_payload_multiturn: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {
                        'kind': 'text',
                        'text': 'How much is the exchange rate for 1 USD?',
                    }
                ],
                'message_id': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**send_message_payload_multiturn),
        )

        response = await client.send_message(request)
        print("\n\nFirst response:\n")
        print(response.model_dump(mode='json', exclude_none=True))
        print("\n\n")
        
        print("\n\n\n\n\n", response.root.result)

        context_id = response.root.result.context_id
        task_id = response.root.result.status.message.task_id

        # Send follow-up query
        second_send_message_payload_multiturn: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': 'USD to CAD'}],
                'message_id': uuid4().hex,
                'context_id': context_id,
                'task_id': task_id,
            },
        }

        second_request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**second_send_message_payload_multiturn),
        )

        second_response = await client.send_message(second_request)
        print("\n\nSecond response:\n")
        print(second_response.model_dump(mode='json', exclude_none=True))
        print("\n\n")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())