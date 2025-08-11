# Step 02: Agent Skill 🛠️

**Add skills to your agent card using official A2A SDK - visual skill discovery**

> **Goal**: Extend your agent card with actual skills using the official A2A SDK and AgentSkill types.

## 🎯 What You'll Learn

- How to define A2A agent skills using official SDK
- AgentSkill structure and metadata
- Visual skill discovery in browser
- How skills appear in agent cards
- Foundation for agent capabilities

## 📋 Prerequisites

- Completed [Step 01: Agent Card](../01_agent_card/)
- Understanding of JSON structure
- UV package manager installed

## 🚀 Implementation

### 1. Create UV Project

```bash
cd 02_agent_skill
uv init a2a02_code
cd a2a02_code
uv add a2a-sdk uvicorn
```

### 2. Agent with Skills Implementation

**File**: `main.py`

```python
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    AgentProvider,
)

class SkillDemoAgent:
    """Agent with greeting and math capabilities."""

    async def invoke(self, skill_id: str, input_data: dict) -> str:
        """Invoke specific skill with input data."""
        if skill_id == "greeting":
            return f"Good day, Nice to meet you."

        elif skill_id == "simple_math":
            return f"Operation simple_math not implemented yet"

        return f"Unknown skill: {skill_id}"


class SkillDemoAgentExecutor(AgentExecutor):
    """Agent Executor with multiple skills."""

    def __init__(self):
        self.agent = SkillDemoAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute agent with skill-based routing."""
        # For demo, we'll use first skill and mock input
        result = await self.agent.invoke("greeting", {"name": "A2A Learner"})
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel execution."""
        raise Exception('cancel not supported')


if __name__ == '__main__':
    # Define agent skills using official A2A types
    greeting_skill = AgentSkill(
        id='greeting',
        name='Personalized Greeting',
        description='Generate personalized greetings for users based on name and time of day',
        tags=['greeting', 'social'],
        examples=['Hello Alice', 'Good morning Bob'],
    )

    math_skill = AgentSkill(
        id='simple_math',
        name='Simple Math Operations',
        description='Perform basic mathematical operations like addition and multiplication',
        tags=['math', 'calculation'],
        examples=['Add 5 and 3', 'Multiply 4 by 7'],
    )

    # Create agent card with skills
    public_agent_card = AgentCard(
        name='Skilled A2A Agent',
        description='An A2A agent demonstrating multiple skills using official SDK',
        url='http://localhost:8001/',
        version='1.1.0',
        provider=AgentProvider(
            organization='A2A Learning Lab',
            url='http://localhost:8001/',
        ),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=False,
        ),
        skills=[greeting_skill, math_skill],  # Official AgentSkill objects
    )

    # Create server using official A2A SDK
    request_handler = DefaultRequestHandler(
        agent_executor=SkillDemoAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    print("🚀 Starting A2A Agent with Skills...")
    print("🛠️ This agent has the following skills:")
    for skill in public_agent_card.skills:
        print(f"   - {skill.id}: {skill.description}")
    print("\n📋 Test URLs:")
    print("   - Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("   - A2A Endpoint: http://localhost:8001/a2a")
    uvicorn.run(server.build(), host='0.0.0.0', port=8001)
```

## 🧪 Testing

### 1. Start the Server

```bash
cd a2a02_code
uv run python main.py
```

### 2. Visual Test in Browser

Open these URLs in your browser:

1. **Agent Card with Skills**: http://localhost:8001/.well-known/agent-card.json
   - **Key insight**: See how skills are embedded using official AgentSkill types
   - Notice the skill structure: id, name, description, tags, examples
   - Skills are now proper A2A SDK objects, not custom JSON

### 4. Test with Official A2A Client

**File**: `test_client.py`

