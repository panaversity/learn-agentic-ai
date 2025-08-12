from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, Runner
from agents.run import AgentRunner, set_default_agent_runner

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key="mock_api",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

class CustomAgentRunner(AgentRunner):
    async def run(self, starting_agent, input, **kwargs):
        print("Custom logic before running the agent...")
        # Call parent with custom logic
        # result = await super().run(starting_agent, input, **kwargs)
        return "Agent have entered sleeping mode and will not respond to any messages."

set_default_agent_runner(CustomAgentRunner())

sleeping_agent = Agent(
    name="SleepingAssistant",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)
    
async def run_sleeping_agent(message: str):
    return await Runner.run(sleeping_agent, message)

# This is for Testing only
if __name__ == "__main__":
    import asyncio
    response = asyncio.run(run_sleeping_agent("Hello, how are you?"))
    print("TEST RES:", response)  # Should print the custom response from the sleeping agent
    

