import os
import chainlit as cl
from typing import cast
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, RunContextWrapper, AsyncOpenAI, OpenAIChatCompletionsModel

load_dotenv()

def setup_config():
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=external_client,
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Setup Agents
    spanish_agent = Agent(
        name="spanish_agent",
        instructions="You translate the user's message to Spanish",
        handoff_description="An english to spanish translator",
        model=model
    )

    french_agent = Agent(
        name="french_agent",
        instructions="You translate the user's message to French",
        handoff_description="An english to french translator",
        model=model
    )

    italian_agent = Agent(
        name="italian_agent",
        instructions="You translate the user's message to Italian",
        handoff_description="An english to italian translator",
        model=model
    )

    # triage Agent
    triage_agent = Agent(
        name="triage_agent",
        instructions=(
            "You are a translation agent. You use the tools given to you to translate."
            "If asked for multiple translations, you call the relevant tools in order."
            "You never translate on your own, you always use the provided tools."
        ),
        tools=[
            spanish_agent.as_tool(
                tool_name="translate_to_spanish",
                tool_description="Translate the user's message to Spanish",
            ),
            french_agent.as_tool(
                tool_name="translate_to_french",
                tool_description="Translate the user's message to French",
            ),
            italian_agent.as_tool(
                tool_name="translate_to_italian",
                tool_description="Translate the user's message to Italian",
            ),
        ],
        model=model
    )
    
    return triage_agent, config


@cl.on_chat_start
async def start():
    triage_agent, config = setup_config()
    cl.user_session.set("triage_agent", triage_agent)
    cl.user_session.set("config", config)
    cl.user_session.set("chat_history", [])
    await cl.Message(content="Welcome to the Panaversity AI Assistant!").send()


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    # Send a thinking message
    msg = cl.Message(content="Thinking...")
    await msg.send()
    
    triage_agent = cast(Agent, cl.user_session.get("triage_agent"))
    config = cast(RunConfig, cl.user_session.get("config"))

    # Retrieve the chat history from the session.
    history = cl.user_session.get("chat_history") or []

    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})

    result = await Runner.run(triage_agent, history, run_config=config)

    response_content = result.final_output

    # Update the thinking message with the actual response
    msg.content = response_content
    await msg.update()

    history.append({"role": "assistant", "content": response_content})

    cl.user_session.set("chat_history", history)

    print(f"History: {history}")
