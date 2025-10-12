import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def setup_gemini_model():
    """Configure Gemini model using OpenAI-compatible API."""
    api_key = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    return OpenAIChatCompletionsModel(
        model="gemini-2.5-flash-lite",
        openai_client=external_client
    )


# ============================================================================
# DEMO: CUSTOMER SUPPORT AGENT
# ============================================================================

# Create Gemini model
llm_model = setup_gemini_model()

# Create support agent
base_agent = Agent(
    name="Base Assistant",
    model=llm_model
)