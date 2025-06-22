from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from agent_card import HelloWorldAgentExecutor, public_agent_card

# --8<-- [end:AgentCard]
request_handler = DefaultRequestHandler(
    agent_executor=HelloWorldAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

server_app = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler
)
    
server = server_app.build()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(server, host='0.0.0.0', port=8000)
