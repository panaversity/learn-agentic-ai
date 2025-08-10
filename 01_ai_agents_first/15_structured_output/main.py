import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, ModelSettings, function_tool

# 🌿 Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
llm_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)


from pydantic import BaseModel
from agents import Agent, Runner

# Define your data structure
class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

# Create agent with structured output
agent = Agent(
    name="InfoCollector",
    instructions="Extract person information from the user's message.",
    output_type=PersonInfo  # This is the magic!
)

async def main():
    result = await Runner.run(
        agent,
        "Hi, I'm Alice, I'm 25 years old and I work as a teacher."
    )

    # Now you get perfect structured data!
    print("Type:", type(result.final_output))        # <class 'PersonInfo'>
    print("Name:", result.final_output.name)         # "Alice"
    print("Age:", result.final_output.age)           # 25
    print("Job:", result.final_output.occupation)    # "teacher"


if __name__ == "__main__":
    asyncio.run(main())
