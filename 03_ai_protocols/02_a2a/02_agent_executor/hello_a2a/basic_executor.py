# basic_executor.py
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from basic_agent import run_sleeping_agent

class SimpleCalendarExecutor(AgentExecutor):
    """Agent Executor - handles A2A protocol."""
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        This is THE method that bridges A2A → Your Agent
        
        Flow:
        1. Extract user input from A2A request
        2. Route to appropriate agent method
        3. Get result from agent
        4. Send response via A2A protocol
        """
        
        # Step 1: Get user input from A2A request
        user_input = context.get_user_input()
        
        result = await run_sleeping_agent(user_input)
        
        # Step 3: Send response back through A2A
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle request cancellation."""
        await event_queue.enqueue_event(new_agent_text_message("Request cancelled"))