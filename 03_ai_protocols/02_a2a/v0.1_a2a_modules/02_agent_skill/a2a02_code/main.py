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
