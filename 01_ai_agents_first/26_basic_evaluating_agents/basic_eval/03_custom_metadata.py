"""
STEP 3: Custom Metadata and Trace Enrichment

Learn how to:
- Add custom attributes to traces (user_id, session_id, tags)
- Include domain-specific metadata
- Filter and search traces by custom attributes
- Build better analytics and debugging capabilities

This helps you track WHO is using the agent and HOW!
"""

import asyncio
import os
import base64
from dotenv import load_dotenv, find_dotenv

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
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
    """Configure instrumentation."""
    logfire.configure(service_name='agent_evaluation_step3', send_to_logfire=False)
    logfire.instrument_openai_agents()
    print("✅ Instrumentation configured!")


def create_gemini_model():
    """Create Gemini model."""
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.0-flash-exp", openai_client=external_client)


async def run_agent_with_custom_metadata(langfuse):
    """Run agent and add custom metadata to the trace."""
    print("\n" + "="*60)
    print("STEP 3: Custom Metadata")
    print("="*60)
    
    question = "What are best practices for agent evaluation?"
    
    # Start a custom span to add metadata
    with langfuse.start_as_current_span(name="Agent-With-Metadata") as span:
        llm_model = create_gemini_model()
        
        agent = Agent(
            name="EvaluationExpert",
            instructions="You are an expert in AI agent evaluation. Provide concise, practical advice.",
            model=llm_model
        )
        
        print(f"\n📝 Question: {question}")
        result = await Runner.run(agent, question)
        
        # Add rich custom metadata
        span.update_trace(
            input=question,
            output=result.final_output,
            # User identification
            user_id="student_42",
            # Session tracking
            session_id="eval-lesson-session-2025-10-03",
            # Tags for filtering
            tags=["evaluation", "best-practices", "panaversity", "step3"],
            # Custom domain data
            metadata={
                "course": "AI Agents First",
                "lesson": "26_basic_evaluating_agents",
                "step": 3,
                "environment": "development",
                "student_level": "intermediate",
                "topic": "agent evaluation",
                "instructor": "Panaversity Team"
            },
            # Version for A/B testing
            version="v1.0.0"
        )
        
        print(f"\n💬 Agent Response:")
        print(f"{result.final_output}")
    
    langfuse.flush()
    print("\n✅ Trace with custom metadata sent!")


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 3: CUSTOM METADATA AND TRACE ENRICHMENT")
    print("="*60)
    
    setup_environment()
    setup_instrumentation()
    
    langfuse = get_client()
    if not langfuse.auth_check():
        raise ConnectionError("❌ Langfuse authentication failed")
    print("✅ Langfuse connected!")
    
    await run_agent_with_custom_metadata(langfuse)
    
    print("\n" + "="*60)
    print("✅ STEP 3 COMPLETE!")
    print("="*60)
    print("\n🎉 You've enriched traces with custom metadata!")
    print("\n📊 What to check in Langfuse:")
    print("   - user_id: student_42")
    print("   - session_id: eval-lesson-session-2025-10-03")
    print("   - tags: evaluation, best-practices, etc.")
    print("   - metadata: course info, environment, etc.")
    print("\n💡 Why This Matters:")
    print("   - Filter traces by user, session, or tags")
    print("   - Track user-specific issues")
    print("   - Monitor different environments (dev/prod)")
    print("   - Analyze usage patterns")
    print("   - A/B test with versions")
    print("\n   Next: Run 04_user_feedback.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
