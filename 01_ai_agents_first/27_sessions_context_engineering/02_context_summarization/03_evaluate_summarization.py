"""
Context Summarization - Evaluation

This script evaluates summarization quality using:
1. Token savings measurement
2. LLM-as-judge for information retention
3. Coherence assessment
4. Cost analysis

Run: python 03_evaluate_summarization.py
"""

import os
import asyncio
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents.models import OpenAIChatCompletionsModel

load_dotenv()

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


# ============= TOKEN COUNTING =============

def count_tokens(messages: List[Dict[str, str]]) -> int:
    """
    Count tokens in messages.
    Falls back to estimation if tiktoken not available.
    """
    if HAS_TIKTOKEN:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = 0
        for msg in messages:
            token_count += len(encoding.encode(msg.get("role", "")))
            token_count += len(encoding.encode(msg.get("content", "")))
            token_count += 4  # Message overhead
        token_count += 2  # Start/end tokens
        return token_count
    else:
        # Fallback: 1 token ~= 4 characters
        char_count = sum(len(msg.get("role", "")) + len(msg.get("content", "")) for msg in messages)
        return char_count // 4 + len(messages) * 4 + 2


# ============= MOCK SUMMARIZER (for evaluation without SDK) =============

class MockSummarizer:
    """
    Mock summarizer that simulates SummarizingSession behavior for evaluation.
    """
    
    def __init__(self, llm_model, keep_turns: int = 5):
        self.llm_model = llm_model
        self.keep_turns = keep_turns
        self.messages: List[Dict[str, str]] = []
    
    async def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append({"role": role, "content": content})
    
    async def get_summarized_context(self) -> List[Dict[str, str]]:
        """
        Get context with summarization applied.
        Keeps last keep_turns messages, summarizes the rest.
        """
        if len(self.messages) <= self.keep_turns:
            return self.messages
        
        # Split into old (to summarize) and recent (to keep)
        old_messages = self.messages[:-self.keep_turns]
        recent_messages = self.messages[-self.keep_turns:]
        
        # Create summary of old messages
        summary_text = await self._summarize_messages(old_messages)
        
        # Return summary + recent messages
        return [
            {"role": "system", "content": f"Previous conversation summary: {summary_text}"}
        ] + recent_messages
    
    async def _summarize_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Use LLM to summarize messages.
        """
        # Format messages for summarization
        conversation = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        )
        
        # Create summarization prompt
        client = self.llm_model.openai_client
        response = await client.chat.completions.create(
            model=self.llm_model.model,
            messages=[
                {
                    "role": "system",
                    "content": """Summarize this conversation, preserving:
1. Main topics and goals
2. Key facts, names, numbers
3. Decisions made
4. Open questions

Keep summary under 100 words."""
                },
                {
                    "role": "user",
                    "content": conversation
                }
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content


# ============= LLM-AS-JUDGE EVALUATOR =============

class SummarizationEvaluator:
    """
    Evaluates summarization quality using LLM-as-judge approach.
    """
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
    
    async def evaluate_information_retention(
        self,
        original_messages: List[Dict[str, str]],
        summarized_context: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Evaluate if key information is retained in summary.
        """
        # Extract original conversation and summary
        original_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in original_messages
        )
        
        summary_text = next(
            (msg['content'] for msg in summarized_context if msg['role'] == 'system'),
            ""
        )
        
        # LLM-as-judge prompt
        evaluation_prompt = f"""Original conversation:
{original_text}

Summary:
{summary_text}

Evaluate the summary quality:
1. Are key facts preserved? (0-10)
2. Are important decisions captured? (0-10)
3. Is the summary coherent? (0-10)
4. What critical information is missing, if any?

Respond in format:
Facts Score: X/10
Decisions Score: X/10
Coherence Score: X/10
Missing: [description or "None"]
Overall: X/10"""

        client = self.llm_model.openai_client
        response = await client.chat.completions.create(
            model=self.llm_model.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at evaluating conversation summaries. Be precise and critical."
                },
                {
                    "role": "user",
                    "content": evaluation_prompt
                }
            ],
            max_tokens=300
        )
        
        evaluation = response.choices[0].message.content
        
        # Parse scores (simple extraction)
        scores = {}
        for line in evaluation.split("\n"):
            if "Facts Score:" in line:
                scores["facts"] = self._extract_score(line)
            elif "Decisions Score:" in line:
                scores["decisions"] = self._extract_score(line)
            elif "Coherence Score:" in line:
                scores["coherence"] = self._extract_score(line)
            elif "Overall:" in line:
                scores["overall"] = self._extract_score(line)
        
        return {
            "scores": scores,
            "full_evaluation": evaluation
        }
    
    def _extract_score(self, line: str) -> int:
        """Extract numeric score from evaluation line."""
        import re
        match = re.search(r'(\d+)/10', line)
        return int(match.group(1)) if match else 0


# ============= EVALUATION SCENARIOS =============

