from agents import SQLiteSession

from a2a.types import AgentCard, AgentCapabilities, TextPart, TaskState, AgentSkill, Part
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager

from finance_advisor import finance_assistant_chat

agent_card = AgentCard(
    name="Finance Advisor Agent",
    description="Get personal finance advices and ask questions",
    url="http://localhost:8000/a2a/",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="finance_advisory",
            name="finance_advisory",
            description="Get finance advisory",
            tags=["finance", "availability", "advisory"],
        ),
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)


class FinanceAgentExecutor(AgentExecutor):
    """A2A executor that bridges A2A messages to OpenAI Agents SDK."""

    def __init__(self):
        self.memory_session: SQLiteSession | None = None
        self.context_id: str | None = None

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        print("context.context_id", context.context_id)
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        try:
            # Initialize task
            task = context.current_task
            if not task:
                await updater.submit()
            await updater.start_work()
            
            # Get user input from A2A context
            user_input = context.get_user_input()
            if self.memory_session is None or self.context_id != context.context_id:
                self.memory_session = SQLiteSession(updater.context_id, "conversations.db")

            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text="📅 checking..."))
                ])
            )

            # Use OpenAI Agents SDK to process the request
            result = await finance_assistant_chat(user_input, session=self.memory_session)
            
            print("\nA2A SERVER\n", result.final_output, "\n\n")

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="finance_advise"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"❌ Finance agent failed: {str(e)}"))])
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the current task."""
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(
            TaskState.failed,
            message=updater.new_agent_message([
                Part(root=TextPart(text="❌ Task cancelled"))
            ])
        )

# Create AgentExecutor with the OpenAI Agent
executor = FinanceAgentExecutor()

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
