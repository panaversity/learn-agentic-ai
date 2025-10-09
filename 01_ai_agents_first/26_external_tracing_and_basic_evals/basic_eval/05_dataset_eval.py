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
from dotenv import load_dotenv, find_dotenv

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from langfuse import Langfuse  # Direct import, no get_client


def setup_environment():
    load_dotenv(find_dotenv())
    required_vars = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing: {', '.join(missing_vars)}")
    print("✅ Environment configured!")


def create_gemini_model(model_name="gemini-2.0-flash-lite"):
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


def create_evaluator_agent():
    """Create an LLM-as-a-Judge evaluator agent."""
    llm_model = create_gemini_model()
    return Agent(
        name="LLM-as-a-Judge",
        instructions=(
            "You are an expert evaluator using LLM-as-a-Judge methodology. "
            "Score responses on a scale of 0-1 based on:\n"
            "- Correctness (0.4): How factually correct is the answer?\n"
            "- Relevance (0.3): How relevant is the answer to the question?\n"
            "- Completeness (0.3): How complete is the answer?\n\n"
            "Respond with ONLY a number between 0 and 1, nothing else."
        ),
        model=llm_model
    )


async def evaluate_with_llm_judge(question: str, expected: str, actual: str, evaluator: Agent) -> dict:
    """Evaluate using LLM-as-a-Judge methodology."""
    evaluation_prompt = f"""
Question: {question}
Expected Answer: {expected}
Actual Answer: {actual}

Please evaluate the actual answer on a scale of 0-1 based on:
- Correctness (0.4): How factually correct is the answer?
- Relevance (0.3): How relevant is the answer to the question?
- Completeness (0.3): How complete is the answer?

Respond with ONLY a number between 0 and 1, nothing else.
"""
    
    try:
        result = await Runner.run(evaluator, evaluation_prompt)
        score = float(result.final_output.strip())
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
        
        # Calculate individual scores based on LLM judgment
        correctness = 1.0 if expected.lower() in actual.lower() else score * 0.8
        relevance = score
        completeness = score
        
        return {
            "overall_score": score,
            "correctness": correctness,
            "relevance": relevance,
            "completeness": completeness,
            "evaluation_method": "LLM-as-a-Judge"
        }
    except (ValueError, AttributeError) as e:
        print(f"⚠️  LLM-as-a-Judge evaluation failed: {e}")
        # Fallback to simple scoring
        simple_score = 1.0 if expected.lower() in actual.lower() else 0.0
        return {
            "overall_score": simple_score,
            "correctness": simple_score,
            "relevance": simple_score,
            "completeness": simple_score,
            "evaluation_method": "Fallback"
        }


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
    Run an evaluation on a dataset with AUTOMATED SCORING.
    
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
    llm_model = create_gemini_model(agent_config.get("model", "gemini-2.0-flash-lite"))
    
    # Create agent with given configuration
    agent = Agent(
        name=agent_config.get("name", "QA-Agent"),
        instructions=agent_config.get("instructions", "You are a helpful assistant."),
        model=llm_model,
    )
    
    # Create LLM-as-a-Judge evaluator
    evaluator = create_evaluator_agent()
    
    # Get dataset
    dataset = langfuse.get_dataset(name=dataset_name)
    
    results = []
    total_score = 0
    
    # Run agent on each dataset item
    for idx, item in enumerate(dataset.items, 1):
        question = item.input["question"]
        expected = item.expected_output["answer"]
        
        print(f"\n[{idx}/{len(dataset.items)}] Question: {question}")
        
        # Run with dataset item context
        with item.run(
            run_name=run_name,
            run_metadata={
                "model": agent_config.get("model", "gemini-2.0-flash-lite"),
                "config": agent_config
            },
            run_description=f"Evaluation run: {run_name}"
        ):
            # Run the agent
            answer = await run_agent_on_question(agent, question)
            
            # AUTOMATED EVALUATION using LLM-as-a-Judge methodology
            evaluation = await evaluate_with_llm_judge(question, expected, answer, evaluator)
            
            print(f"   Answer: {answer[:100]}...")
            print(f"   Expected: {expected}")
            print(f"   🎯 Overall Score: {evaluation['overall_score']:.2f}")
            print(f"   ✅ Correctness: {evaluation['correctness']:.2f}")
            print(f"   📊 Relevance: {evaluation['relevance']:.2f}")
            print(f"   📝 Completeness: {evaluation['completeness']:.2f}")
            print(f"   🔧 Evaluator: {evaluation.get('evaluation_method', 'Unknown')}")
            
            # Add scores to Langfuse
            try:
                # Score the current run
                langfuse.score_current_trace(
                    name="overall_score",
                    value=evaluation['overall_score'],
                    data_type="NUMERIC",
                    comment=f"Overall evaluation score for: {question[:50]}..."
                )
                
                langfuse.score_current_trace(
                    name="correctness",
                    value=evaluation['correctness'],
                    data_type="NUMERIC",
                    comment="Factual correctness score"
                )
                
                langfuse.score_current_trace(
                    name="relevance",
                    value=evaluation['relevance'],
                    data_type="NUMERIC",
                    comment="Relevance to question score"
                )
                
                langfuse.score_current_trace(
                    name="completeness",
                    value=evaluation['completeness'],
                    data_type="NUMERIC",
                    comment="Answer completeness score"
                )
            except Exception as e:
                print(f"   ⚠️  Error adding scores: {e}")
            
            total_score += evaluation['overall_score']
            
            results.append({
                "question": question,
                "answer": answer,
                "expected": expected,
                "evaluation": evaluation,
                "item_id": item.id
            })
    
    # Calculate average score
    avg_score = total_score / len(results) if results else 0
    
    langfuse.flush()
    
    print(f"\n✅ Completed evaluation: {run_name}")
    print(f"   Processed {len(results)} questions")
    print(f"   🎯 Average Score: {avg_score:.2f}")
    print(f"   📊 Performance: {'Excellent' if avg_score > 0.8 else 'Good' if avg_score > 0.6 else 'Needs Improvement'}")
    
    return results, avg_score


