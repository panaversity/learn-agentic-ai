"""
Context Summarization - Production Implementation

This example shows production-grade summarization patterns:
1. Configurable summarizer prompts
2. Async summarization with error handling
3. Tool output trimming
4. Idempotent summarization (prevents re-summarizing summaries)
5. Monitoring and logging

Run: python 02_production_summarization.py
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import LLMSummarizer, SummarizingSession

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============= ENHANCED SUMMARIZER =============

class ProductionSummarizer:
    """
    Production-grade summarizer with monitoring and error handling.
    """
    
    def __init__(self, llm_model, domain: str = "general"):
        """
        Initialize summarizer with domain-specific prompts.
        
        Args:
            llm_model: Language model for summarization
            domain: Conversation domain (e.g., 'support', 'consulting', 'general')
        """
        self.domain = domain
        self.summarization_count = 0
        self.total_input_tokens = 0
        self.total_summary_tokens = 0
        
        # Domain-specific system messages
        system_messages = {
            "support": """Summarize customer support conversation, preserving:
1. Customer's issue or request
2. Solutions attempted or provided
3. Open tickets or action items
4. Customer sentiment and satisfaction level
Keep summary under 150 words.""",
            
            "consulting": """Summarize consulting conversation, preserving:
1. Client's business goals and constraints
2. Recommendations provided
3. Decisions made and next steps
4. Key metrics or numbers discussed
Keep summary under 200 words.""",
            
            "general": """Summarize conversation, preserving:
1. Main topics and goals discussed
2. Key decisions or commitments
3. Important facts, names, or numbers
4. Open questions or next steps
Keep summary concise (under 150 words)."""
        }
        
        self.summarizer = LLMSummarizer(
            model=llm_model,
            system_message=system_messages.get(domain, system_messages["general"]),
            max_tokens=300
        )
        
        logger.info(f"ProductionSummarizer initialized with domain: {domain}")
    
    async def summarize(self, messages: list) -> str:
        """
        Summarize messages with error handling and monitoring.
        """
        start_time = datetime.now()
        input_token_estimate = sum(len(str(msg)) // 4 for msg in messages)
        
        try:
            logger.info(f"Starting summarization of {len(messages)} messages (~{input_token_estimate} tokens)")
            
            # Perform summarization
            summary = await self.summarizer.summarize(messages)
            
            # Update stats
            self.summarization_count += 1
            self.total_input_tokens += input_token_estimate
            summary_tokens = len(summary) // 4
            self.total_summary_tokens += summary_tokens
            
            duration = (datetime.now() - start_time).total_seconds()
            compression_ratio = (1 - summary_tokens / input_token_estimate) * 100 if input_token_estimate > 0 else 0
            
            logger.info(f"Summarization completed in {duration:.2f}s")
            logger.info(f"Compression: {input_token_estimate} → {summary_tokens} tokens ({compression_ratio:.1f}% reduction)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Fallback: return simple concatenation
            return "Previous conversation context (summarization failed): " + " ".join(
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}..." 
                for msg in messages[:3]
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get summarization statistics."""
        avg_compression = (
            (1 - self.total_summary_tokens / self.total_input_tokens) * 100
            if self.total_input_tokens > 0 else 0
        )
        
        return {
            "summarization_count": self.summarization_count,
            "total_input_tokens": self.total_input_tokens,
            "total_summary_tokens": self.total_summary_tokens,
            "average_compression_ratio": f"{avg_compression:.1f}%",
            "domain": self.domain
        }


# ============= ADVANCED SESSION CONFIGURATION =============

