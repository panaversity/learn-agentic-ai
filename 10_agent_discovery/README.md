# Step 09: Agent Discovery 🔍

**Learning Objective**: Implement agent discovery mechanisms using the official A2A Python SDK to enable dynamic agent ecosystem formation and capability-based collaboration.

## 📚 Official A2A Reference

**Primary Documentation**: [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)  
**Agent Discovery Guide**: [A2A Agent Discovery](https://google-a2a.github.io/A2A/topics/agent-discovery/)  
**Card Resolver API**: [A2ACardResolver Reference](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.client.A2ACardResolver)

## 🎯 What You'll Learn

- Using `A2ACardResolver` for agent discovery
- Agent Card discovery via `.well-known/agent-card.json`
- Dynamic capability discovery and matching using SDK
- Client creation from discovered agent cards
- Health monitoring with A2A SDK
- Registry patterns using official SDK components

## 🏗️ Project Structure

```
09_agent_discovery/
├── README.md
├── pyproject.toml
├── src/
│   ├── discovery_service.py      # A2A SDK-based discovery
│   ├── agent_registry.py         # Registry using A2ACardResolver
│   ├── capability_matcher.py     # SDK-based capability matching
│   └── discovery_client.py       # A2A discovery client
├── agents/
│   ├── math_agent.py            # Math agent with A2A SDK
│   ├── language_agent.py        # Language agent with A2A SDK
│   └── utility_agent.py         # Utility agent with A2A SDK
├── tests/
│   ├── test_discovery.py
│   └── test_sdk_features.py
└── examples/
    ├── basic_discovery.py
    └── advanced_discovery.py
```

## 🚀 Quick Start

### 1. Initialize Project

```bash
cd 09_agent_discovery
uv init discovery_code
cd discovery_code
uv add a2a fastapi uvicorn httpx
```

### 2. Start Discovery Service and Agents

```bash
# Terminal 1: Start the A2A discovery service
uv run python src/discovery_service.py

# Terminal 2: Start sample agents
uv run python agents/math_agent.py
uv run python agents/language_agent.py

# Terminal 3: Test discovery
uv run python examples/basic_discovery.py
```

### 3. Test A2A SDK Discovery

```bash
# Test direct agent card resolution
curl http://localhost:8000/.well-known/agent-card.json

# Test discovery service
curl http://localhost:8080/discover

# Test capability matching
uv run python examples/advanced_discovery.py
```

## 📋 Core Implementation

### Discovery Service with A2A SDK (discovery_service.py)

```python
from a2a.client import A2ACardResolver, A2AClient
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title="A2A SDK Discovery Service")

class A2ADiscoveryService:
    def __init__(self):
        self.resolver = A2ACardResolver()
        self.registered_agents: Dict[str, Dict] = {}
        self.last_verified: Dict[str, datetime] = {}

    async def register_agent_url(self, agent_url: str) -> Optional[Dict]:
        """Register an agent using A2A Card Resolver"""
        try:
            # Use SDK to resolve agent card
            agent_card = await self.resolver.get_agent_card(agent_url)

            if agent_card:
                agent_id = agent_card.name.replace(" ", "_").lower()

                self.registered_agents[agent_id] = {
                    "id": agent_id,
                    "url": agent_url,
                    "card": agent_card.dict(),
                    "registered_at": datetime.now(),
                    "verified": True
                }
                self.last_verified[agent_id] = datetime.now()

                logging.info(f"Successfully registered agent: {agent_card.name}")
                return self.registered_agents[agent_id]

        except Exception as e:
            logging.error(f"Failed to register agent at {agent_url}: {e}")

        return None

    async def discover_agents_by_skill(self, skill_id: str) -> List[Dict]:
        """Discover agents that provide a specific skill"""
        matching_agents = []

        for agent_data in self.registered_agents.values():
            agent_card = agent_data.get("card", {})
            skills = agent_card.get("skills", [])

            for skill in skills:
                if skill.get("id") == skill_id or skill.get("name") == skill_id:
                    matching_agents.append(agent_data)
                    break

        return matching_agents

    async def discover_agents_by_capability(self, capability: str) -> List[Dict]:
        """Discover agents with specific capabilities"""
        matching_agents = []

        for agent_data in self.registered_agents.values():
            agent_card = agent_data.get("card", {})
            capabilities = agent_card.get("capabilities", {})

            # Check if capability is enabled
            if capabilities.get(capability, False):
                matching_agents.append(agent_data)

        return matching_agents

    async def verify_all_agents(self):
        """Verify all registered agents using A2A Card Resolver"""
        for agent_id, agent_data in list(self.registered_agents.items()):
            agent_url = agent_data.get("url")

            try:
                # Re-resolve agent card to verify it's still available
                agent_card = await self.resolver.get_agent_card(agent_url)

                if agent_card:
                    # Update the card in case it changed
                    agent_data["card"] = agent_card.dict()
                    agent_data["verified"] = True
                    self.last_verified[agent_id] = datetime.now()
                    logging.info(f"✅ Verified agent: {agent_id}")
                else:
                    agent_data["verified"] = False
                    logging.warning(f"❌ Failed to verify agent: {agent_id}")

            except Exception as e:
                agent_data["verified"] = False
                logging.error(f"❌ Error verifying agent {agent_id}: {e}")

    async def cleanup_stale_agents(self):
        """Remove agents that haven't been verified recently"""
        cutoff = datetime.now() - timedelta(minutes=10)
        stale_agents = [
            agent_id for agent_id, last_verified in self.last_verified.items()
            if last_verified < cutoff
        ]

        for agent_id in stale_agents:
            del self.registered_agents[agent_id]
            del self.last_verified[agent_id]
            logging.info(f"🗑️ Removed stale agent: {agent_id}")

# Global discovery service instance
discovery_service = A2ADiscoveryService()

@app.post("/register")
async def register_agent(registration_data: Dict):
    """Register an agent using A2A SDK"""
    agent_url = registration_data.get("url")
    if not agent_url:
        raise HTTPException(status_code=400, detail="Agent URL required")

    agent_data = await discovery_service.register_agent_url(agent_url)
    if agent_data:
        return {
            "status": "registered",
            "agent_id": agent_data["id"],
            "agent_name": agent_data["card"]["name"]
        }

    raise HTTPException(status_code=400, detail="Failed to register agent")

@app.get("/discover")
async def discover_agents(
    skill: Optional[str] = None,
    capability: Optional[str] = None,
    verified_only: bool = True
):
    """Discover agents with optional filtering"""
    agents = list(discovery_service.registered_agents.values())

    if verified_only:
        agents = [agent for agent in agents if agent.get("verified", False)]

    if skill:
        agents = await discovery_service.discover_agents_by_skill(skill)

    if capability:
        agents = await discovery_service.discover_agents_by_capability(capability)

    return {
        "agents": agents,
        "count": len(agents),
        "filters": {"skill": skill, "capability": capability, "verified_only": verified_only}
    }

@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    if agent_id not in discovery_service.registered_agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_data = discovery_service.registered_agents[agent_id]

    # Try to get fresh agent card
    try:
        fresh_card = await discovery_service.resolver.get_agent_card(agent_data["url"])
        if fresh_card:
            agent_data["card"] = fresh_card.dict()
            agent_data["last_updated"] = datetime.now().isoformat()
    except Exception as e:
        logging.warning(f"Failed to refresh agent card for {agent_id}: {e}")

    return agent_data

@app.post("/verify")
async def verify_agents():
    """Manually trigger agent verification"""
    await discovery_service.verify_all_agents()
    await discovery_service.cleanup_stale_agents()

    return {
        "status": "verification_complete",
        "active_agents": len(discovery_service.registered_agents)
    }

async def background_verification():
    """Background task for periodic agent verification"""
    while True:
        try:
            await discovery_service.verify_all_agents()
            await discovery_service.cleanup_stale_agents()
            await asyncio.sleep(300)  # Verify every 5 minutes
        except Exception as e:
            logging.error(f"Background verification error: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    """Start background verification"""
    asyncio.create_task(background_verification())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting A2A SDK Discovery Service...")
    print("📡 Service available at: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Math Agent with A2A SDK (agents/math_agent.py)

```python
from a2a import Agent, AgentCard, AgentSkill, AgentProvider, AgentCapabilities
from a2a.server import A2AServer
import asyncio
import logging

# Create math agent card
math_agent_card = AgentCard(
    name="Advanced Math Agent",
    version="1.0.0",
    description="Mathematical computation agent using A2A SDK",
    provider=AgentProvider(
        organization="A2A Learning Hub",
        url="http://localhost:8000"
    ),
    url="http://localhost:8000",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="calculate",
            name="Mathematical Calculation",
            description="Perform arithmetic, algebra, and basic calculus operations",
            input_modes=["text"],
            output_modes=["text"],
            examples=["2 + 2", "sqrt(16)", "sin(pi/2)"]
        ),
        AgentSkill(
            id="equation_solve",
            name="Equation Solver",
            description="Solve mathematical equations",
            input_modes=["text"],
            output_modes=["text"],
            examples=["x^2 + 2x + 1 = 0", "2x + 3 = 7"]
        )
    ]
)

