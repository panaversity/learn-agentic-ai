import asyncio
import httpx
import json


async def test_calendar_agent():
    """Simple test of calendar agent discovery."""

    # Test 1: Can we discover the agent?
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/.well-known/agent-card.json")
            agent_card = response.json()

            print("✅ Agent Discovery Successful!")
            print(f"   Agent Name: {agent_card['name']}")
            print(f"   Available Skills: {len(agent_card['skills'])}")

            for skill in agent_card['skills']:
                print(f"     • {skill['name']}: {skill['description']}")

        except Exception as e:
            print(f"❌ Agent Discovery Failed: {e}")
            print("💡 Make sure the calendar agent is running!")

if __name__ == "__main__":
    asyncio.run(test_calendar_agent())
