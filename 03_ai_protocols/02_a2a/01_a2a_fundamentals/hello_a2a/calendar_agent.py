from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.utils import new_agent_text_message
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, AgentProvider

# 🎯 CONCEPT 1: Agent Business Logic (Your Core Functionality)
class CalendarAgent:
    """
    This is YOUR agent's brain - the actual business logic.
    Think of this as the 'worker' that does the real tasks.
    """
    async def invoke(self, message) -> str:
        """Invoke the Agent"""
        return "Not taking any task"
    
# 🎯 CONCEPT 2: Agent Executor (A2A Protocol Bridge)
class CalendarAgentExecutor(AgentExecutor):
    """
    This is the A2A protocol handler - it connects A2A messages 
    to your agent's business logic. Think of it as a 'translator'.
    """
    
    def __init__(self):
        self.agent = CalendarAgent()  # Connect to your business logic
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        This method receives A2A requests and calls your agent methods.
        In a real implementation, you'd parse the request and route to appropriate methods.
        """
        # Demo: Show how agent processes a request
        result = await self.agent.invoke(context.get_user_input())
        
        # Send response back through A2A protocol
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle request cancellation."""
        raise Exception('cancel not supported in this example')
    
# 🎯 CONCEPT 3: Agent Skills (What You Advertise to Others)
calendar_skills = [
    AgentSkill(
        id="check_availability",           # Unique identifier
        name="Check Availability",        # Human-readable name
        description="Check free time slots for given dates and times",  # What it does
        tags=["calendar", "availability", "scheduling"],  # Categories for discovery
        examples=[  # Help other agents/users understand usage
            "Am I free tomorrow at 3 PM?",
            "What's my availability this week?",
            "Check if Tuesday afternoon is open"
        ]
    ),
    AgentSkill(
        id="schedule_meeting",
        name="Schedule Meeting",
        description="Schedule new meetings and send invitations",
        tags=["calendar", "meeting", "scheduling"],
        examples=[
            "Schedule a team meeting for Friday at 2 PM",
            "Book a 1-hour call with John next Tuesday",
            "Set up a project review meeting"
        ]
    ),
    AgentSkill(
        id="find_conflicts",
        name="Find Conflicts",
        description="Identify scheduling conflicts and suggest alternatives",
        tags=["calendar", "conflicts", "optimization"],
        examples=[
            "Check for conflicts in my schedule this week",
            "Find overlapping meetings",
            "Analyze my calendar for double-bookings"
        ]
    )
]

# 🎯 CONCEPT 4: Agent Card (Your Digital Business Card)
calendar_agent_card = AgentCard(
    # Basic Identity
    name="Personal Calendar Agent",
    description="Manages scheduling, availability, and calendar coordination using A2A SDK",
    url="http://localhost:8001/mcp",        # Where to find this agent
    version="1.0.0",                     # Version for compatibility

    # Provider Information (Who built this agent)
    provider=AgentProvider(
        organization="A2A Learning Lab",
        url="https://github.com/a2a-learning"
    ),

    # Communication Formats (What languages this agent speaks)
    default_input_modes=["text/plain", "application/json"],   # What it can receive
    default_output_modes=["application/json", "text/plain"],  # What it can send

    # Technical Capabilities (Advanced features)
    capabilities=AgentCapabilities(
        streaming=False,                 # Can send real-time updates?
        push_notifications=True,          # Can send alerts?
        state_transition_history=False     # Tracks conversation history?
    ),

    # Available Skills (What this agent can do)
    skills=calendar_skills,
    
    preferred_transport="JSONRPC"
)

# 🎯 CONCEPT 5: A2A Server (The Official Protocol Implementation)
if __name__ == "__main__":
    # Create the request handler with your executor
    request_handler = DefaultRequestHandler(
        agent_executor=CalendarAgentExecutor(),  # Your agent logic
        task_store=InMemoryTaskStore(),          # Memory for tasks
        queue_manager=InMemoryQueueManager()
    )

    # Create the A2A-compliant server
    server = A2AFastAPIApplication(
        agent_card=calendar_agent_card,  # Your agent's business card
        http_handler=request_handler     # Your request processor
    )

    # Start the server with helpful information
    print("🗓️ Starting Calendar Agent on port 8001...")
    print("📋 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("🔗 A2A Endpoint: http://localhost:8001/a2a")
    print("🛠️ Skills Available:", [skill.id for skill in calendar_skills])
    print("\n💡 Try: curl http://localhost:8001/.well-known/agent-card.json")
    
    import uvicorn
    from fastapi import FastAPI
    
    app: FastAPI = server.build()

    uvicorn.run(server.build(), host="localhost", port=8001)