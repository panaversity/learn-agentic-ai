import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # Our custom logic goes here...
    # Send a fake response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()