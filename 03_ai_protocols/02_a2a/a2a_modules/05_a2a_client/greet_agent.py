import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class GreetingAgent:
    """A greeting agent that responds to user messages contextually."""

    async def invoke(self, message: str = "") -> str:
        """Process user input and return appropriate greeting."""
        logger.info(f"GreetingAgent processing: '{message}'")
        
        if not message or message == "No message found":
            return 'Hello! How can I help you today?'
        
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return f'Hello there! You said: "{message}"'
        elif "goodbye" in message_lower or "bye" in message_lower:
            return f'Goodbye! Thanks for chatting: "{message}"'
        elif "how are you" in message_lower:
            return "I'm doing great! Thanks for asking. How can I assist you?"
        else:
            return f'I heard you say: "{message}". How can I assist you?'


class GreetingAgentExecutor(AgentExecutor):
    """
    Agent Executor that properly extracts and processes user messages.
    
    Uses the corrected message extraction pattern from Step 04.
    """

    def __init__(self):
        self.agent = GreetingAgent()
        logger.info("GreetingAgentExecutor initialized")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute with proper message extraction and processing."""
        logger.info("=== GreetingAgentExecutor.execute() called ===")
        
        # Extract user message using corrected pattern from Step 04
        user_message = self._extract_message_from_context(context)
        logger.info(f"Extracted user message: '{user_message}'")
        
        try:
            # Process with greeting agent
            result = await self.agent.invoke(user_message)
            logger.info(f"Agent response: '{result}'")
            
            # Send response via event queue
            await event_queue.enqueue_event(new_agent_text_message(result))
            logger.info("✅ Response enqueued successfully")
            
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error(error_msg)
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle cancellation requests."""
        logger.info("=== GreetingAgentExecutor.cancel() called ===")
        cancel_msg = "Operation was cancelled"
        await event_queue.enqueue_event(new_agent_text_message(cancel_msg))

    def _extract_message_from_context(self, context: RequestContext) -> str:
        """
        Extract user message from RequestContext.
        
        Uses the corrected pattern from Step 04:
        A2A SDK structure: Part(root=TextPart(text='hello'))
        """
        if not context.message:
            return "No message found"
            
        if context.message.parts:
            for part in context.message.parts:
                # Method 1: A2A SDK structure: Part(root=TextPart(text='hello'))
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    return part.root.text
                # Method 2: Direct text attribute fallback
                elif hasattr(part, 'text'):
                    return part.text
        
        return "No message found"
