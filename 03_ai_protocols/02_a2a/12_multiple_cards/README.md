# Step 11: Public vs Extended Agent Cards 🔐

**Learn A2A agent card tiers - public discovery vs authenticated extended capabilities**

> **Goal**: Implement the A2A pattern of public agent cards with additional authenticated extended cards using the official A2A SDK.

## 🎯 What You'll Learn

- A2A public vs extended agent card patterns
- Authentication-gated skill access using A2A SDK
- `supportsAuthenticatedExtendedCard` feature
- Tiered capability disclosure
- Visual comparison of card differences
- Foundation for secure agent architectures

## 💡 Key Insights

1. **Tiered access enables business models** - Public discovery with premium features
2. **Authentication context matters** - Skills must check user permissions
3. **Capability advertising strategy** - What to show publicly vs privately
4. **User experience flow** - Clear path from public to authenticated access
5. **A2A supports complex access patterns** - Not just all-or-nothing

## 📋 Prerequisites

- Completed [Step 02: Agent Skill](../02_agent_skill/)
- Understanding of AgentCard and AgentSkill types from A2A SDK

## 🎯 A2A Concept: Agent Card Tiers

A2A agents can expose **two different agent cards**:

1. **Public Card**: Basic capabilities visible to everyone
2. **Extended Card**: Additional capabilities for authenticated users only

This enables **capability tiering** - public discovery with premium features for authorized access.

## 🚀 Implementation

We'll create a single agent with dual agent cards using the official A2A SDK:

### 1. Initialize Project

```bash
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill, AgentCard, AgentProvider, AgentCapabilities

class TieredAgentExecutor(AgentExecutor):
    """Agent executor supporting both public and extended skills"""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute based on skill ID and authentication status"""

        ...

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel execution"""
        ...

    # PUBLIC SKILL - Available to everyone
    public_skill = AgentSkill(
        id='hello_world',
        name='Basic Hello World',
        description='Returns a friendly hello world greeting - available to all users',
        tags=['greeting', 'public', 'basic'],
        examples=['hi', 'hello', 'greet me'],
    )

    # EXTENDED SKILLS - Only for authenticated users
    super_skill = AgentSkill(
        id='super_hello_world',
        name='Super Hello World',
        description='Returns an enhanced SUPER greeting with special formatting - requires authentication',
        tags=['greeting', 'premium', 'enhanced', 'authenticated'],
        examples=['super hi', 'give me a super hello', 'premium greeting'],
    )

    premium_skill = AgentSkill(
        id='premium_analysis',
        name='Premium Analysis',
        description='Advanced computational analysis features - authenticated users only',
        tags=['analysis', 'premium', 'advanced', 'authenticated'],
        examples=['analyze this data', 'premium insights', 'advanced analysis'],
    )

    # PUBLIC AGENT CARD - Basic capabilities visible to everyone
    public_agent_card = AgentCard(
        name='Tiered Capability Agent',
        description='An A2A agent demonstrating public vs authenticated extended capabilities',
        url='http://localhost:8005/',
        version='1.0.0',
        provider=AgentProvider(
            organization='A2A Tiered Services Lab',
            url='http://localhost:8005/'
        ),
        iconUrl='http://localhost:8005/icon.png',
        documentationUrl='http://localhost:8005/docs',
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=False
        ),
        skills=[public_skill],  # Only public skill in public card
        supportsAuthenticatedExtendedCard=True,  # Indicates extended card is available
    )

    # EXTENDED AGENT CARD - Full capabilities for authenticated users
    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Tiered Capability Agent - Extended Edition',
            'description': 'Full-featured A2A agent with premium capabilities for authenticated users',
            'version': '1.1.0',  # Different version for extended features
            'skills': [
                public_skill,    # Include public skill
                super_skill,     # Add premium skills
                premium_skill,
            ],
            # Inherit all other settings from public card
        }
    )

```

And main.py

```python
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from tiered_agent import TieredAgentExecutor, public_agent_card, extended_agent_card

if __name__ == "__main__":
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=TieredAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create A2A server with BOTH agent cards
    server = A2AStarletteApplication(
        agent_card=public_agent_card,           # Public card
        http_handler=request_handler,
        extended_agent_card=extended_agent_card,  # Extended card for authenticated users
    )

    print("🔐 Starting Tiered Capability Agent on port 8005...")
    print(f"📋 Public skills: {[skill.id for skill in public_agent_card.skills]}")
    print(f"🌟 Extended skills: {[skill.id for skill in extended_agent_card.skills]}")
    print(f"🔑 Extended card support: {public_agent_card.supportsAuthenticatedExtendedCard}")

    uvicorn.run(server.build(), host="0.0.0.0", port=8005)

```

## 🧪 Testing

### 1. Start the Tiered Agent

```bash
uv run python main.py
```

### 2. Visual Agent Card Comparison

**Public Card** (everyone can see):
http://localhost:8005/.well-known/agent-card.json

**Extended Card** (authenticated users only):
http://localhost:8005/agent/authenticatedExtendedCard

### 3. Compare Cards in Browser

Open both URLs and notice the differences:

### Public Card Discovery

- ✅ Shows basic capabilities only
- ✅ Indicates extended card is available via `supportsAuthenticatedExtendedCard: true`
- ✅ Allows public skill testing
- ✅ Standard A2A agent card format

### Extended Card Discovery

- ✅ Shows all capabilities (public + premium)
- ✅ Different name and version
- ✅ Additional premium skills visible
- ✅ Same base structure as public card

### Skill Execution

- ✅ Public skills work for everyone
- ✅ Premium skills show authentication requirements
- ✅ Clear feedback about access levels

## 🔍 Key A2A Concepts

### Agent Card Tiering

- **Public discovery**: Anyone can see basic capabilities
- **Extended capabilities**: Premium features for authenticated users
- **Graduated access**: Start with public, upgrade to extended
- **Clear indication**: `supportsAuthenticatedExtendedCard` flag

### Capability Disclosure Strategy

- **Marketing approach**: Public card showcases basic value
- **Security approach**: Sensitive capabilities hidden until authenticated
- **Scalability approach**: Different service tiers
- **Discovery approach**: Users know extended features exist

### A2A Authentication Integration

- **Standard endpoints**: Both cards use standard A2A endpoints
- **Authentication context**: Skills check authentication status
- **Graceful degradation**: Public skills always work
- **Clear messaging**: Users understand access requirements

### Why This Pattern Matters

- **Business models**: Enable freemium and premium service tiers
- **Security**: Sensitive capabilities aren't publicly advertised
- **User experience**: Clear progression from basic to advanced features
- **Agent discovery**: Public cards enable efficient ecosystem discovery

## 🎯 Next Step

**Ready for Step 04?** → [04_agent_executor](../04_agent_executor/) - Implement the Agent Executor pattern with proper request handling

---

## 🏗️ Enterprise Applications

1. **SaaS API agents**: Free tier vs paid tier capabilities
2. **Internal vs external APIs**: Different capabilities for different user types
3. **Security-sensitive agents**: Hide advanced features until verified
4. **Progressive feature unlock**: Users discover more as they authenticate
5. **Compliance requirements**: Restrict certain features to authorized users

## 📖 Official Reference

This step demonstrates extended agent card concepts from: [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

**🎉 Congratulations! You've implemented A2A agent card tiering with public and extended capabilities!**