# Create the agent
math_agent = Agent(card=math_agent_card)

@math_agent.skill("calculate")
async def calculate(message, context):
    """Handle mathematical calculations"""
    try:
        expression = message.content.strip()

        # Safe evaluation (in production, use a proper math parser)
        import math

        # Allow common math functions
        safe_dict = {
            "__builtins__": {},
            "math": math,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
            "log": math.log,
            "abs": abs,
            "pow": pow,
            "round": round
        }

        result = eval(expression, safe_dict)

        return {
            "content": f"Result: {result}",
            "type": "text",
            "metadata": {
                "expression": expression,
                "result_type": type(result).__name__
            }
        }

    except Exception as e:
        return {
            "content": f"Error: {str(e)}",
            "type": "error",
            "metadata": {"error_type": type(e).__name__}
        }

@math_agent.skill("equation_solve")
async def solve_equation(message, context):
    """Solve mathematical equations"""
    try:
        equation = message.content.strip()

        # Simple linear equation solver (extend for more complex equations)
        if "=" in equation:
            left, right = equation.split("=")
            left, right = left.strip(), right.strip()

            # For simple cases like "2x + 3 = 7"
            if "x" in left and right.isdigit():
                # Very basic solver - extend this
                return {
                    "content": f"Equation: {equation}\nThis is a basic equation solver. Result would be calculated here.",
                    "type": "text",
                    "metadata": {"equation_type": "linear"}
                }

        return {
            "content": f"Equation format not recognized: {equation}",
            "type": "text"
        }

    except Exception as e:
        return {
            "content": f"Error solving equation: {str(e)}",
            "type": "error"
        }

