# Step 1: A2A Fundamentals (Give your Agent Discovery Card to market right Skills)

**Learning Goal**: Master the complete A2A discovery system using the official A2A Python SDK, including agent cards, skills, capabilities, and multi-agent ecosystems.

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ Use the official A2A Python SDK for agent development
- ✅ Understand A2A agent discovery through standardized agent cards
- ✅ Design agent skills using official AgentSkill types
- ✅ Build a multi-agent ecosystem with varied specializations
- ✅ Master the foundational concepts before diving into protocol details

## 📚 Core Concepts

- [Agent Card Specification🏷️](https://google-a2a.github.io/A2A/latest/specification/#55-agentcard-object-structure)
- [A2A Skills specification](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.types.AgentSkill)
- [Agent Skills & Agent Card Example](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

### 1. Agent Cards - The Business Cards of AI

Agent cards are JSON documents served using the official A2A SDK that act as "business cards" for AI agents. They enable discovery by advertising:

- **Identity**: Name and description
- **Location**: URL endpoint for communication
- **Capabilities**: What the agent can do
- **Skills**: Specific functions offered using AgentSkill types
- **Formats**: Supported input/output types
- **Examples**: Sample queries for guidance
- **Provider**: Organization information using AgentProvider

### 2. Skills Definition with Official SDK

Skills are specific capabilities that agents advertise using the official `AgentSkill` type:

- **Structured Skills**: Use AgentSkill objects with id, name, description
- **Granular Functions**: Individual tasks (e.g., "greeting", "math_operations")
- **Clear Descriptions**: What each skill accomplishes
- **Example Queries**: How to invoke each skill
- **Tags**: Categorization for discovery
- **Type Safety**: Pydantic models ensure correct structure

### 3. Multi-Agent Ecosystems with SDK

Understanding how multiple agents work together using official components:

- **Specialization**: Each agent focuses on specific domains
- **Discovery**: Agents find each other through standardized cards
- **Interoperability**: Official SDK ensures framework compatibility
- **Orchestration**: Host agents coordinate multiple specialists
- **Type Safety**: Official types prevent integration errors

## 🛠️ Implementation Using Official A2A SDK

### Our Approach: Learning by Building One Complete Agent

We'll build one agent that demonstrates all A2A concepts. This approach helps you:

1. **Focus deeply** on core concepts without getting overwhelmed
2. **See relationships** between different A2A components
3. **Build confidence** through hands-on success
4. **Apply what you learn** to other agents later

### Project Setup

```bash
# Create new UV project
uv init hello_a2a
cd hello_a2a

# Add official A2A SDK and dependencies
uv add "a2a-sdk[http-server]" uvicorn
# After next released i.e: 3.1 it may change to uv add "a2a-sdk[http-server]"[http-server]
# see: https://github.com/a2aproject/a2a-python/pull/217
```

## 📚 Complete Agent Implementation: Calendar Agent

We'll build a **Calendar Agent** because scheduling is:

- **Universally relatable** - everyone manages calendars
- **Skill-diverse** - demonstrates multiple agent capabilities
- **Interactive** - provides clear input/output examples
- **Extensible** - easy to add new features as you learn

### Step 1: Understanding the Agent Card Structure

Let's examine each component of an A2A agent card and why it matters:

```python
# calendar_agent.py - Complete A2A Agent Implementation
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.utils import new_agent_text_message
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, AgentProvider

# 🎯 CONCEPT 1: Agent Business Logic (Your Core Functionality)
class CalendarAgent:
    """
    This is YOUR agent's brain - the actual business logic.
    Think of this as the 'worker' that does the real tasks.
    """
    async def invoke(self, message) -> str:
        """Invoke the Agent"""
        return "Not taking any task"

# 🎯 CONCEPT 2: Agent Executor (A2A Protocol Bridge)
class CalendarAgentExecutor(AgentExecutor):
    """
    This is the A2A protocol handler - it connects A2A messages
    to your agent's business logic. Think of it as a 'translator'.
    """

    def __init__(self):
        self.agent = CalendarAgent()  # Connect to your business logic

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        This method receives A2A requests and calls your agent methods.
        In a real implementation, you'd parse the request and route to appropriate methods.
        """
        # Demo: Show how agent processes a request
        result = await self.agent.invoke(context.get_user_input())

        # Send response back through A2A protocol
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle request cancellation."""
        raise Exception('cancel not supported in this example')

# 🎯 CONCEPT 3: Agent Skills (What You Advertise to Others)
calendar_skills = [
    AgentSkill(
        id="check_availability",           # Unique identifier
        name="Check Availability",        # Human-readable name
        description="Check free time slots for given dates and times",  # What it does
        tags=["calendar", "availability", "scheduling"],  # Categories for discovery
        examples=[  # Help other agents/users understand usage
            "Am I free tomorrow at 3 PM?",
            "What's my availability this week?",
            "Check if Tuesday afternoon is open"
        ]
    ),
    AgentSkill(
        id="schedule_meeting",
        name="Schedule Meeting",
        description="Schedule new meetings and send invitations",
        tags=["calendar", "meeting", "scheduling"],
        examples=[
            "Schedule a team meeting for Friday at 2 PM",
            "Book a 1-hour call with John next Tuesday",
            "Set up a project review meeting"
        ]
    ),
    AgentSkill(
        id="find_conflicts",
        name="Find Conflicts",
        description="Identify scheduling conflicts and suggest alternatives",
        tags=["calendar", "conflicts", "optimization"],
        examples=[
            "Check for conflicts in my schedule this week",
            "Find overlapping meetings",
            "Analyze my calendar for double-bookings"
        ]
    )
]

# 🎯 CONCEPT 4: Agent Card (Your Digital Business Card)
calendar_agent_card = AgentCard(
    # Basic Identity
    name="Personal Calendar Agent",
    description="Manages scheduling, availability, and calendar coordination using A2A SDK",
    url="http://localhost:8001/mcp",        # Where to find this agent
    version="1.0.0",                     # Version for compatibility

    # Provider Information (Who built this agent)
    provider=AgentProvider(
        organization="A2A Learning Lab",
        url="https://github.com/a2a-learning"
    ),

    # Communication Formats (What languages this agent speaks)
    default_input_modes=["text/plain", "application/json"],   # What it can receive
    default_output_modes=["application/json", "text/plain"],  # What it can send

    # Technical Capabilities (Advanced features)
    capabilities=AgentCapabilities(
        streaming=False,                 # Can send real-time updates?
        push_notifications=True,          # Can send alerts?
        state_transition_history=False     # Tracks conversation history?
    ),

    # Available Skills (What this agent can do)
    skills=calendar_skills
)

# 🎯 CONCEPT 5: A2A Server (The Official Protocol Implementation)
if __name__ == "__main__":
    # Create the request handler with your executor
    request_handler = DefaultRequestHandler(
        agent_executor=CalendarAgentExecutor(),  # Your agent logic
        task_store=InMemoryTaskStore(),          # Memory for tasks
        queue_manager=InMemoryQueueManager()
    )

    # Create the A2A-compliant server
    server = A2AFastAPIApplication(
        agent_card=calendar_agent_card,  # Your agent's business card
        http_handler=request_handler     # Your request processor
    )

    # Start the server with helpful information
    print("🗓️ Starting Calendar Agent on port 8001...")
    print("📋 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("🔗 A2A Endpoint: http://localhost:8001/a2a")
    print("🛠️ Skills Available:", [skill.id for skill in calendar_skills])
    print("\n💡 Try: curl http://localhost:8001/.well-known/agent-card.json")

    import uvicorn
    from fastapi import FastAPI

    app: FastAPI = server.build()

    uvicorn.run(server.build(), host="localhost", port=8001)
```

### Step 2: **Run your agent** and Test it

1. **Save the complete calendar agent** as `calendar_agent.py`

2. **Run your agent**:

```bash
uv run python calendar_agent.py
```

4. **Test agent discovery**:

```bash
# See your agent's business card
curl http://localhost:8001/.well-known/agent-card.json | jq

# What skills does your agent offer?
curl http://localhost:8001/.well-known/agent-card.json | jq '.skills[].name'

# What are the agent's capabilities?
curl http://localhost:8001/.well-known/agent-card.json | jq '.capabilities'
```

### 🔍 Understanding Each Component

Let's analyze why each part exists and how they work together:

#### 1. **CalendarAgent Class**: Your Core Business Logic

- **Purpose**: Contains the actual functionality (scheduling, checking availability)
- **Why separate**: Keeps your business logic independent of A2A protocol
- **Key insight**: Focus on what your agent does, not how it communicates

#### 2. **CalendarAgentExecutor Class**: Protocol Bridge

- **Purpose**: Translates A2A requests into calls to your business logic
- **Why needed**: A2A protocol requires specific request/response handling
- **Key insight**: This handles the technical communication details for you

#### 3. **AgentSkill Objects**: Public Interface Declaration

- **Purpose**: Tells other agents what this agent can do
- **Why important**: Enables agent discovery and coordination
- **Key insight**: Think of these as your agent's resume

#### 4. **AgentCard Object**: Digital Business Card

- **Purpose**: Advertises agent identity, location, and capabilities
- **Why structured**: Enables automatic discovery and validation
- **Key insight**: This makes your agent discoverable by others

#### 5. **A2AFastAPIApplication**: Official FastAPI Server Implementation

- **Purpose**: Handles all A2A protocol requirements automatically
- **Why use official SDK**: Ensures compatibility and reduces boilerplate
- **Key insight**: Focus on your agent logic, let the SDK handle the protocol

## 🧪 Single-Agent Learning Experience

### Exercise 1: Modify Your Agent's Skills

Practice by making changes and seeing immediate results:

1. **Add a new skill** to `calendar_skills` array:

```python
AgentSkill(
    id="send_reminders",
    name="Send Reminders",
    description="Send meeting reminders via email or SMS",
    tags=["calendar", "reminders", "notifications"],
    examples=["Remind me about tomorrow's meeting", "Send a reminder 30 minutes before"]
)
```

2. **Restart and test** - see how your agent card changes!

### Exercise 2: Test with Simple Client

1. Create a simple test to understand agent communication:

```python
# test_calendar.py
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
```

2. Test with Official A2A Client

**File**: `test_client.py`

```python
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
```

## ✅ Success Criteria

You've mastered A2A fundamentals when you can:

- [ ] **Explain the agent card**: Understand each field in the AgentCard and why it exists
- [ ] **Design meaningful skills**: Create AgentSkill objects that clearly describe capabilities
- [ ] **Separate concerns**: Distinguish between business logic (CalendarAgent) and protocol handling (AgentExecutor)
- [ ] **Test agent discovery**: Use curl to fetch and examine agent cards
- [ ] **Modify agent capabilities**: Add new skills and see them reflected in the agent card
- [ ] **Understand the A2A pattern**: See how the official SDK handles protocol compliance

## 🎓 Key Takeaways

1. **Focus on One Thing**: One comprehensive example teaches more than multiple simple ones
2. **Separate Your Concerns**: Business logic vs. protocol handling vs. interface definition
3. **Use the Official SDK**: Type safety, protocol compliance, and reduced boilerplate
4. **Agent Discovery**: Standardized `.well-known/agent-card.json` enables automatic discovery
5. **Skills as Contracts**: AgentSkill objects provide rich metadata for agent coordination
6. **Build Incrementally**: Start simple, add features step by step

## 📖 Official References

- [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)
- [AgentCard Specification](https://google-a2a.github.io/A2A/latest/specification/#55-agentcard-object-structure)
- [AgentSkill Types](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.types.AgentSkill)
- [Agent Execution Patterns](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

## 🚀 Next Step

With A2A fundamentals mastered through hands-on practice with a single comprehensive agent, you're ready for **Step 2: Agent Executor** where you'll learn how to handle complex request routing and response management.

---

**Time Investment**: ~1 hour  
**Difficulty**: Beginner  
**Skills Gained**: A2A agent cards, official SDK usage, agent skills design, protocol understanding  
**Prerequisites**: Python 3.12+, UV package manager

**🎉 Congratulations! You've mastered A2A fundamentals with a deep, practical understanding!**
