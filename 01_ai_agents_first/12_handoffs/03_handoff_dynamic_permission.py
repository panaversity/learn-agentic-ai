import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled, handoff

_ = load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


set_tracing_disabled(disabled=False)

class UserContext(BaseModel):
    user_id: str
    subscription_tier: str = "free"  # free, premium, enterprise
    has_permission: bool = False


# This agent will use the custom LLM provider
agent = Agent(
    name="Assistant",
    instructions="You only respond for the user's request and delegate to the expert agent if needed.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)

expert_agent = Agent(
    name="Expert",
    instructions="You are an expert in the field of recursion in programming.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)


agent.handoffs = [handoff(expert_agent, is_enabled=lambda ctx, agent: ctx.context.has_permission)]

async def main():
    context = UserContext(user_id="123", subscription_tier="premium", has_permission=False)

    result = await Runner.run(
        agent,
        "Call the expert agent and ask about recursion in programming",
        context=context,
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
    


