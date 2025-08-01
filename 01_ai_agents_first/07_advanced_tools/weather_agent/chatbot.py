import chainlit as cl
from hello import run
@cl.on_chat_start
async def main():
    await cl.Message(
        content="Hello! I am a Weather chatbot. How can I assist you today?"
    ).send()



@cl.on_message

async def main(message: cl.Message):
    # Simulate a response from the chatbot
        if message:
            #   convert message to text
            print("Message",message.content)
            result = run(message.content)
        
        await cl.Message(
            content=f"{result}"
        ).send()
   