```python
import asyncio
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from uuid import uuid4

async def test_skills():
    base_url = 'http://localhost:8001'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()

        print(f"Agent has {len(agent_card.skills)} skills:")
        for skill in agent_card.skills:
            print(f"  - {skill.id}: {skill.description}")

        # Test messaging
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': 'Hello skilled agent!'}],
                    'messageId': uuid4().hex,
                }
            )
        )
        response = await client.send_message(request)
        print("Response:", response.model_dump(exclude_none=True))

if __name__ == '__main__':
    asyncio.run(test_skills())
```

## 📊 Expected Output

When you visit `http://localhost:8001/.well-known/agent-card.json`, you should see skills using official A2A SDK structure:

```json
{
  "name": "Skilled A2A Agent",
  "description": "An A2A agent demonstrating multiple skills using official SDK",
  "url": "http://localhost:8001/",
  "version": "1.1.0",
  "provider": {
    "organization": "A2A Learning Lab",
    "url": "http://localhost:8001/"
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {
      "id": "greeting",
      "name": "Personalized Greeting",
      "description": "Generate personalized greetings for users based on name and time of day",
      "tags": ["greeting", "social"],
      "examples": ["Hello Alice", "Good morning Bob"]
    },
    {
      "id": "simple_math",
      "name": "Simple Math Operations",
      "description": "Perform basic mathematical operations like addition and multiplication",
      "tags": ["math", "calculation"],
      "examples": ["Add 5 and 3", "Multiply 4 by 7"]
    }
  ]
}
```

## 🔍 Key A2A Concepts

### Official AgentSkill Structure

Following the [A2A specification](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.types.AgentSkill):

- **id**: Unique identifier for the skill (required)
- **name**: Human-readable skill name (required)
- **description**: What the skill does (required)
- **tags**: Categorization and searchability (optional)
- **examples**: Sample usage patterns (optional)

### Agent Executor Integration

- **SkillDemoAgentExecutor**: Extends official AgentExecutor base class
- **execute()**: Handles A2A protocol and routes to skill logic
- **RequestContext**: Contains request metadata
- **EventQueue**: Manages response streaming

### Official A2A SDK Benefits

- **Type safety**: Pydantic models ensure correct structure
- **Protocol compliance**: Automatic A2A JSON-RPC handling
- **Streaming support**: Built-in event queue management
- **Task management**: Automatic task lifecycle handling

### Skill Discovery & Advertising

- **Agent cards advertise skills**: Other agents see capabilities via discovery
- **Standard format**: Official AgentSkill type ensures interoperability
- **Self-documenting**: Rich metadata (tags, examples) aids understanding
- **Composition ready**: Skills can be chained and orchestrated

## ✅ Success Criteria

- ✅ UV project created with a2a-server dependency
- ✅ Server starts without errors using official A2A SDK
- ✅ Agent card shows 2 skills using official AgentSkill types
- ✅ Skills have proper id, name, description, tags, and examples
- ✅ A2A endpoint responds to message/send requests
- ✅ Console shows skill advertisements when accessed
- ✅ Official A2A client can interact with the agent

## 🎯 Next Step

**Ready for Step 03?** → [03_multiple_cards](../03_multiple_cards/) - Create an ecosystem of specialized agents

---

## 💡 Key Insights

1. **Skills are contracts** - Input/output schemas define exactly how to interact
2. **Discovery is powerful** - Other agents can find and understand your capabilities
3. **Schemas enable automation** - Agents can automatically validate and use skills
4. **Specialization works** - Agents can focus on specific capabilities
5. **Visual inspection helps** - Browser testing reveals skill structure clearly

## 🔧 Skill Design Best Practices

1. **Clear names**: Use descriptive, unique skill names
2. **Good descriptions**: Explain what the skill does and when to use it
3. **Proper schemas**: Define all required and optional parameters
4. **Consistent outputs**: Use predictable output formats
5. **Error handling**: Consider what happens when inputs are invalid

## 📖 Official Reference

This step implements concepts from: [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

**🎉 Congratulations! Your agent now has discoverable skills using the official A2A SDK!**
