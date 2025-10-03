"""
STEP 5: Dataset-Based Evaluation (Offline Evaluation)

Learn how to:
- Create evaluation datasets in Langfuse
- Run systematic tests on benchmark questions
- Compare different agent configurations
- Track metrics across multiple runs
- Make data-driven optimization decisions

This is how you test agents BEFORE deploying to production!
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
    logfire.configure(service_name='agent_evaluation_step5', send_to_logfire=False)
    logfire.instrument_openai_agents()
    print("✅ Instrumentation configured!")


def create_gemini_model(model_name="gemini-2.0-flash-exp"):
    """Create Gemini model."""
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletionsModel(model=model_name, openai_client=external_client)


# Sample evaluation dataset
EVALUATION_DATASET = [
    {
        "question": "What is the capital of France?",
        "expected_answer": "Paris",
        "category": "geography"
    },
    {
        "question": "What is 25 * 4?",
        "expected_answer": "100",
        "category": "math"
    },
    {
        "question": "Who wrote Romeo and Juliet?",
        "expected_answer": "William Shakespeare",
        "category": "literature"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "expected_answer": "Au",
        "category": "science"
    },
    {
        "question": "In what year did World War II end?",
        "expected_answer": "1945",
        "category": "history"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "expected_answer": "Jupiter",
        "category": "science"
    },
    {
        "question": "How many continents are there?",
        "expected_answer": "7",
        "category": "geography"
    },
    {
        "question": "What is the square root of 144?",
        "expected_answer": "12",
        "category": "math"
    },
]


async def run_agent_on_question(agent: Agent, question: str) -> str:
    """Run an agent on a single question."""
    result = await Runner.run(agent, question)
    return result.final_output


def create_dataset(langfuse, dataset_name: str):
    """Create or get a dataset in Langfuse."""
    try:
        # Try to get existing dataset
        dataset = langfuse.get_dataset(name=dataset_name)
        print(f"✅ Using existing dataset: {dataset_name}")
        return dataset
    except Exception:
        # Create new dataset if it doesn't exist
        print(f"📝 Creating new dataset: {dataset_name}")
        langfuse.create_dataset(
            name=dataset_name,
            description="General knowledge Q&A evaluation dataset",
            metadata={
                "created_by": "panaversity",
                "lesson": "26_basic_evaluating_agents",
                "type": "qa_benchmark"
            }
        )
        
        # Add items to dataset
        for item in EVALUATION_DATASET:
            langfuse.create_dataset_item(
                dataset_name=dataset_name,
                input={"question": item["question"]},
                expected_output={"answer": item["expected_answer"]},
                metadata={"category": item["category"]}
            )
        
        print(f"✅ Created dataset with {len(EVALUATION_DATASET)} items")
        return langfuse.get_dataset(name=dataset_name)


async def run_evaluation(
    langfuse,
    dataset_name: str,
    run_name: str,
    agent_config: dict
):
    """
    Run an evaluation on a dataset.
    
    Args:
        langfuse: Langfuse client
        dataset_name: Name of the dataset
        run_name: Name for this evaluation run
        agent_config: Configuration for the agent
    """
    print(f"\n{'='*60}")
    print(f"Running evaluation: {run_name}")
    print(f"{'='*60}")
    
    # Create Gemini model
    llm_model = create_gemini_model(agent_config.get("model", "gemini-2.0-flash-exp"))
    
    # Create agent with given configuration
    agent = Agent(
        name=agent_config.get("name", "QA-Agent"),
        instructions=agent_config.get("instructions", "You are a helpful assistant."),
        model=llm_model,
    )
    
    # Get dataset
    dataset = langfuse.get_dataset(name=dataset_name)
    
    results = []
    
    # Run agent on each dataset item
    for idx, item in enumerate(dataset.items, 1):
        question = item.input["question"]
        expected = item.expected_output["answer"]
        
        print(f"\n[{idx}/{len(dataset.items)}] Question: {question}")
        
        # Run with dataset item context
        with item.run(
            run_name=run_name,
            run_metadata={
                "model": agent_config.get("model", "gemini-2.0-flash-exp"),
                "config": agent_config
            },
            run_description=f"Evaluation run: {run_name}"
        ):
            # Run the agent
            answer = await run_agent_on_question(agent, question)
            
            print(f"   Answer: {answer}")
            print(f"   Expected: {expected}")
            
            results.append({
                "question": question,
                "answer": answer,
                "expected": expected,
                "item_id": item.id
            })
    
    langfuse.flush()
    
    print(f"\n✅ Completed evaluation: {run_name}")
    print(f"   Processed {len(results)} questions")
    
    return results


async def compare_configurations(langfuse, dataset_name: str):
    """Compare different agent configurations on the same dataset."""
    print("\n" + "="*60)
    print("COMPARING AGENT CONFIGURATIONS")
    print("="*60)
    
    # Configuration 1: Basic instructions
    config_1 = {
        "name": "BasicQA",
        "instructions": "You are a helpful assistant. Answer questions concisely.",
        "model": "gemini-2.0-flash-exp"
    }
    
    # Configuration 2: Detailed instructions
    config_2 = {
        "name": "DetailedQA",
        "instructions": (
            "You are a knowledgeable assistant with expertise across multiple domains. "
            "Answer questions accurately and concisely. If you're unsure, say so."
        ),
        "model": "gemini-2.0-flash-exp"
    }
    
    # Run evaluations
    await run_evaluation(
        langfuse,
        dataset_name,
        "basic-config-v1",
        config_1
    )
    
    await asyncio.sleep(2)  # Brief pause between runs
    
    await run_evaluation(
        langfuse,
        dataset_name,
        "detailed-config-v1",
        config_2
    )
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    print(f"\nCompared 2 configurations on {len(EVALUATION_DATASET)} questions")
    print("\n📊 View detailed comparison in Langfuse:")
    print(f"   {os.getenv('LANGFUSE_HOST')}/datasets/{dataset_name}")


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 5: DATASET-BASED EVALUATION")
    print("="*60)
    
    setup_environment()
    setup_instrumentation()
    
    langfuse = get_client()
    if not langfuse.auth_check():
        raise ConnectionError("❌ Langfuse authentication failed")
    print("✅ Langfuse connected!")
    
    # Create or get dataset
    dataset_name = "qa-benchmark-panaversity"
    print(f"\n📊 Preparing dataset: {dataset_name}")
    create_dataset(langfuse, dataset_name)
    
    # Run comparison evaluation
    await compare_configurations(langfuse, dataset_name)
    
    # Summary
    print("\n" + "="*60)
    print("✅ STEP 5 COMPLETE!")
    print("="*60)
    print("\n🎉 You've run a complete dataset evaluation!")
    print("\n� What to check in Langfuse:")
    print("   1. Go to Datasets section")
    print(f"   2. Find: {dataset_name}")
    print("   3. See all 8 test questions")
    print("   4. View 2 different runs:")
    print("      - basic-config-v1")
    print("      - detailed-config-v1")
    print("   5. Compare their performance")
    print("\n💡 Key Learnings:")
    print("   - Datasets let you test systematically")
    print("   - Run same tests with different configs")
    print("   - Track which configuration performs better")
    print("   - Catch regressions before production")
    print("   - Make data-driven optimization decisions")
    print("\n💡 Next Steps:")
    print("   - Try different Gemini models")
    print("   - Modify instructions")
    print("   - Add more test questions")
    print("   - Set up LLM-as-a-Judge evaluators")
    print(f"\n📊 Visit: {os.getenv('LANGFUSE_HOST')}/datasets")
    print("\n🎓 You've completed all 5 steps of agent evaluation!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
