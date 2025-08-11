import uvicorn
import logging
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Choose which executor to use
from agent_executor import EnhancedAgentExecutor  # Official example
# from enhanced_agent_executor import EnhancedAgentExecutor  # Enhanced version

# Enable detailed logging to see EventQueue operations
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Agent skill definition
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='Official A2A HelloWorld example - just returns hello world',
        tags=['hello world', 'tutorial', 'official'],
        examples=['hi', 'hello world', 'test'],
    )

    # Agent card matching official tutorial
    agent_card = AgentCard(
        name='Hello World Agent Executor',
        description='Official A2A Agent Executor tutorial implementation',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    # Setup A2A server with official components
    request_handler = DefaultRequestHandler(
        agent_executor=EnhancedAgentExecutor(),  # Use official executor
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("🎯 Starting Official Agent Executor Server...")
    print("📋 Agent Discovery: http://localhost:9999/.well-known/agent-card.json")
    print("💬 Test with curl or Postman (see collection below)...")
    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
