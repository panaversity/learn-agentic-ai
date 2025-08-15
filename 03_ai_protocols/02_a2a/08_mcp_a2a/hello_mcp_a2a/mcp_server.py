import logging
import os

from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv, find_dotenv
from agents import Runner

from currency_exchange_agent import currency_assistant

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Create and Configure the FastMCP Application ---
mcp_app = FastMCP(
    name="SharedStandAloneMCPServer",
    stateless_http=True,
    json_response=True, # Generally easier for HTTP clients if they don't need full SSE parsing
)

# --- 2. Define a simple tool ---
@mcp_app.tool(
    name="exchange_officer",
    description="Exchange officer at currency exchange agentic system to answer all exchange related questions and currency exchange rates."
)
async def ask_exchange_officer(question: str) -> str:
    """A simple greeting tool."""

    # Use OpenAI Agents SDK to process the request
    result = await Runner.run(currency_assistant, question)

    print( "MCP SERVER\n\n", result.final_output, "\n\n")
    return result.final_output

mcp_app_instance = mcp_app.streamable_http_app()
