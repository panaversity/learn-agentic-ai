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
