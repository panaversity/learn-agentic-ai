import os
from dotenv import load_dotenv
import chainlit as cl
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@cl.on_chat_start
def start_chat():
    """
    Initialize the chat session.
    """
    cl.Message(
        content="Hello! I'm running in a Docker container. How can I help you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages.
    """
    try:
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": message.content}
            ],
            stream=True
        )

        # Create a Chainlit message for streaming
        msg = cl.Message(content="")
        
        # Stream the response
        for chunk in response:
            if chunk.choices[0].delta.content:
                await msg.stream_token(chunk.choices[0].delta.content)
        
        # Send the final message
        await msg.send()
        
    except Exception as e:
        await cl.Message(
            content=f"Error: {str(e)}",
            author="Error"
        ).send() 