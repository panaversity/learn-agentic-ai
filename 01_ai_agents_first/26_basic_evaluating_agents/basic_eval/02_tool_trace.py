"""
STEP 2: Agent with Tools and Tracing

Learn how to:
- Add function tools to your agent
- See tool calls in the trace
- Monitor multi-step agent execution
- Track which tools are used and when

This builds on Step 1 by adding tool capabilities!
"""

import asyncio
import os
import base64
from dotenv import load_dotenv, find_dotenv

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from langfuse import get_client
import logfire


def setup_environment():
    """Configure environment variables."""
    load_dotenv(find_dotenv())
    
    required_vars = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing: {', '.join(missing_vars)}")
    
    os.environ.setdefault("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    LANGFUSE_AUTH = base64.b64encode(
        f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
    ).decode()
    
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
    print("✅ Environment configured!")


def setup_instrumentation():
    """Configure OpenTelemetry instrumentation."""
    logfire.configure(
        service_name='agent_evaluation_step2',
        send_to_logfire=False,
    )
    logfire.instrument_openai_agents()
    print("✅ Instrumentation configured!")


def create_gemini_model():
    """Create Gemini model client."""
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    return llm_model


# Define function tools
@function_tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Weather description
    """
    # In production, this would call a real weather API
    weather_data = {
        "San Francisco": "sunny, 72°F",
        "New York": "cloudy, 65°F",
        "London": "rainy, 55°F",
        "Tokyo": "clear, 68°F",
        "Paris": "partly cloudy, 60°F",
    }
    return f"The weather in {city} is {weather_data.get(city, 'sunny, 70°F')}."


@function_tool
def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.
    
    Args:
        expression: Math expression to evaluate (e.g., "2 + 2")
        
    Returns:
        Result of the calculation
    """
    try:
        # Simple eval for demo - in production use safer parsing
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


async def run_agent_with_tools(langfuse):
    """
    Run an agent with multiple tools.
    
    The agent can decide which tools to call based on the user's question.
    All tool calls are automatically traced!
    """
    print("\n" + "="*60)
    print("STEP 2: Agent with Tools")
    print("="*60)
    
    # Create Gemini model
    llm_model = create_gemini_model()
    
    # Create agent with tools
    agent = Agent(
        name="ToolExpert",
        instructions=(
            "You are a helpful assistant with access to tools. "
            "Use the weather tool to check weather and the calculate tool for math. "
            "Always use tools when appropriate."
        ),
        model=llm_model,
        tools=[get_weather, calculate]  # Provide tools to the agent
    )
    
    # Ask a question that requires tools
    question = "What's the weather in Tokyo? Also, what's 15 * 7?"
    print(f"\n📝 Question: {question}")
    
    # Run the agent - it will automatically call the tools!
    result = await Runner.run(agent, question)
    
    # Display the response
    print(f"\n💬 Agent Response:")
    print(f"{result.final_output}")
    
    # Flush traces
    langfuse.flush()
    
    print("\n✅ Trace with tool calls sent to Langfuse!")
    print(f"   View at: {os.getenv('LANGFUSE_HOST')}/traces")


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 2: AGENT WITH TOOLS AND TRACING")
    print("="*60)
    
    # Setup
    print("\n📦 Setting up...")
    setup_environment()
    setup_instrumentation()
    
    # Connect to Langfuse
    print("\n🔗 Connecting to Langfuse...")
    langfuse = get_client()
    
    if not langfuse.auth_check():
        raise ConnectionError("❌ Langfuse authentication failed")
    
    print("✅ Langfuse connected!")
    
    # Run the agent with tools
    print("\n🤖 Running agent with tools...")
    await run_agent_with_tools(langfuse)
    
    # Summary
    print("\n" + "="*60)
    print("✅ STEP 2 COMPLETE!")
    print("="*60)
    print("\n🎉 You've traced an agent with tools!")
    print("\n📊 What to check in Langfuse:")
    print("   - See the main agent span")
    print("   - Find the tool call spans (get_weather, calculate)")
    print("   - Check the order of operations")
    print("   - View tool inputs and outputs")
    print("\n💡 Key Learning:")
    print("   When agents use tools, each tool call becomes")
    print("   a separate span in the trace. This lets you see:")
    print("   - Which tools were called")
    print("   - What parameters were passed")
    print("   - What results were returned")
    print("   - How long each tool took")
    print("\n   Next: Run 03_custom_metadata.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
