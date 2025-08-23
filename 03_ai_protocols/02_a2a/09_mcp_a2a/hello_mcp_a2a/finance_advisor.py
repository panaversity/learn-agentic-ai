import os

from dotenv import load_dotenv, find_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

MCP_SERVER_URL = "http://localhost:8000/exchange/mcp" # Ensure this matches your running server

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Create Agent
finance_assistant: Agent = Agent(
    name="FinanceAdvisory",
    instructions="""You are Finance Advisor assistant. You can coordinate with exchange officer for all exchange related questions and currency exchange rates. Always answer to the best of your abilities.""",
    model=llm_model,
)


async def finance_assistant_chat(messages, session):
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL, timeout=300)
    async with MCPServerStreamableHttp(params=mcp_params, name="Test", cache_tools_list=True) as exchange_mcp_conn:
        try:
            assistant = Agent(
                name="Finance Advisor Agent",
                instructions="""You are Finance Advisor assistant. You can coordinate with exchange officer for all exchange related questions and currency exchange rates. Always answer to the best of your abilities.""",
                model=llm_model,
                mcp_servers=[exchange_mcp_conn]
            )

            result = await Runner.run(assistant, messages, session=session)
            return result

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")

