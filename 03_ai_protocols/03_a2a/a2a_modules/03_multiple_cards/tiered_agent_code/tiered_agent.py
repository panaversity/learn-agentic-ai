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
