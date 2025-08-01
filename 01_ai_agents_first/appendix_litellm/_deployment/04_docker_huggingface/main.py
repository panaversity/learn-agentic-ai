import os
import logging
from typing import Dict
from dotenv import load_dotenv
import chainlit as cl
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history
conversation_history: Dict[str, list] = {}

@cl.on_chat_start
async def start_chat():
    """
    Initialize the chat session with production settings.
    """
    try:
        # Initialize conversation history
        session_id = cl.user_session.get("id")
        conversation_history[session_id] = []
        
        # Log session start
        logger.info(f"Starting new chat session: {session_id}")
        
        # Send welcome message
        await cl.Message(
            content="Welcome to the Production Chainlit Bot! How can I assist you today?"
        ).send()
        
    except Exception as e:
        logger.error(f"Error in chat initialization: {str(e)}")
        await cl.Message(
            content="An error occurred during initialization. Please try again.",
            author="Error"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages with production-grade error handling and logging.
    """
    try:
        # Get session ID
        session_id = cl.user_session.get("id")
        logger.info(f"Processing message for session {session_id}")
        
        # Update conversation history
        conversation_history[session_id].append({
            "role": "user",
            "content": message.content
        })
        
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                *conversation_history[session_id]
            ],
            stream=True
        )

        # Create a Chainlit message for streaming
        msg = cl.Message(content="")
        
        # Stream the response
        for chunk in response:
            if chunk.choices[0].delta.content:
                await msg.stream_token(chunk.choices[0].delta.content)
        
        # Update conversation history
        conversation_history[session_id].append({
            "role": "assistant",
            "content": msg.content
        })
        
        # Send the final message
        await msg.send()
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await cl.Message(
            content=f"An error occurred: {str(e)}",
            author="Error"
        ).send()

@cl.on_chat_end
async def end_chat():
    """
    Clean up when chat ends and log session completion.
    """
    try:
        session_id = cl.user_session.get("id")
        if session_id in conversation_history:
            del conversation_history[session_id]
            logger.info(f"Chat session ended and cleaned up: {session_id}")
    except Exception as e:
        logger.error(f"Error in chat cleanup: {str(e)}")

# Health check endpoint
@cl.on_health_check
async def health_check():
    """
    Verify the application's health status.
    """
    try:
        # Check OpenAI API connection
        client.models.list(limit=1)
        return True
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False 