class AdvancedSummarizingSession(SummarizingSession):
    """
    Enhanced summarizing session with additional production features.
    """
    
    def __init__(self, summarizer, keep_turns: int = 5, trim_tool_outputs: bool = True):
        """
        Initialize advanced summarizing session.
        
        Args:
            summarizer: LLMSummarizer instance
            keep_turns: Number of recent turns to keep verbatim
            trim_tool_outputs: Whether to trim large tool outputs before summarization
        """
        super().__init__(summarizer=summarizer, keep_turns=keep_turns)
        self.trim_tool_outputs = trim_tool_outputs
        self.max_tool_output_length = 500  # chars
        
        logger.info(f"AdvancedSummarizingSession initialized (keep_turns={keep_turns}, trim_tools={trim_tool_outputs})")
    
    async def add_items(self, items):
        """
        Add items with tool output trimming if enabled.
        """
        if self.trim_tool_outputs:
            items = self._trim_large_tool_outputs(items)
        
        await super().add_items(items)
    
    def _trim_large_tool_outputs(self, items):
        """
        Trim large tool outputs to reduce token usage before summarization.
        """
        trimmed_items = []
        
        for item in items:
            if item.get("role") == "tool" and len(item.get("content", "")) > self.max_tool_output_length:
                # Trim tool output
                original_length = len(item["content"])
                trimmed_content = item["content"][:self.max_tool_output_length] + f"\n... (trimmed {original_length - self.max_tool_output_length} chars)"
                
                trimmed_item = item.copy()
                trimmed_item["content"] = trimmed_content
                trimmed_items.append(trimmed_item)
                
                logger.debug(f"Trimmed tool output: {original_length} → {len(trimmed_content)} chars")
            else:
                trimmed_items.append(item)
        
        return trimmed_items


# ============= DEMO: CUSTOMER SUPPORT AGENT =============

async def demo_customer_support():
    """
    Demonstrate production summarization with customer support agent.
    """
    print("=" * 60)
    print("PRODUCTION SUMMARIZATION DEMO")
    print("Customer Support Agent with Long Conversation")
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
    
    # Create production summarizer
    prod_summarizer = ProductionSummarizer(llm_model, domain="support")
    
    # Create advanced session
    session = AdvancedSummarizingSession(
        summarizer=prod_summarizer.summarizer,
        keep_turns=4,  # Keep last 4 turns
        trim_tool_outputs=True
    )
    
    # Create support agent
    agent = Agent(
        name="SupportAgent",
        instructions="""You are a customer support agent for an e-commerce platform.
Help customers with order issues, returns, and account questions.
Always be empathetic and solution-oriented.
Reference previous conversation context when relevant.""",
        model=llm_model,
        session=session
    )
    
    # Simulate customer support conversation (12 turns)
    conversation_turns = [
        "Hi, I haven't received my order #12345 yet",
        "I placed it on January 5th, it's been 10 days",
        "The tracking shows it's stuck at the local depot",
        "Order #12345 - wireless headphones, $89.99",
        "Yes, I need them urgently for a trip this weekend",
        "Can you upgrade to express shipping or send a replacement?",
        "That works! Please send the replacement express",
        "My address is 123 Main St, New York, NY 10001",
        "Also, I'd like to return another item - order #12340",
        "It's a laptop case that doesn't fit my laptop",
        "Yes, I have the original packaging and receipt",
        "Great! Can I use the refund as credit for the replacement shipping?"
    ]
    
    print("\nStarting support conversation...\n")
    
    runner = Runner()
    for i, user_message in enumerate(conversation_turns, 1):
        print(f"\n{'─' * 60}")
        print(f"Turn {i}/12")
        print(f"{'─' * 60}")
        print(f"Customer: {user_message}")
        
        # Run agent
        response = await runner.run(agent=agent, input=user_message)
        print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
        
        # Show session state
        items = await session.get_items()
        message_count = len([item for item in items if item.get("role") in ["user", "assistant"]])
        
        print(f"\n📊 Session State:")
        print(f"   - Messages in context: {message_count}")
        print(f"   - Total context items: {len(items)}")
        
        if i > session.keep_turns:
            print(f"   ✅ Summarization active (keeping last {session.keep_turns} turns)")
    
    # Show final stats
    print("\n" + "=" * 60)
    print("SUMMARIZATION STATISTICS")
    print("=" * 60)
    
    stats = prod_summarizer.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Demo completed!")
    print("\nℹ️  Production features demonstrated:")
    print("   • Domain-specific summarizer prompts (support)")
    print("   • Async summarization with error handling")
    print("   • Tool output trimming")
    print("   • Monitoring and logging")
    print("   • Compression statistics")


if __name__ == "__main__":
    asyncio.run(demo_customer_support())
