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
    model="gemini-2.0-flash",
    openai_client=external_client
)


@function_tool
def check_calendar_availability(date: str, time_slot: str) -> str:
    """Check Ameen's calendar availability for a specific date and time."""
    # Simulate calendar data
    tomorrow = datetime.now() + timedelta(days=1)
    calendar_data = {
        "date": tomorrow.strftime("%Y-%m-%d"),
        "busy_slots": [
            {"start": "2:00 PM", "end": "3:30 PM", "event": "Doctor appointment"},
            {"start": "5:00 PM", "end": "6:00 PM", "event": "Team standup"}
        ],
        "available_slots": [
            {"start": "7:00 PM", "end": "9:00 PM", "preference": "high"},
            {"start": "8:00 PM", "end": "10:00 PM", "preference": "medium"}
        ]
    }
    return f"Ameen's availability for {date}: {json.dumps(calendar_data, indent=2)}"


@function_tool
def get_personal_preferences() -> str:
    """Get Ameen's personal preferences for Table Tennis."""
    preferences = {
        "preferred_times": ["evening", "7-9 PM"],
        "skill_level": "intermediate",
        "equipment": "brings own paddle",
        "availability_notice": "prefers 2+ hours advance notice"
    }
    return f"Ameen's Table Tennis preferences: {json.dumps(preferences, indent=2)}"


# Create Ameen's Agent
ameen_agent: Agent = Agent(
    name="Ameen's Calendar Agent",
    instructions="""You are Ameen's personal calendar assistant. You help coordinate his schedule for Table Tennis games.
    
    Your personality:
    - Friendly and organized
    - Always check calendar conflicts
    - Provide clear availability windows
    - Mention any scheduling preferences
    
    When asked about Table Tennis availability:
    1. Check calendar for conflicts
    2. Suggest best available time slots
    3. Include personal preferences
    4. Be specific about times and dates""",
    model=llm_model,
    tools=[check_calendar_availability, get_personal_preferences]
)

# Ameen's Agent Card for A2A
ameen_agent_card = AgentCard(
    name="Ameen's Personal Calendar Agent",
    description="Personal calendar management and scheduling coordination for Ameen",
    url="http://localhost:8001/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False
    ),
    skills=[
        AgentSkill(
            id="calendar_availability_check",
            name="calendar_availability_check",
            description="Check personal calendar for conflicts and availability",
            tags=["calendar", "availability", "scheduling"],
        ),
        AgentSkill(
            id="scheduling_preferences",
            name="scheduling_preferences",
            description="Provide personal scheduling preferences and constraints",
            tags=["preferences", "scheduling"],
        )
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)


class AmeenAgentExecutor(AgentExecutor):
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
                    Part(root=TextPart(text="📅 Ameen's calendar agent checking availability...")
                         )
                ])
            )

            # Use OpenAI Agents SDK to process the request
            result = await Runner.run(self.agent, user_input)

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="ameen_calendar_response"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"❌ Ameen's calendar agent failed: {str(e)}"))])
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
    print("🚀 Starting Ameen's Personal Calendar Agent")

    # Create AgentExecutor with the OpenAI Agent
    executor = AmeenAgentExecutor(ameen_agent)

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )

    # Create A2A server with proper handler
    server = A2AFastAPIApplication(
        agent_card=ameen_agent_card,
        http_handler=request_handler
    )

    print("📅 Ameen's calendar agent ready!")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8001)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())