"""
STEP 4: User Feedback Collection

Learn how to:
- Collect user ratings (thumbs up/down)
- Attach scores to traces
- Build feedback loops for improvement
- Track user satisfaction over time

This is crucial for understanding what works and what doesn't!
"""

import asyncio
import os
import base64
from dotenv import load_dotenv, find_dotenv

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from langfuse import get_client
import logfire


def setup_environment():
    """Configure environment."""
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
    """Configure instrumentation."""
    logfire.configure(service_name='agent_evaluation_step4', send_to_logfire=False)
    logfire.instrument_openai_agents()
    print("✅ Instrumentation configured!")


def create_gemini_model():
    """Create Gemini model."""
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.0-flash-exp", openai_client=external_client)


async def run_agent_and_collect_feedback(langfuse):
    """Run agent and simulate user feedback."""
    print("\n" + "="*60)
    print("STEP 4: User Feedback Collection")
    print("="*60)
    
    question = "What metrics should I track when evaluating AI agents?"
    
    # Run agent with custom span to get trace ID
    with langfuse.start_as_current_span(name="Agent-With-Feedback") as span:
        llm_model = create_gemini_model()
        
        agent = Agent(
            name="MetricsExpert",
            instructions=(
                "You are an expert in AI observability and monitoring. "
                "Provide clear, actionable metrics to track."
            ),
            model=llm_model
        )
        
        print(f"\n📝 Question: {question}")
        result = await Runner.run(agent, question)
        
        # Get the trace ID for attaching feedback
        trace_id = langfuse.get_current_trace_id()
        
        # Update trace with input/output
        span.update_trace(
            input=question,
            output=result.final_output,
        )
        
        print(f"\n💬 Agent Response:")
        print(f"{result.final_output}")
    
    # Simulate user feedback
    print("\n" + "-"*60)
    print("USER FEEDBACK SIMULATION")
    print("-"*60)
    print("\n👤 User sees the response and gives feedback...")
    print("\n   [User clicks: 👍 Thumbs Up]")
    
    # Create a positive feedback score
    langfuse.create_score(
        value=1,  # 1 = positive, 0 = negative
        name="user-feedback",
        comment="User found this response helpful and comprehensive",
        trace_id=trace_id
    )
    
    print("\n✅ Positive feedback recorded!")
    
    # You can also add multiple scores for different aspects
    langfuse.create_score(
        value=0.9,  # Scale of 0-1
        name="response-quality",
        comment="High quality response with good examples",
        trace_id=trace_id
    )
    
    langfuse.create_score(
        value=0.85,
        name="relevance",
        comment="Very relevant to the question asked",
        trace_id=trace_id
    )
    
    langfuse.flush()
    print("✅ All feedback scores sent to Langfuse!")


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 4: USER FEEDBACK COLLECTION")
    print("="*60)
    
    setup_environment()
    setup_instrumentation()
    
    langfuse = get_client()
    if not langfuse.auth_check():
        raise ConnectionError("❌ Langfuse authentication failed")
    print("✅ Langfuse connected!")
    
    await run_agent_and_collect_feedback(langfuse)
    
    print("\n" + "="*60)
    print("✅ STEP 4 COMPLETE!")
    print("="*60)
    print("\n🎉 You've collected and recorded user feedback!")
    print("\n📊 What to check in Langfuse:")
    print("   - Find the trace")
    print("   - Look for 'Scores' section")
    print("   - See user-feedback: 1 (👍)")
    print("   - See response-quality: 0.9")
    print("   - See relevance: 0.85")
    print("\n💡 Real-World Applications:")
    print("   In production, you would:")
    print("   1. Show agent response in your UI")
    print("   2. Add 👍/👎 buttons")
    print("   3. When user clicks, call langfuse.create_score()")
    print("   4. Analyze feedback to improve:")
    print("      - Identify poorly-rated responses")
    print("      - Find patterns in feedback")
    print("      - A/B test improvements")
    print("      - Monitor satisfaction over time")
    print("\n💡 Score Types:")
    print("   - Binary: 0 or 1 (thumbs up/down)")
    print("   - Scale: 0.0 to 1.0 (quality ratings)")
    print("   - Custom: Any metric you want to track")
    print("\n   Next: Run 05_dataset_eval.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
