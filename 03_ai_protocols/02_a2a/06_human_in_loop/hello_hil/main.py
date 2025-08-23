from a2a.types import AgentCard, AgentCapabilities, TextPart, TaskState, AgentSkill, Part
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager


agent_card = AgentCard(
    name="Currency Agent",
    description="Get latest currency exchange rates",
    url="http://localhost:8001/",
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
    preferred_transport="JSONRPC"
)


class CAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.submit() if not context.current_task else None
        await updater.start_work()

        user_input = context.get_user_input()

        # # Check if input is complete
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
    # Create AgentExecutor with the OpenAI Agent
    executor = CAgentExecutor()

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    # Create A2A server with proper handler
    agent_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    ).build()
    
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(agent_app, host="localhost", port=8001)

if __name__ == "__main__":
    import asyncio
    asyncio.run(build_agent_server())