"""
STEP 1: Basic Agent with Tracing

Learn how to:
- Set up Langfuse for observability
- Configure Gemini as your LLM provider
- Run a simple agent with automatic tracing
- View traces in the Langfuse dashboard

This is your first step in agent evaluation!
"""

import asyncio
import os
import base64
from dotenv import load_dotenv, find_dotenv

# Import OpenAI Agents SDK components
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from langfuse import get_client
import logfire


def setup_environment():
    """
    Configure environment variables for Gemini and Langfuse.
    
    Required environment variables:
    - GEMINI_API_KEY: Your Google Gemini API key
    - LANGFUSE_PUBLIC_KEY: Langfuse public key
    - LANGFUSE_SECRET_KEY: Langfuse secret key
    """
    load_dotenv(find_dotenv())
    
    # Verify required environment variables
    required_vars = [
        "GEMINI_API_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please copy .env_backup to .env and add your API keys.\n"
            "Get Gemini key at: https://aistudio.google.com/apikey\n"
            "Get Langfuse keys at: https://cloud.langfuse.com"
        )
    
    # Set Langfuse host (default to EU region)
    os.environ.setdefault("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Build Basic Auth header for OpenTelemetry
    LANGFUSE_AUTH = base64.b64encode(
        f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
    ).decode()
    
    # Configure OpenTelemetry endpoint & headers for Langfuse
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
    
    print("✅ Environment configured successfully!")


def setup_instrumentation():
    """
    Configure Pydantic Logfire instrumentation for OpenAI Agents SDK.
    
    This automatically captures all agent interactions and sends them
    to Langfuse via OpenTelemetry (OTLP).
    """
    logfire.configure(
        service_name='agent_evaluation_step1',
        send_to_logfire=False,  # We're sending to Langfuse instead
    )
    
    # Automatically instrument the OpenAI Agents SDK
    # This patches the SDK to emit OpenTelemetry traces
    logfire.instrument_openai_agents()
    
    print("✅ Logfire instrumentation configured!")


def create_gemini_model():
    """
    Create a Gemini model client using OpenAI-compatible API.
    
    Gemini supports the OpenAI Chat Completions API format,
    so we can use it with the OpenAI Agents SDK!
    
    Returns:
        OpenAIChatCompletionsModel configured for Gemini
    """
    # 1. Create AsyncOpenAI client pointing to Gemini's endpoint
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    # 2. Wrap it in OpenAIChatCompletionsModel for use with Agents SDK
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",  # Fast and capable model
        openai_client=external_client
    )
    
    return llm_model


async def run_basic_agent_with_tracing(langfuse):
    """
    Run a simple agent with automatic tracing.
    
    This demonstrates:
    - Creating an agent with Gemini
    - Running the agent on a question
    - Automatic trace capture by Langfuse
    
    Args:
        langfuse: Langfuse client instance
    """
    print("\n" + "="*60)
    print("STEP 1: Basic Agent with Tracing")
    print("="*60)
    
    # Create Gemini model
    llm_model = create_gemini_model()
    
    # Create agent with custom instructions
    agent = Agent(
        name="EvaluationExpert",
        instructions=(
            "You are a senior AI engineer with expertise in agent evaluation and observability. "
            "Provide clear, concise answers with practical examples."
        ),
        model=llm_model
    )
    
    # Ask a question
    question = "Why is it important to evaluate AI agents in production?"
    print(f"\n📝 Question: {question}")
    
    # Run the agent (this will be automatically traced!)
    result = await Runner.run(agent, question)
    
    # Display the response
    print(f"\n💬 Agent Response:")
    print(f"{result.final_output}")
    
    # Flush to ensure traces are sent immediately
    langfuse.flush()
    
    print("\n✅ Trace sent to Langfuse!")
    print(f"   View at: {os.getenv('LANGFUSE_HOST')}/traces")


async def main():
    """
    Main function - orchestrates the entire process.
    
    Steps:
    1. Configure environment variables
    2. Set up instrumentation
    3. Initialize Langfuse client
    4. Run the agent with tracing
    """
    print("\n" + "="*60)
    print("🚀 STEP 1: BASIC AGENT WITH TRACING")
    print("="*60)
    
    # Step 1: Setup environment
    print("\n📦 Setting up environment...")
    setup_environment()
    
    # Step 2: Configure instrumentation
    print("\n� Configuring instrumentation...")
    setup_instrumentation()
    
    # Step 3: Initialize Langfuse client
    print("\n🔗 Connecting to Langfuse...")
    langfuse = get_client()
    
    # Verify authentication
    if not langfuse.auth_check():
        raise ConnectionError(
            "❌ Failed to authenticate with Langfuse.\n"
            "Please check your credentials in .env file.\n"
            "Get Langfuse keys at: https://cloud.langfuse.com"
        )
    
    print("✅ Langfuse client authenticated!")
    
    # Step 4: Run the agent with tracing
    print("\n🤖 Running agent...")
    await run_basic_agent_with_tracing(langfuse)
    
    # Final summary
    print("\n" + "="*60)
    print("✅ STEP 1 COMPLETE!")
    print("="*60)
    print("\n🎉 Congratulations! You've run your first traced agent!")
    print("\n📊 What to do next:")
    print("   1. Visit Langfuse dashboard:")
    print(f"      {os.getenv('LANGFUSE_HOST')}/traces")
    print("\n   2. Explore your trace:")
    print("      - See the LLM call to Gemini")
    print("      - Check token usage")
    print("      - View latency/timing")
    print("      - Inspect input and output")
    print("\n   3. Try modifying:")
    print("      - Change the question")
    print("      - Modify the agent instructions")
    print("      - Switch to a different Gemini model")
    print("\n   4. Move to Step 2:")
    print("      Run: uv run python 02_tool_trace.py")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