async def register_with_discovery():
    """Register this agent with the discovery service"""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8080/register",
                json={"url": "http://localhost:8000"}
            )
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ Registered with discovery service: {result}")
            else:
                logging.warning(f"⚠️ Failed to register: {response.text}")
    except Exception as e:
        logging.warning(f"⚠️ Could not register with discovery service: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)

    # Create A2A server
    server = A2AServer(math_agent)

    print("🧮 Starting Advanced Math Agent...")
    print("🔢 Skills: calculate, equation_solve")
    print("📡 Agent card: http://localhost:8000/.well-known/agent-card.json")

    # Register with discovery service (if available)
    await register_with_discovery()

    # Start the server
    await server.start(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

### Discovery Client with A2A SDK (src/discovery_client.py)

```python
from a2a.client import A2ACardResolver, A2AClient
import asyncio
import httpx
import logging
from typing import List, Dict, Optional

class A2ADiscoveryClient:
    def __init__(self, discovery_service_url: str = "http://localhost:8080"):
        self.discovery_url = discovery_service_url
        self.resolver = A2ACardResolver()

    async def discover_agent_by_url(self, agent_url: str):
        """Directly discover an agent using A2A Card Resolver"""
        try:
            agent_card = await self.resolver.get_agent_card(agent_url)
            return agent_card
        except Exception as e:
            logging.error(f"Failed to discover agent at {agent_url}: {e}")
            return None

    async def discover_agents_via_service(
        self,
        skill: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[Dict]:
        """Discover agents via the discovery service"""
        try:
            params = {}
            if skill:
                params["skill"] = skill
            if capability:
                params["capability"] = capability

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.discovery_url}/discover", params=params)

                if response.status_code == 200:
                    return response.json().get("agents", [])

        except Exception as e:
            logging.error(f"Failed to discover agents via service: {e}")

        return []

    async def create_client_for_agent(self, agent_url: str):
        """Create an A2A client for a discovered agent"""
        try:
            # Verify agent exists and get card
            agent_card = await self.discover_agent_by_url(agent_url)
            if agent_card:
                # Create client using SDK
                client = A2AClient.get_client_from_agent_card_url(agent_url)
                return client, agent_card
        except Exception as e:
            logging.error(f"Failed to create client for {agent_url}: {e}")

        return None, None

    async def test_agent_communication(self, agent_url: str, skill_id: str, test_message: str):
        """Test communication with a discovered agent"""
        client, agent_card = await self.create_client_for_agent(agent_url)

        if client and agent_card:
            try:
                response = await client.send_message(
                    skill_id=skill_id,
                    message={
                        "content": test_message,
                        "role": "user"
                    }
                )
                return response
            except Exception as e:
                logging.error(f"Communication test failed: {e}")

        return None

    async def discover_and_test_skill(self, skill_id: str, test_message: str):
        """Discover agents with a skill and test communication"""
        print(f"🔍 Discovering agents with skill: {skill_id}")

        agents = await self.discover_agents_via_service(skill=skill_id)

        if not agents:
            print(f"❌ No agents found with skill: {skill_id}")
            return []

        results = []
        for agent_data in agents:
            agent_url = agent_data.get("url")
            agent_name = agent_data.get("card", {}).get("name", "Unknown")

            print(f"🧪 Testing {agent_name} at {agent_url}")

            response = await self.test_agent_communication(agent_url, skill_id, test_message)

            if response:
                print(f"✅ Response: {response.get('content', 'No content')}")
                results.append({
                    "agent": agent_data,
                    "response": response,
                    "success": True
                })
            else:
                print(f"❌ Failed to communicate with {agent_name}")
                results.append({
                    "agent": agent_data,
                    "response": None,
                    "success": False
                })

        return results

# Example usage functions
async def demo_basic_discovery():
    """Demonstrate basic agent discovery"""
    client = A2ADiscoveryClient()

    print("🎯 A2A SDK Discovery Demo")
    print("=" * 40)

    # Direct agent discovery
    print("\n1. Direct Agent Discovery")
    agent_card = await client.discover_agent_by_url("http://localhost:8000")
    if agent_card:
        print(f"✅ Discovered: {agent_card.name}")
        print(f"   Skills: {[skill.name for skill in agent_card.skills]}")

    # Service-based discovery
    print("\n2. Service-Based Discovery")
    agents = await client.discover_agents_via_service()
    print(f"✅ Found {len(agents)} agents via discovery service")

    for agent_data in agents:
        card = agent_data.get("card", {})
        print(f"   - {card.get('name', 'Unknown')} ({card.get('version', 'N/A')})")

async def demo_skill_discovery():
    """Demonstrate skill-based discovery and testing"""
    client = A2ADiscoveryClient()

    print("\n🔍 Skill-Based Discovery Demo")
    print("=" * 40)

    # Test math skill
    results = await client.discover_and_test_skill("calculate", "2 + 2 * 3")

    print(f"\n📊 Results: {len(results)} agents tested")
    successful = [r for r in results if r["success"]]
    print(f"✅ Successful communications: {len(successful)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        await demo_basic_discovery()
        await demo_skill_discovery()

    asyncio.run(main())
```

## 🧪 Testing Examples

### Basic Discovery Test (examples/basic_discovery.py)

```python
import asyncio
from src.discovery_client import A2ADiscoveryClient

async def main():
    client = A2ADiscoveryClient()

    print("🔍 A2A Agent Discovery Test")
    print("=" * 30)

    # Test direct discovery
    print("\n1. Testing direct agent discovery...")
    agent_card = await client.discover_agent_by_url("http://localhost:8000")

    if agent_card:
        print(f"✅ Agent found: {agent_card.name}")
        print(f"   Description: {agent_card.description}")
        print(f"   Skills available: {len(agent_card.skills)}")

        for skill in agent_card.skills:
            print(f"     - {skill.name} ({skill.id})")
    else:
        print("❌ No agent found at localhost:8000")

    # Test service discovery
    print("\n2. Testing discovery service...")
    agents = await client.discover_agents_via_service()
    print(f"✅ Discovery service found {len(agents)} agents")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Discovery Test (examples/advanced_discovery.py)

```python
import asyncio
from src.discovery_client import A2ADiscoveryClient

async def main():
    client = A2ADiscoveryClient()

    print("🚀 Advanced A2A Discovery Features")
    print("=" * 40)

    # Test skill discovery and communication
    test_cases = [
        {"skill": "calculate", "message": "sqrt(16) + 2^3"},
        {"skill": "equation_solve", "message": "2x + 4 = 10"}
    ]

    for test_case in test_cases:
        print(f"\n🧪 Testing skill: {test_case['skill']}")
        print(f"📝 Test message: {test_case['message']}")

        results = await client.discover_and_test_skill(
            test_case['skill'],
            test_case['message']
        )

        if results:
            for result in results:
                if result['success']:
                    agent_name = result['agent']['card']['name']
                    response_content = result['response'].get('content', 'No content')
                    print(f"✅ {agent_name}: {response_content}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Key Learning Points

### 1. A2A SDK Agent Discovery

- Using `A2ACardResolver` for automatic agent card resolution
- Leveraging `.well-known/agent-card.json` standard endpoints
- Error handling in discovery operations

### 2. Client Creation from Discovery

- `A2AClient.get_client_from_agent_card_url()` for automatic client setup
- SDK-managed HTTP client lifecycle
- Proper error handling for failed connections

### 3. Agent Registration Patterns

- Automatic agent card verification via SDK
- Registry integration with A2A Card Resolver
- Health monitoring using periodic card resolution

### 4. Skill and Capability Matching

- SDK-native skill identification and filtering
- Capability-based agent selection
- Dynamic agent communication testing

## 🎯 Success Criteria

- [ ] A2A SDK discovery service running and accepting registrations
- [ ] Agents successfully registered using `A2ACardResolver`
- [ ] Skill-based discovery working with SDK
- [ ] Agent communication established via discovered cards
- [ ] Health monitoring using periodic card resolution

## 🔗 Next Steps

After mastering A2A SDK-based agent discovery, proceed to **[Step 10: Agent-to-Agent Communication](../10_agent_to_agent/README.md)** to implement advanced communication patterns using the official SDK.

## 📚 Additional Resources

- [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)
- [A2ACardResolver API Reference](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.client.A2ACardResolver)
- [A2A Agent Discovery Guide](https://google-a2a.github.io/A2A/topics/agent-discovery/)
- [Agent Cards Specification](https://google-a2a.github.io/A2A/specification/#agent-cards)
