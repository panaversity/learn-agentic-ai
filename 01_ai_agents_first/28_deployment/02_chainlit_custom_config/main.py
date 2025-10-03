import os
from typing import Dict
from dotenv import load_dotenv
import chainlit as cl
from openai import OpenAI
from chainlit.types import AskFileResponse

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history
conversation_history: Dict[str, list] = {}

@cl.on_chat_start
async def start_chat():
    """
    Initialize the chat session with custom settings and welcome message.
    """
    # Initialize conversation history for this session
    conversation_history[cl.user_session.get("id")] = []
    
    # Set custom chat settings
    cl.user_session.set("model", "gpt-3.5-turbo")
    
    # Send welcome message with custom elements
    elements = [
        cl.Image(name="logo", 
                display="inline", 
                path="https://raw.githubusercontent.com/Chainlit/chainlit/main/logo.png")
    ]
    
    await cl.Message(
        content="Welcome to CustomAI Chat! How can I assist you today?",
        elements=elements
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages with enhanced features.
    """
    # Get session ID
    session_id = cl.user_session.get("id")
    
    # Update conversation history
    conversation_history[session_id].append({
        "role": "user",
        "content": message.content
    })
    
    try:
        # Create chat completion with history
        response = client.chat.completions.create(
            model=cl.user_session.get("model"),
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
        
        # Update conversation history with assistant's response
        conversation_history[session_id].append({
            "role": "assistant",
            "content": msg.content
        })
        
        # Send the final message
        await msg.send()
        
    except Exception as e:
        # Handle errors gracefully
        await cl.Message(
            content=f"An error occurred: {str(e)}",
            author="Error"
        ).send()

@cl.on_settings_update
async def setup_agent(settings):
    """
    Handle settings updates from the UI.
    """
    # Update model selection
    cl.user_session.set("model", settings.get("model", "gpt-3.5-turbo"))
    
    await cl.Message(
        content=f"Settings updated! Now using model: {settings.get('model')}"
    ).send()

@cl.on_chat_end
async def end_chat():
    """
    Clean up when chat ends.
    """
    # Clear conversation history for this session
    session_id = cl.user_session.get("id")
    if session_id in conversation_history:
        del conversation_history[session_id] 