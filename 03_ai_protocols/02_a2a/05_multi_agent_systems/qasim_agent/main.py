import os
import json

from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool

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
    model="gemini-2.5-flash",
    openai_client=external_client
)


@function_tool
def analyze_schedule_optimization(date: str, participants: list) -> str:
    """Analyze and optimize scheduling for multiple participants."""
    tomorrow = datetime.now() + timedelta(days=1)
    optimization_data = {
        "date": tomorrow.strftime("%Y-%m-%d"),
        "optimal_slots": [
            {"time": "8:00 PM - 9:30 PM", "efficiency_score": 0.95, "reason": "Peak availability for all"},
            {"time": "7:30 PM - 9:00 PM", "efficiency_score": 0.87, "reason": "Good for most participants"}
        ],
        "schedule_conflicts": ["5:00-6:00 PM: Multiple conflicts detected"],
        "recommendations": [
            "Book 90-minute slot for proper game time",
            "Send confirmations 2 hours before",
            "Consider backup time slot"
        ]
    }
    return f"Schedule optimization analysis: {json.dumps(optimization_data, indent=2)}"


@function_tool
def get_time_management_insights() -> str:
    """Provide time management insights for Table Tennis scheduling."""
    insights = {
        "best_practices": [
            "Evening slots (7-9 PM) have highest participation",
            "90 minutes allows for warm-up and cool-down",
            "Friday evenings are most popular"
        ],
        "efficiency_tips": [
            "Block recurring slots for regular games",
            "Use group calendar for transparency",
            "Set up automated reminders"
        ]
    }
    return f"Time management insights: {json.dumps(insights, indent=2)}"


# Create Qasim's Agent
qasim_agent: Agent = Agent(
    name="Qasim's Schedule Manager",
    instructions="""You are Qasim's schedule management specialist. You excel at optimizing time slots and coordinating group activities.
    
    Your personality:
    - Analytical and efficient
    - Focus on optimization and productivity
    - Provide data-driven recommendations
    - Consider all participants' needs
    
    When coordinating Table Tennis:
    1. Analyze optimal time slots
    2. Consider schedule efficiency
    3. Provide backup options
    4. Suggest time management best practices""",
    model=llm_model,
    tools=[analyze_schedule_optimization, get_time_management_insights]
)

# Qasim's Agent Card for A2A
qasim_agent_card = AgentCard(
    name="Qasim's Schedule Manager Agent",
    description="Schedule optimization and time management coordination for Qasim",
    url="http://localhost:8002/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False
    ),
    skills=[
        AgentSkill(
            id="schedule_optimization",
            name="schedule_optimization",
            description="Analyze and optimize scheduling for multiple participants",
            tags=["optimization", "scheduling", "efficiency"],
        ),
        AgentSkill(
            id="time_management",
            name="time_management",
            description="Provide time management insights and efficiency recommendations",
            tags=["time_management", "insights", "best_practices"],
        )
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC",
)


class QasimAgentExecutor(AgentExecutor):
    """A2A executor that bridges A2A messages to OpenAI Agents SDK."""

    def __init__(self, agent: Agent):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        try:
            # Initialize task
            if not context.current_task:
                await updater.submit()
            await updater.start_work()

            # Get user input from A2A context
            user_input = context.get_user_input()

            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text="📊 Qasim's schedule manager analyzing optimization...")
                         )
                ])
            )

            # Use OpenAI Agents SDK to process the request
            result = await Runner.run(self.agent, user_input)

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="qasim_schedule_response"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"❌ Qasim's schedule manager failed: {str(e)}"))])
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
        
def main():
    print("🚀 Starting Qasim's Schedule Manager Agent")

    # Create AgentExecutor with the OpenAI Agent
    executor = QasimAgentExecutor(qasim_agent)

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )

    # Create A2A server with proper handler
    server = A2AFastAPIApplication(
        agent_card=qasim_agent_card,
        http_handler=request_handler
    )

    print("📊 Qasim's schedule manager ready!")
    print("🔗 Agent Card: http://localhost:8002/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8002")

    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8002)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())