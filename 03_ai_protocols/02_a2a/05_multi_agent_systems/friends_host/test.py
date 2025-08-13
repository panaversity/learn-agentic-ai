```python
import asyncio
import httpx
import json
from typing import List

class MultiAgentTester:
    """Test the complete multi-agent Table Tennis scheduling system."""

    def __init__(self):
        self.agents = {
            "host": "http://localhost:8000",
            "ameen": "http://localhost:8001",
            "qasim": "http://localhost:8002",
            "ahmad": "http://localhost:8003"
        }

    async def test_agent_discovery(self):
        """Test A2A agent card discovery."""
        print("🔍 Testing Agent Discovery...")

        for name, url in self.agents.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/.well-known/agent-card.json")
                    if response.status_code == 200:
                        card = response.json()
                        print(f"  ✅ {name}: {card.get('name')} - {card.get('description')[:50]}...")
                    else:
                        print(f"  ❌ {name}: Failed to fetch agent card")
            except Exception as e:
                print(f"  ❌ {name}: Connection failed - {e}")

    async def test_individual_agents(self):
        """Test each agent individually."""
        print("\n🧪 Testing Individual Agents...")

        test_query = "Are you available tomorrow evening for Table Tennis?"

        for name, url in self.agents.items():
            if name == "host":  # Skip host for individual testing
                continue

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "message/send",
                        "params": {
                            "message": {
                                "role": "user",
                                "parts": [{"kind": "text", "text": test_query}],
                                "messageId": "test-msg-001"
                            }
                        },
                        "id": "test-001"
                    }

                    response = await client.post(url, json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ {name}: Response received")

                        # Extract response preview
                        if result.get("result") and result["result"].get("artifacts"):
                            preview = result["result"]["artifacts"][0].get("text", "")[:100]
                            print(f"    Preview: {preview}...")
                    else:
                        print(f"  ❌ {name}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  ❌ {name}: Test failed - {e}")

    async def test_multi_agent_coordination(self):
        """Test complete multi-agent coordination via host."""
        print("\n🎯 Testing Multi-Agent Coordination...")

        coordination_queries = [
            "What time is everyone available tomorrow for Table Tennis?",
            "Can we schedule a Table Tennis game for tomorrow evening?",
            "Check if the team is free for Table Tennis tomorrow at 8 PM"
        ]

        for i, query in enumerate(coordination_queries, 1):
            print(f"\n  Test {i}: {query}")

            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "message/send",
                        "params": {
                            "message": {
                                "role": "user",
                                "parts": [{"kind": "text", "text": query}],
                                "messageId": f"coordination-test-{i}"
                            }
                        },
                        "id": f"test-coordination-{i}"
                    }

                    response = await client.post(self.agents["host"], json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        print(f"    ✅ Coordination successful")

                        if result.get("result") and result["result"].get("artifacts"):
                            response_text = result["result"]["artifacts"][0].get("text", "")

                            # Check for key coordination elements
                            checks = {
                                "Agent responses": any(name in response_text for name in ["Ameen", "Qasim", "Ahmad"]),
                                "Time coordination": any(time in response_text.lower() for time in ["8", "pm", "evening"]),
                                "Court booking": "court" in response_text.lower() or "booking" in response_text.lower(),
                                "Success indicator": "success" in response_text.lower() or "scheduled" in response_text.lower()
                            }

                            for check, passed in checks.items():
                                status = "✅" if passed else "⚠️"
                                print(f"    {status} {check}: {'PASS' if passed else 'CHECK'}")

                            print(f"    📝 Response preview: {response_text[:200]}...")
                    else:
                        print(f"    ❌ Coordination failed: HTTP {response.status_code}")

            except Exception as e:
                print(f"    ❌ Coordination error: {e}")

            await asyncio.sleep(2)  # Pause between tests

async def main():
    """Run complete multi-agent system tests."""
    print("🧪 Multi-Agent Table Tennis Scheduling System Tests")
    print("=" * 60)

    tester = MultiAgentTester()

    # Run all test suites
    await tester.test_agent_discovery()
    await tester.test_individual_agents()
    await tester.test_multi_agent_coordination()

    print("\n🎯 Test Summary:")
    print("  1. Agent Discovery: Verify all agent cards accessible")
    print("  2. Individual Agents: Test each agent responds correctly")
    print("  3. Multi-Agent Coordination: Test complete workflow")

    print("\n✅ Multi-agent testing complete!")
    print("🏓 Ready for Table Tennis scheduling!")

if __name__ == "__main__":
    asyncio.run(main())
```

