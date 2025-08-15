import os
from fastapi import FastAPI

from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, SQLiteSession

from a2a.types import AgentCard, AgentCapabilities, TextPart, TaskState, AgentSkill, Part
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Create Agent
currency_agent: Agent = Agent(
    name="Currency Agent",
    instructions="""You are Currency assistant. You help coordinate currency exchange rates.""",
    model=llm_model,
)

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


class AmeenAgentExecutor(AgentExecutor):
    """A2A executor that bridges A2A messages to OpenAI Agents SDK."""

    def __init__(self, agent: Agent):
        self.agent = agent
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
                    Part(root=TextPart(text="📅 Ameen's calendar agent checking availability..."))
                ])
            )

            # Use OpenAI Agents SDK to process the request
            result = await Runner.run(self.agent, user_input, session=self.memory_session)

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="currency_response"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"❌ Currency agent failed: {str(e)}"))])
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

def build_agent_server():
    # Create AgentExecutor with the OpenAI Agent
    executor = AmeenAgentExecutor(currency_agent)

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
    
    return agent_app

app = FastAPI()
app.mount("/", build_agent_server())

def main():
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())