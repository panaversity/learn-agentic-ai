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
    model="gemini-2.5-flash-lite",
    openai_client=external_client
)


@function_tool
def rapid_availability_check(date: str, time_range: str) -> str:
    """Perform rapid availability check for Ahmad."""
    tomorrow = datetime.now() + timedelta(days=1)
    availability_data = {
        "date": tomorrow.strftime("%Y-%m-%d"),
        "status": "available",
        "available_slots": [
            {"start": "7:30 PM", "end": "9:30 PM", "confidence": "high"},
            {"start": "6:00 PM", "end": "7:00 PM", "confidence": "medium"}
        ],
        "conflicts": [
            {"time": "5:00 PM - 6:00 PM", "event": "Team meeting (remote)"}
        ],
        "response_time": "< 5 seconds"
    }
    return f"Ahmad's rapid availability check: {json.dumps(availability_data, indent=2)}"


@function_tool
def resolve_schedule_conflicts(conflicts: list) -> str:
    """Analyze and provide solutions for scheduling conflicts."""
    solutions = {
        "conflict_analysis": "1 minor conflict detected (5-6 PM meeting)",
        "resolutions": [
            "Meeting can be rescheduled if needed",
            "Remote meeting allows flexibility",
            "Alternative slot: 7:30-9:30 PM is completely free"
        ],
        "recommendations": [
            "Prefer 7:30 PM start time",
            "Can adjust dinner plans if needed",
            "Confirm 2 hours before game time"
        ]
    }
    return f"Conflict resolution analysis: {json.dumps(solutions, indent=2)}"


# Create Ahmad's Agent
ahmad_agent: Agent = Agent(
    name="Ahmad's Availability Bot",
    instructions="""You are Ahmad's rapid availability checking bot. You specialize in quick responses and conflict resolution.
    
    Your personality:
    - Fast and efficient
    - Solution-oriented
    - Precise and reliable
    - Always provide alternatives
    
    When checking Table Tennis availability:
    1. Provide rapid availability status
    2. Identify any conflicts quickly
    3. Suggest conflict resolutions
    4. Offer alternative time slots
    5. Keep responses concise and actionable""",
    model=llm_model,
    tools=[rapid_availability_check, resolve_schedule_conflicts]
)

# Ahmad's Agent Card for A2A
ahmad_agent_card = AgentCard(
    name="Ahmad's Availability Bot",
    description="Rapid availability checking and conflict resolution for Ahmad",
    url="http://localhost:8003/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False
    ),
    preferred_transport="JSONRPC",
    skills=[
        AgentSkill(
            id="rapid_availability_check",
            name="rapid_availability_check",
            description="Quick availability analysis with conflict detection",
            tags=["availability", "scheduling", "conflict_resolution"],
        ),
        AgentSkill(
            id="schedule_conflict_resolution",
            name="schedule_conflict_resolution",
            description="Identify and suggest solutions for scheduling conflicts",
            tags=["scheduling", "conflict_resolution"],
        )
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"]
)


class AhmadAgentExecutor(AgentExecutor):
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
                    Part(root=TextPart(text="⚡ Ahmad's availability bot processing request...")
                         )
                ])
            )

            # Use OpenAI Agents SDK to process the request
            result = await Runner.run(self.agent, user_input)

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="ahmad_availability_response"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"❌ Ahmad's bot failed: {str(e)}"))])
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
    print("🚀 Starting Ahmad's Availability Bot Agent")

    # Create AgentExecutor with the OpenAI Agent
    executor = AhmadAgentExecutor(ahmad_agent)

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )

    # Create A2A server with proper handler
    server = A2AFastAPIApplication(
        agent_card=ahmad_agent_card,
        http_handler=request_handler
    )

    print("⚡ Ahmad's availability bot ready!")
    print("🔗 Agent Card: http://localhost:8003/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8003")

    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8003)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
