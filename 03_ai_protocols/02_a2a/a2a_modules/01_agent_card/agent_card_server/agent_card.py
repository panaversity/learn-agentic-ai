from a2a.types import AgentCapabilities, AgentCard, AgentProvider

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue


class HelloWorldAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        ...

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        ...


# Complete Agent Card following A2A specification
public_agent_card = AgentCard(
    name='Hello World A2A Agent',
    description='A simple A2A agent that demonstrates basic agent card discovery and structure. This agent serves as a foundation for learning A2A protocol concepts.',
    url='http://localhost:8000/',
    version='1.0.0',
    provider=AgentProvider(
        organization='A2A Learning Lab',
        url='https://github.com/your-org/a2a-learning'
    ),
    iconUrl='http://localhost:8000/icon.png',  # Optional: agent icon
    documentationUrl='http://localhost:8000/docs',  # Optional: documentation
    defaultInputModes=['text/plain', 'application/json'],
    defaultOutputModes=['text/plain', 'application/json'],
    capabilities=AgentCapabilities(
        streaming=True,
        pushNotifications=False,
        stateTransitionHistory=False
    ),
    skills=[],  # Empty for basic agent card - skills added in Step 02
    # Security schemes would be added for production agents
    securitySchemes=None,  # None for development - add authentication in production
    security=None,  # None for development
    supportsAuthenticatedExtendedCard=False  # Set to True if supporting extended cards
)