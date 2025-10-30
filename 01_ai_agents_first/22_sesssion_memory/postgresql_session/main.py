from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Retrieve the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the external client
externel_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Initialize the model
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash", openai_client=externel_client
)

# Initialize the agent
agent = Agent(name="Assistant Agent", model=model)

# The PostgreSQL connection string using the asyncpg driver
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")

# Create a clean URL without the problematic keywords
CLEAN_DB_URL = POSTGRES_DB_URL.split("?")[0]

# Create an async SQLAlchemy engine with the SSL configuration
# The `connect_args` dictionary passes the `ssl` parameter to asyncpg
engine = create_async_engine(CLEAN_DB_URL, connect_args={"ssl": "require"})

# Create a session using SQLAlchemySession, passing the engine
session = SQLAlchemySession("conversation_123", engine=engine, create_tables=True)

print("--- Running first query with PostgreSQL session ---")
result1 = Runner.run_sync(
    agent, "What city is the Golden Gate Bridge in?", session=session
)
print("Agent 01 :", result1.final_output)

print("\n--- Running second query with PostgreSQL session ---")
# The session object remembers the previous turn
result2 = Runner.run_sync(agent, "What state is it in?", session=session)
print("Agent 02 :", result2.final_output)