async def compare_configurations(langfuse, dataset_name: str):
    """Compare different agent configurations on the same dataset with AUTOMATED SCORING."""
    print("\n" + "="*60)
    print("COMPARING AGENT CONFIGURATIONS (AUTOMATED EVALUATION)")
    print("="*60)
    
    # Configuration 1: Basic instructions
    config_1 = {
        "name": "BasicQA",
        "instructions": "You are a helpful assistant. Answer questions concisely.",
        "model": "gemini-2.0-flash-lite"
    }
    
    # Configuration 2: Detailed instructions
    config_2 = {
        "name": "DetailedQA",
        "instructions": (
            "You are a knowledgeable assistant with expertise across multiple domains. "
            "Answer questions accurately and concisely. If you're unsure, say so."
        ),
        "model": "gemini-2.0-flash-lite"
    }
    
    # Run evaluations with automated scoring
    print("\n🔍 Running Basic Configuration...")
    results_1, score_1 = await run_evaluation(
        langfuse,
        dataset_name,
        "basic-config-v1",
        config_1
    )
    
    await asyncio.sleep(2)  # Brief pause between runs
    
    print("\n🔍 Running Detailed Configuration...")
    results_2, score_2 = await run_evaluation(
        langfuse,
        dataset_name,
        "detailed-config-v1",
        config_2
    )
    
    # AUTOMATED COMPARISON RESULTS
    print("\n" + "="*60)
    print("🎯 AUTOMATED EVALUATION RESULTS")
    print("="*60)
    print(f"\n📊 Configuration Comparison:")
    print(f"   Basic QA:     {score_1:.2f} average score")
    print(f"   Detailed QA:  {score_2:.2f} average score")
    print(f"   Difference:   {abs(score_2 - score_1):.2f}")
    
    if score_2 > score_1:
        improvement = ((score_2 - score_1) / score_1) * 100
        print(f"   🏆 Winner: Detailed QA (+{improvement:.1f}% improvement)")
    elif score_1 > score_2:
        improvement = ((score_1 - score_2) / score_2) * 100
        print(f"   🏆 Winner: Basic QA (+{improvement:.1f}% improvement)")
    else:
        print(f"   🤝 Tie: Both configurations performed equally")
    
    print(f"\n📈 Performance Analysis:")
    print(f"   - Total questions evaluated: {len(EVALUATION_DATASET)}")
    print(f"   - All evaluations automated (no manual review needed)")

    print(f"\n📊 View detailed comparison in Langfuse:")
    print(f"   {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/datasets/{dataset_name}")
    
    return {"basic": score_1, "detailed": score_2}


async def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 STEP 5: DATASET-BASED EVALUATION (AUTOMATED)")
    print("="*60)

    setup_environment()
    
    # Create Langfuse client directly (no OpenTelemetry)
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
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


if __name__ == "__main__":
    asyncio.run(main())
