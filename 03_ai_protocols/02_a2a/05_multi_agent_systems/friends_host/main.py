import os
import httpx
import asyncio
import json

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass, field

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunContextWrapper, SQLiteSession
from a2a.types import AgentCard, AgentCapabilities, TextPart, TaskState, AgentSkill, Part, Message, Role
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, Client
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

@dataclass
class AgentInfo:
    name: str
    url: str
    port: int
    description: str = ""
    status: str = "unknown"
    agent_card: AgentCard | None = None

@dataclass
class AgentsA2ACall:
    message: str
    port: int

@dataclass
class CoordinatorContext:
    agents_by_port: dict[int, AgentInfo] = field(default_factory=dict)
    allowed_ports: list[int] = field(default_factory=lambda: [8001, 8002, 8003])

    def add_agent(self, port: int, agent_info: AgentInfo):
        """Add or update an agent in the registry by port."""
        self.agents_by_port[port] = agent_info
    
    def get_agent_by_port(self, port: int) -> AgentInfo | None:
        """Get agent by port number."""
        return self.agents_by_port.get(port)
    
    def get_all_agents(self) -> dict[int, AgentInfo]:
        """Get all agents mapped by port."""
        return self.agents_by_port.copy()
    
    def get_online_agents(self) -> dict[int, AgentInfo]:
        """Get only online agents."""
        return {port: agent for port, agent in self.agents_by_port.items() if agent.status == "online"}

 
@function_tool
async def discover_agents(context: RunContextWrapper[CoordinatorContext]) -> str:
    """Discover available A2A agents and create A2A clients for each."""
    ports = context.context.allowed_ports

    discovered = {}
    async with httpx.AsyncClient(timeout=60) as httpx_client:
        for port in ports:
            url = f"http://localhost:{port}"
            try:
                # Use A2A client to discover and connect
                resolver = A2ACardResolver(base_url=url, httpx_client=httpx_client)
                agent_card = await resolver.get_agent_card()
                                
                name = agent_card.name
                description = agent_card.description
                agent_info = AgentInfo(
                    name=name,
                    url=url,
                    port=port,
                    description=description,
                    status="online",
                    agent_card=agent_card
                )
                
                # Store in context with A2A client
                context.context.add_agent(port=port, agent_info=agent_info)

                discovered[name] = {
                    "name": name,
                    "description": description,
                    "url": url,
                    "status": "online",
                    "capabilities": agent_card.capabilities.model_dump() if agent_card.capabilities else {}
                }
                
            except Exception as e:
                discovered[url] = {"status": "error", "error": str(e), "url": url}
    
    return f"Discovered agents: {json.dumps(discovered, indent=2)}"

@function_tool
async def coordinate_agents(context: RunContextWrapper[CoordinatorContext], agent_messages: list[AgentsA2ACall]):
    """
    Send personalized messages to agents using A2A clients. 
    agent_messages: JSON string like [{"8003": "Check your calendar"}, {"8001": "Optimize schedule"}]
    """
    print(f"\n current context: ", context.context, "\n")

    responses = {}
    
    for requested_call in agent_messages:
        port = requested_call.port
        message = requested_call.message
        message_id = f"agent-{port}-{int(datetime.now().timestamp())}"
        agent_info = context.context.get_agent_by_port(port)

        if agent_info is None or agent_info.agent_card is None:
            raise ValueError(f"No agent card found for port {port}. Ensure agent is online and has a valid card.")
                
        try:
            # Create A2A message
            a2a_message = Message(
                role=Role.user,
                message_id=message_id,
                parts=[Part(root=TextPart(text=message))]
            )
            
            async with httpx.AsyncClient(timeout=120) as httpx_client:

                # Create A2A client for this agent
                client_config = ClientConfig(httpx_client=httpx_client, streaming=False)
                client: Client = ClientFactory(config=client_config).create(card=agent_info.agent_card)

                # Send message using A2A client 
                response_stream = client.send_message(a2a_message)
                
                # Collect response (since streaming=False, should get complete response)
                response_parts = []
                async for chunk in response_stream:
                    if chunk is not None:
                        # chunk is a tuple: (Task, None)
                        task = chunk[0] if isinstance(chunk, tuple) else chunk
                        if hasattr(task, 'artifacts') and task.artifacts:
                            for artifact in task.artifacts:
                                if hasattr(artifact, 'parts') and artifact.parts:
                                    for part in artifact.parts:
                                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                            response_parts.append(part.root.text)

                response_text = " ".join(response_parts) if response_parts else "No response received"

                responses[port] = {
                    "status": "success",
                    "response": response_text,
                    "agent": agent_info.name if agent_info else f"Unknown Agent on port {port}"
                }
            
        except Exception as e:
            responses[port] = {"status": "error", "error": str(e), "agent": agent_info.name if agent_info else f"Unknown Agent on port {port}"}

    return responses

