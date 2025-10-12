import os
import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel

from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

def setup_gemini_model():
    """Configure Gemini model using OpenAI-compatible API."""
    api_key = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    return OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=external_client
    )

async def main():
    # In your application, you would use your existing engine
    # Get DB URL from NEON Postgres DB
    engine = create_async_engine("postgresql+asyncpg://neondb_owner:npg_iQ1sYWIyza0f@ep-blue-pine-ad0c0yu7-pooler.c-2.us-east-1.aws.neon.tech/hello_agent?ssl=require")

    llm_model = setup_gemini_model()

    agent = Agent("Assistant", model=llm_model)
    session = SQLAlchemySession(
        "muhammad",
        engine=engine,
        create_tables=True,  # Auto-create tables for the demo
    )

    result = await Runner.run(agent, "What did I just ask?", session=session)
    print(result.final_output)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())