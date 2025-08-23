import asyncio
import httpx
from a2a.client import A2ACardResolver

async def test_skills():
    base_url = 'http://localhost:8001'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()

        print(f"Agent Card:\n\n {agent_card}")

if __name__ == '__main__':
    asyncio.run(test_skills())