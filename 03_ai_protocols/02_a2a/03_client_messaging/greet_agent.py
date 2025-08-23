# greet_agent.py
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.utils import new_agent_text_message
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

class GreetingExecutor(AgentExecutor):
    """Agent executor that provides greeting responses."""
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Process user input and generate greeting response."""
        
        # Extract user input from the request context
        user_input = context.get_user_input()
        
        print(f"💬 Received message: '{user_input}'")
        
        # Generate personalized greeting response
        if "hello" in user_input.lower():
            response = f"👋 Hello there! You said: '{user_input}'"
        elif "goodbye" in user_input.lower():
            response = f"👋 Goodbye! Thanks for saying: '{user_input}'"
        elif "how are you" in user_input.lower():
            response = f"😊 I'm doing great! You asked: '{user_input}'"
        else:
            response = f"🤖 I received your message: '{user_input}'. Try saying hello!"
        
        # Send response back to client
        await event_queue.enqueue_event(new_agent_text_message(response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle request cancellation."""
        await event_queue.enqueue_event(new_agent_text_message("Request cancelled"))

# Define agent card with capabilities
greeting_card = AgentCard(
    name="Greeting Agent",
    description="A friendly agent that responds to greetings and messages",
    url="http://localhost:8000/",
    version="1.0.0",
    
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_transition_history=False
    ),
    
    skills=[
        AgentSkill(
            id="greeting",
            name="Greeting & Conversation",
            description="Respond to greetings and casual conversation",
            tags=["greeting", "conversation", "friendly"],
            examples=[
                "Hello!",
                "How are you?",
                "Goodbye!",
                "Hi there!"
            ]
        )
    ],
    
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    # Create and configure A2A server
    request_handler = DefaultRequestHandler(
        agent_executor=GreetingExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    server = A2AFastAPIApplication(
        agent_card=greeting_card,
        http_handler=request_handler
    )
    
    print("🤖 Starting Greeting Agent on port 8000...")
    print("🔗 Agent Card: http://localhost:8000/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8000/a2a")
    print("⚡ Ready for A2A client connections!")
    
    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8000)
