#  0. Importing the necessary libraries
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI

import os
from dotenv import load_dotenv, find_dotenv

# 0.1. Loading the environment variables
load_dotenv(find_dotenv())

# 1. Which LLM Provider to use? -> Google Chat Completions API Service
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model to use?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# 3. Creating the Agent
agent: Agent = Agent(name="Assistant", model=llm_model)

# 4. Running the Agent
result = Runner.run_sync(starting_agent=agent, input="Welcome and motivate me to learn Agentic AI")

print("AGENT RESPONSE: " , result.final_output)