import asyncio
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class EnhancedAgent:
    """Enhanced agent that processes actual user messages."""

    async def invoke(self, message: str) -> str:
        """Process a message and return response."""
        logger.info(f"Agent processing message: {message}")

        # Simulate some processing time
        await asyncio.sleep(0.5)

        # Different responses based on input
        if "hello" in message.lower():
            return "Hello! Nice to meet you through the A2A protocol!"
        elif "time" in message.lower():
            return "I don't have access to real time, but I can process your requests!"
        elif "error" in message.lower():
            raise Exception("Simulated error for testing error handling")
        else:
            return f"I received your message: '{message}'. How can I help you?"


class EnhancedAgentExecutor(AgentExecutor):
    """
    Enhanced Agent Executor that processes actual user input.

    Key improvements over official example:
    1. Extracts user message from RequestContext
    2. Processes the actual message content
    3. Detailed logging for learning
    4. Error handling
    """

    def __init__(self):
        self.agent = EnhancedAgent()
        logger.info("Enhanced AgentExecutor initialized")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Enhanced execution with message processing.
        """
        logger.info("=== Enhanced AgentExecutor.execute() called ===")

        # Extract message from RequestContext
        user_message = self._extract_message_from_context(context)
        logger.info(f"Extracted user message: {user_message}")

        # Log context details for learning
        self._log_context_details(context)

        try:
            # Process with enhanced agent
            logger.info("Calling enhanced agent.invoke()...")
            result = await self.agent.invoke(user_message)
            logger.info(f"Agent returned: {result}")

            # Enqueue the response
            logger.info("Enqueueing response to EventQueue...")
            await event_queue.enqueue_event(new_agent_text_message(result))
            logger.info("✅ Response successfully enqueued!")

        except Exception as e:
            # Handle errors gracefully
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error(error_msg)
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """Enhanced cancel with proper response."""
        logger.info("=== Enhanced AgentExecutor.cancel() called ===")
        cancel_msg = "Agent execution was cancelled"
        await event_queue.enqueue_event(new_agent_text_message(cancel_msg))

    def _extract_message_from_context(self, context: RequestContext) -> str:
        """Extract user message from RequestContext."""
        logger.info(f"Extracting message from RequestContext: {context}")

        if not context.message:
            logger.warning("No message in context")
            return "No message found"

        logger.info(f"Message: {context.message}")

        # Safe logging of message parts
        try:
            logger.info(f"Message Parts: {context.message.dict()}")
        except Exception as e:
            logger.warning(f"Could not serialize message: {e}")

        if context.message.parts:
            for i, part in enumerate(context.message.parts):
                logger.info(f"Part {i}: {type(part).__name__}")
                logger.info(f"Part {i} attributes: {dir(part)}")

                # Try different ways to access the text based on A2A SDK structure
                try:
                    # Method 1: Direct access to root.text (based on logs showing Part(root=TextPart(...)))
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        logger.info(
                            f"Found text via part.root.text: {part.root.text}")
                        return part.root.text

                    # Method 2: Direct text attribute
                    elif hasattr(part, 'text'):
                        logger.info(f"Found text via part.text: {part.text}")
                        return part.text

                    # Method 3: Check if it's a dict-like structure
                    elif hasattr(part, 'get') and part.get('text'):
                        logger.info(
                            f"Found text via part.get('text'): {part.get('text')}")
                        return part.get('text')

                    else:
                        logger.info(f"Part {i} structure: {part}")

                except Exception as e:
                    logger.error(f"Error accessing part {i}: {e}")
                    continue

        logger.warning("No text found in message parts")
        return "No message found"

    def _log_context_details(self, context: RequestContext):
        """Log RequestContext details for learning purposes."""
        logger.info("--- RequestContext Details ---")
        logger.info(
            f"Message ID: {context.message.messageId if context.message else 'None'}")
        logger.info(
            f"Message Role: {context.message.role if context.message else 'None'}")
        logger.info(
            f"Message Parts Count: {len(context.message.parts) if context.message and context.message.parts else 0}")
        logger.info(f"Task ID: {context.task_id}")
        logger.info("-----------------------------")