@function_tool
def book_table_tennis_court(date: str, time: str, duration: str) -> str:
    """Book a Table Tennis court (simulation)."""
    booking_data = {
        "booking_id": f"TT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "court": "Court 1",
        "date": date,
        "time": time,
        "duration": duration,
        "status": "confirmed",
        "amenities": ["Paddles available", "Balls provided", "Water station nearby"]
    }
    return f"Court booking confirmed: {json.dumps(booking_data, indent=2)}"

# Create Multi-Agent Coordinator
coordinator_agent: Agent[CoordinatorContext] = Agent(
    name="Table Tennis Games Organizer",
    instructions="""You are the Table Tennis Multi-Agent Coordinator. You orchestrate scheduling between friends using port-based addressing.

    Your process:
    1. First discover available agents using discover_agents tool (no parameters needed)
    2. Send messages to specific agents using coordinate_agents tool with AgentsA2ACall objects
    3. Use port numbers to address agents: 8001, 8002, 8003
    4. Analyze responses to find optimal time slots
    5. Book the court if consensus is reached
    6. Provide a comprehensive summary

    For coordinate_agents, create AgentsA2ACall objects like:
    [
        AgentsA2ACall(message="Check your availability for tomorrow 7-9 PM", port=8001),
        AgentsA2ACall(message="What's your preferred time?", port=8002)
    ]

    Always discover agents first, then coordinate using port numbers.
    When talking with users to schedule games etc. always use agent names do not expose ports.
    """,
    model=llm_model,
    tools=[discover_agents, coordinate_agents, book_table_tennis_court]
)

# Host Agent Card for A2A
host_agent_card = AgentCard(
    name="Table Tennis Multi-Agent Coordinator",
    description="Orchestrates Table Tennis scheduling across multiple specialized agents",
    url="http://localhost:8000/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False
    ),
    skills=[
        AgentSkill(
            id="multi_agent_coordination",
            name="multi_agent_coordination",
            description="Coordinate scheduling across multiple agents simultaneously",
            tags=["coordination", "multi_agent", "scheduling"],
        ),
        AgentSkill(
            id="court_booking",
            name="court_booking",
            description="Book Table Tennis courts and manage reservations",
            tags=["booking", "reservation", "court_management"],
        ),
        AgentSkill(
            id="agent_discovery",
            name="agent_discovery",
            description="Discover and connect to available A2A agents",
            tags=["discovery", "networking", "agent_management"],
        )
    ],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

class HostAgentExecutor(AgentExecutor):
    """A2A executor that bridges A2A messages to OpenAI Agents SDK."""

    def __init__(self, agent: Agent[CoordinatorContext]):
        self.agent = agent
        self.session = SQLiteSession("my_first_conversation")
        self.coordinator_context = CoordinatorContext()

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
                    Part(root=TextPart(
                        text="🏓 Multi-Agent Coordinator orchestrating Table Tennis scheduling..."))
                ])
            )

            # Use OpenAI Agents SDK with context
            result = await Runner.run(
                self.agent, 
                user_input,
                context=self.coordinator_context,
                session=self.session
            )

            await updater.add_artifact(
                [Part(root=TextPart(text=result.final_output))],
                name="coordinator_response"
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"❌ Multi-agent coordination failed: {str(e)}"))
                ])
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
    print("🚀 Starting Table Tennis Multi-Agent Coordinator")
    
    # Create AgentExecutor with context support
    executor = HostAgentExecutor(coordinator_agent)
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    # Create A2A server
    server = A2AFastAPIApplication(
        agent_card=host_agent_card,
        http_handler=request_handler
    )
    
    print("🏓 Multi-Agent Coordinator ready!")
    print("🔗 Agent Card: http://localhost:8000/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8000")
    print("🎯 Ready to coordinate Table Tennis scheduling!")
    print("💡 Use: python cli_client.py to interact via CLI")
    
    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8000)

if __name__ == "__main__":
    asyncio.run(main())