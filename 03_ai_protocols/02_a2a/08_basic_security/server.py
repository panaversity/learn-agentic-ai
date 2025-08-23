from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from a2a.types import AgentCard, AgentCapabilities, TextPart, TaskState, AgentSkill, Part, SecurityScheme, APIKeySecurityScheme, In
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

# Agent Card with API key security scheme
agent_card = AgentCard(
    name="Currency Agent",
    description="Get latest currency exchange rates",
    url="http://localhost:8001/a2a/",  # Use https:// in production
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="calendar_currency",
            name="calendar_currency",
            description="Check currency exchange rates",
            tags=["currency", "availability", "exchange"],
        ),
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC",
    security_schemes={
        "api-key": SecurityScheme(root=APIKeySecurityScheme(name="X-API-Key", description="API key for authentication", in_=In.header, type="apiKey"))
    },
    security=[{"api-key": []}]
)

class CAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.submit() if not context.current_task else None
        await updater.start_work()

        user_input = context.get_user_input()

        # Check if input is complete
        if " to " not in user_input:  # Simple check for currencies
            await updater.update_status(
                TaskState.input_required,
                message=updater.new_agent_message([
                    Part(root=TextPart(text="Which currencies? Like USD to EUR."))
                ]),
                final=True,
            )
        else:
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text="Checking rate..."))
                ])
            )
            await updater.add_artifact(
                [Part(root=TextPart(text="IT'S 250"))],
                name="exchange_rate"
            )
            await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(
            TaskState.failed,
            message=updater.new_agent_message([
                Part(root=TextPart(text="Task stopped."))
            ])
        )

def build_agent_server():
    # Create AgentExecutor
    executor = CAgentExecutor()

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    app = FastAPI()
    # Create A2A server with FastAPI
    agent_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    ).build()
    
    app.mount("/a2a", agent_app)

    @app.middleware("http")
    async def validate_api_key(request: Request, call_next):
        if request.url.path == "/a2a/.well-known/agent-card.json":  # Bypass for Agent Card
            return await call_next(request)
        elif request.url.path.startswith("/a2a"):  # Apply to A2A endpoints
            api_key = request.headers.get("X-API-Key")
            VALID_API_KEYS = ["secure-api-key-123"]
            print(f"🔑 API Key: {api_key}")
            if api_key not in VALID_API_KEYS:
                print(f"Invalid API key: {api_key}")
                return JSONResponse(
                    content={"error": "unauthorized", "reason": "Invalid or missing API key"},
                    status_code=401,
                    headers={"WWW-Authenticate": "ApiKey"}
                )
        return await call_next(request)
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)

if __name__ == "__main__":
    import asyncio
    asyncio.run(build_agent_server())