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
from langfuse import Langfuse  # Direct import, no get_client


def setup_environment():
    """Configure environment variables."""
    load_dotenv(find_dotenv())
    required_vars = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing: {', '.join(missing_vars)}")
    print("✅ Environment configured!")


def create_gemini_model():
    """Create Gemini model."""
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)


async def run_agent_and_collect_feedback():
    """Run agent and simulate user feedback - SIMPLIFIED VERSION."""
    print("\n" + "="*60)
    print("STEP 4: User Feedback Collection (SIMPLIFIED)")
    print("="*60)
    
    # Create Langfuse client directly (no OpenTelemetry)
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    # Test connection
    if not langfuse.auth_check():
        raise ConnectionError("❌ Langfuse authentication failed")
    print("✅ Langfuse connected!")
    
    question = "What metrics should I track when evaluating AI agents?"
    
    # Create a trace ID manually
    trace_id = langfuse.create_trace_id()
    print(f"\n📝 Question: {question}")
    print(f"🔍 Trace ID: {trace_id}")
    
    # Run agent (without any OpenTelemetry instrumentation)
    llm_model = create_gemini_model()
    agent = Agent(
        name="MetricsExpert",
        instructions=(
            "You are an expert in AI observability and monitoring. "
            "Provide clear, actionable metrics to track."
        ),
        model=llm_model
    )
    
    result = await Runner.run(agent, question)
    
    print(f"\n💬 Agent Response:")
    print(f"{result.final_output[:300]}...")  # Show first 300 chars
    
    # Simulate user feedback
    print("\n" + "-"*60)
    print("USER FEEDBACK SIMULATION")
    print("-"*60)
    print("\n👤 User sees the response and gives feedback...")
    print("\n   [User clicks: 👍 Thumbs Up]")
    
    # Create scores using the simplest possible approach
    print("\n🔧 Creating user feedback scores...")
    
    # Score 1: Boolean feedback (thumbs up/down)
    try:
        score1 = langfuse.create_score(
            name="user-feedback",
            value=1,  # 1 = positive, 0 = negative
            trace_id=trace_id,
            data_type="BOOLEAN",  # Explicitly specify data type
            comment="User found this response helpful and comprehensive"
        )
        print("✅ Positive feedback recorded!")
        print(f"   Score ID: {getattr(score1, 'id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error creating user-feedback score: {e}")
    
    # Score 2: Numeric quality rating
    try:
        score2 = langfuse.create_score(
            name="response-quality",
            value=0.9,  # Scale of 0-1
            trace_id=trace_id,
            data_type="NUMERIC",  # Explicitly specify data type
            comment="High quality response with good examples"
        )
        print("✅ Response quality score recorded!")
        print(f"   Score ID: {getattr(score2, 'id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error creating response-quality score: {e}")
    
    # Score 3: Numeric relevance rating
    try:
        score3 = langfuse.create_score(
            name="relevance",
            value=0.85,
            trace_id=trace_id,
            data_type="NUMERIC",  # Explicitly specify data type
            comment="Very relevant to the question asked"
        )
        print("✅ Relevance score recorded!")
        print(f"   Score ID: {getattr(score3, 'id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error creating relevance score: {e}")
    
    # Score 4: Categorical evaluation
    try:
        score4 = langfuse.create_score(
            name="overall-satisfaction",
            value="excellent",  # Categorical value
            trace_id=trace_id,
            data_type="CATEGORICAL",  # Explicitly specify data type
            comment="Overall user satisfaction level"
        )
        print("✅ Overall satisfaction score recorded!")
        print(f"   Score ID: {getattr(score4, 'id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error creating overall-satisfaction score: {e}")
    
    # Flush to ensure all data is sent
    print("\n   Flushing data to Langfuse...")
    langfuse.flush()
    print("✅ All feedback scores sent to Langfuse!")
    
    print(f"\n🔍 Final Info:")
    print(f"   - Trace ID: {trace_id}")
    print(f"   - Langfuse host: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
    
    return trace_id


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 4: USER FEEDBACK COLLECTION")
    print("="*60)
    print("This version bypasses OpenTelemetry completely")
    
    setup_environment()
    
    trace_id = await run_agent_and_collect_feedback()
    
    print("\n" + "="*60)
    print("✅ STEP 4 COMPLETE!")
    print("="*60)
    print(f"\n🎉 Scores created for trace: {trace_id}")
    print("\n📊 Check your Langfuse dashboard:")
    print(f"   - Go to: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
    print(f"   - Find trace: {trace_id}")
    print("   - Look for 'Scores' section")
    print("   - You should see 4 scores:")
    print("     - user-feedback: 1 (BOOLEAN - 👍)")
    print("     - response-quality: 0.9 (NUMERIC)")
    print("     - relevance: 0.85 (NUMERIC)")
    print("     - overall-satisfaction: 'excellent' (CATEGORICAL)")
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
    print("\n💡 Score Types (per Langfuse docs):")
    print("   - BOOLEAN: 0 or 1 (thumbs up/down)")
    print("   - NUMERIC: 0.0 to 1.0 (quality ratings)")
    print("   - CATEGORICAL: String values (excellent, good, poor)")
    print("   - All types support comments and trace linking")
    print("\n💡 If scores still don't appear:")
    print("   - Check your Langfuse project settings")
    print("   - Verify API keys have correct permissions")
    print("   - Try creating a score manually in the UI first")
    print("\n   Next: Run 05_dataset_eval.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
