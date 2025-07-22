import chainlit as cl


@cl.on_chat_start
async def start():
    await cl.Message("How can I help you today?").send()


@cl.on_message
async def main(message: str):
    # Simple echo bot - replace with your LLM/agent logic
    response = f"You said: {message}"
    await cl.Message(response).send()