async def evaluate_scenario(
    scenario_name: str,
    messages: List[Tuple[str, str]],
    keep_turns: int,
    llm_model
):
    """
    Evaluate a single conversation scenario.
    """
    print(f"\n{'=' * 60}")
    print(f"Scenario: {scenario_name}")
    print(f"{'=' * 60}")
    
    # Create summarizer
    summarizer = MockSummarizer(llm_model, keep_turns=keep_turns)
    
    # Add all messages
    for role, content in messages:
        await summarizer.add_message(role, content)
    
    # Get original and summarized context
    original_context = summarizer.messages
    summarized_context = await summarizer.get_summarized_context()
    
    # Count tokens
    original_tokens = count_tokens(original_context)
    summarized_tokens = count_tokens(summarized_context)
    
    # Calculate savings
    token_savings = original_tokens - summarized_tokens
    savings_percent = (token_savings / original_tokens * 100) if original_tokens > 0 else 0
    
    print(f"\n📊 Token Metrics:")
    print(f"   Original context: {original_tokens} tokens")
    print(f"   Summarized context: {summarized_tokens} tokens")
    print(f"   Savings: {token_savings} tokens ({savings_percent:.1f}%)")
    
    # Calculate cost savings (approximate at $0.002/1k tokens)
    cost_per_1k = 0.002
    original_cost = (original_tokens / 1000) * cost_per_1k
    summarized_cost = (summarized_tokens / 1000) * cost_per_1k
    cost_savings = original_cost - summarized_cost
    
    print(f"\n💰 Cost Savings (approximate):")
    print(f"   Original cost: ${original_cost:.4f}")
    print(f"   Summarized cost: ${summarized_cost:.4f}")
    print(f"   Savings: ${cost_savings:.4f}")
    
    # Evaluate quality with LLM-as-judge
    print(f"\n🔍 Evaluating summary quality...")
    evaluator = SummarizationEvaluator(llm_model)
    evaluation = await evaluator.evaluate_information_retention(
        original_context,
        summarized_context
    )
    
    print(f"\n📝 Quality Scores:")
    for metric, score in evaluation["scores"].items():
        print(f"   {metric.capitalize()}: {score}/10")
    
    return {
        "scenario": scenario_name,
        "original_tokens": original_tokens,
        "summarized_tokens": summarized_tokens,
        "savings_percent": savings_percent,
        "cost_savings": cost_savings,
        "quality_scores": evaluation["scores"]
    }


async def run_evaluation():
    """
    Run evaluation on multiple scenarios.
    """
    print("=" * 60)
    print("SUMMARIZATION EVALUATION")
    print("=" * 60)
    
    # Setup Gemini model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    # Scenario 1: Customer Support (8 turns)
    support_messages = [
        ("user", "My order hasn't arrived yet, it's been 10 days"),
        ("assistant", "I'm sorry to hear that. Let me look up your order. Can you provide the order number?"),
        ("user", "Order #12345, placed on January 5th"),
        ("assistant", "Thank you. I see your order was shipped but is delayed at the depot. I can offer a refund or resend with express shipping."),
        ("user", "Please resend with express shipping"),
        ("assistant", "Done! Express shipment created, arrives in 2 days. Confirmation sent to your email."),
        ("user", "Great! Also, I want to return another item from order #12340"),
        ("assistant", "Of course. What item would you like to return and what's the reason?")
    ]
    
    # Scenario 2: Consulting (12 turns)
    consulting_messages = [
        ("user", "We need to improve our website conversion rate"),
        ("assistant", "What's your current conversion rate and what's your goal?"),
        ("user", "Currently 2%, want to reach 4% in 3 months"),
        ("assistant", "That's ambitious but achievable. What's your current traffic source mix?"),
        ("user", "60% organic, 30% paid ads, 10% social media"),
        ("assistant", "Good foundation. I recommend focusing on three areas: landing page optimization, checkout flow, and trust signals."),
        ("user", "What specific changes for landing pages?"),
        ("assistant", "Add social proof, improve hero copy, reduce friction in forms. I can create a detailed audit."),
        ("user", "Yes please. What's your timeline?"),
        ("assistant", "I'll deliver the audit in 1 week, then we implement changes over 4 weeks with A/B testing."),
        ("user", "Budget for implementation?"),
        ("assistant", "Estimate $15-20K for design, development, and testing tools. Worth it for 2x conversion increase.")
    ]
    
    results = []
    
    # Evaluate scenarios
    results.append(await evaluate_scenario(
        "Customer Support (8 turns)",
        support_messages,
        keep_turns=3,
        llm_model=llm_model
    ))
    
    results.append(await evaluate_scenario(
        "Consulting (12 turns)",
        consulting_messages,
        keep_turns=4,
        llm_model=llm_model
    ))
    
    # Summary report
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    for result in results:
        print(f"\n{result['scenario']}:")
        print(f"  Token savings: {result['savings_percent']:.1f}%")
        print(f"  Cost savings: ${result['cost_savings']:.4f}")
        print(f"  Quality (overall): {result['quality_scores'].get('overall', 'N/A')}/10")
    
    avg_savings = sum(r['savings_percent'] for r in results) / len(results)
    total_cost_savings = sum(r['cost_savings'] for r in results)
    
    print(f"\n📊 Overall Results:")
    print(f"   Average token savings: {avg_savings:.1f}%")
    print(f"   Total cost savings: ${total_cost_savings:.4f}")
    
    print("\n✅ Evaluation completed!")


if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment")
        print("Please create a .env file with your API key")
    else:
        asyncio.run(run_evaluation())
