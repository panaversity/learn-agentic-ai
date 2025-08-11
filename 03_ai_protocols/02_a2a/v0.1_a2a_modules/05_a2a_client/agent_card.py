import uvicorn
import logging
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from greet_agent import GreetingAgentExecutor

# Enable detailed logging to see A2A communication
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_greeting_agent_server(port: int = 8000):
    """
    Create and configure the A2A Greeting Agent server.

    This server is used to test A2A client implementations.
    """

    # Define agent skill
    skill = AgentSkill(
        id='greeting_agent',
        name='Greeting Agent',
        description='A friendly agent that responds to greetings and processes user messages',
        tags=['greeting', 'chat', 'friendly', 'test'],
        examples=['hello', 'hi there', 'how are you?',
                  'goodbye', 'tell me about yourself'],
    )

    # Create agent card
    agent_card = AgentCard(
        name='A2A Greeting Agent',
        description='A friendly A2A agent for testing client-server communication patterns',
        url=f'http://localhost:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        # Support both streaming and non-streaming
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Setup A2A server with corrected agent executor
    request_handler = DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),  # Uses corrected message extraction
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    return server, agent_card


if __name__ == '__main__':
    port = 8000
    server, card = create_greeting_agent_server(port)

    print("🤖 Starting A2A Greeting Agent Server...")
    print(
        f"📋 Agent Discovery: http://localhost:{port}/.well-known/agent-card.json")
    print(f"💬 Agent Name: {card.name}")
    print(f"🎯 Skills: {[skill.name for skill in card.skills]}")
    print("🔗 Ready for A2A client connections...")
    print()
    print("Test with:")
    print(f"curl http://localhost:{port}/.well-known/agent-card.json | jq '.'")
    print()

    uvicorn.run(server.build(), host='0.0.0.0', port=port)
