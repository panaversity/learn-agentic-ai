import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
from agents.extensions.memory.redis_session import RedisSession

set_tracing_disabled(True)  # Disable tracing 

# Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)

model = OpenAIChatCompletionsModel(model = "gemini-2.5-flash", openai_client = external_client)

# create a session
# Get Redis URL from Redis Cloud
redis_url = "redis://username:password@hostname:port"  # Replace with your actual Redis URL
session = RedisSession.from_url(session_id="user-123", url=redis_url)

agent = Agent(name="Assistant", instructions="You are helpful assistant", model=model)

async def main():
    try:
        # Use persistent session
        result1 = await Runner.run(
            agent,
            input="my name is XYZ",
            session=session
        )
        print(result1.final_output)

        result2 = await Runner.run(
            agent,
            input="do u know my name",
            session=session
        )
        print(result2.final_output)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # close the session
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())