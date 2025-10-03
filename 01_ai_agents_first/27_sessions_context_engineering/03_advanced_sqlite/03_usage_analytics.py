"""
Advanced SQLite Sessions - Usage Analytics

This example demonstrates querying usage analytics from SQLite:
1. Token usage tracking
2. Cost analysis per conversation
3. Performance metrics
4. Conversation statistics

Use Cases:
- Monitoring agent token consumption
- Cost optimization
- Usage reporting for billing
- Performance analysis

Run: python 03_usage_analytics.py
"""

import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import AdvancedSQLiteSession

load_dotenv()


# ============= ANALYTICS QUERIES =============

class UsageAnalytics:
    """
    Query and analyze usage data from AdvancedSQLiteSession database.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def get_total_usage(self) -> Dict[str, Any]:
        """Get total usage across all conversations."""
        self.cursor.execute("""
            SELECT 
                COUNT(DISTINCT conversation_id) as num_conversations,
                COUNT(*) as num_runs,
                SUM(prompt_tokens) as total_prompt_tokens,
                SUM(completion_tokens) as total_completion_tokens,
                SUM(prompt_tokens + completion_tokens) as total_tokens
            FROM usage_logs
        """)
        
        row = self.cursor.fetchone()
        if not row or row[0] == 0:
            return {
                "num_conversations": 0,
                "num_runs": 0,
                "total_tokens": 0,
                "estimated_cost": 0.0
            }
        
        num_conversations, num_runs, prompt_tokens, completion_tokens, total_tokens = row
        
        # Estimate cost (approximate at $0.002/1k tokens)
        cost = (total_tokens / 1000) * 0.002 if total_tokens else 0
        
        return {
            "num_conversations": num_conversations,
            "num_runs": num_runs,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": cost
        }
    
    def get_conversation_usage(self, conversation_id: str) -> Dict[str, Any]:
        """Get usage for specific conversation."""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as num_runs,
                SUM(prompt_tokens) as total_prompt_tokens,
                SUM(completion_tokens) as total_completion_tokens,
                SUM(prompt_tokens + completion_tokens) as total_tokens,
                AVG(prompt_tokens + completion_tokens) as avg_tokens_per_run
            FROM usage_logs
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = self.cursor.fetchone()
        if not row or row[0] == 0:
            return {"error": "No usage data found"}
        
        num_runs, prompt_tokens, completion_tokens, total_tokens, avg_tokens = row
        cost = (total_tokens / 1000) * 0.002 if total_tokens else 0
        
        return {
            "conversation_id": conversation_id,
            "num_runs": num_runs,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "avg_tokens_per_run": avg_tokens,
            "estimated_cost": cost
        }
    
    def get_top_conversations_by_cost(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most expensive conversations."""
        self.cursor.execute("""
            SELECT 
                conversation_id,
                COUNT(*) as num_runs,
                SUM(prompt_tokens + completion_tokens) as total_tokens
            FROM usage_logs
            GROUP BY conversation_id
            ORDER BY total_tokens DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for conversation_id, num_runs, total_tokens in self.cursor.fetchall():
            cost = (total_tokens / 1000) * 0.002
            results.append({
                "conversation_id": conversation_id,
                "num_runs": num_runs,
                "total_tokens": total_tokens,
                "estimated_cost": cost
            })
        
        return results
    
    def get_conversation_count(self) -> int:
        """Get total number of conversations in database."""
        self.cursor.execute("SELECT COUNT(*) FROM conversations")
        return self.cursor.fetchone()[0]
    
    def get_message_count(self) -> int:
        """Get total number of messages stored."""
        self.cursor.execute("SELECT COUNT(*) FROM messages")
        return self.cursor.fetchone()[0]
    
    def get_database_size(self) -> str:
        """Get database file size."""
        import os
        size_bytes = os.path.getsize(self.db_path)
        
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# ============= DEMO: GENERATE SAMPLE DATA =============

async def generate_sample_data(db_path: str):
    """
    Generate sample conversations with usage data for analytics demo.
    """
    print("=" * 60)
    print("GENERATING SAMPLE DATA")
    print("=" * 60)
    
    # Setup model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    runner = Runner()
    
    # Create 3 sample conversations
    conversations = [
        {
            "id": "support-conv-001",
            "agent_name": "SupportAgent",
            "instructions": "You are a customer support agent.",
            "messages": [
                "My order hasn't arrived",
                "It's been 10 days since I placed it",
                "Can you refund me?"
            ]
        },
        {
            "id": "sales-conv-001",
            "agent_name": "SalesAgent",
            "instructions": "You are a sales assistant.",
            "messages": [
                "Tell me about your premium plan",
                "What features does it include?",
                "How much does it cost?",
                "Do you offer annual discounts?",
                "I'll take it"
            ]
        },
        {
            "id": "tech-conv-001",
            "agent_name": "TechSupport",
            "instructions": "You are technical support.",
            "messages": [
                "My app keeps crashing",
                "It happens when I try to upload files",
                "I'm on Windows 11",
                "The file is 50MB, a PDF document"
            ]
        }
    ]
    
    for conv in conversations:
        print(f"\n📝 Creating conversation: {conv['id']}")
        
        session = AdvancedSQLiteSession(
            db_path=db_path,
            conversation_id=conv['id'],
            store_run_usage=True  # Enable usage tracking
        )
        
        agent = Agent(
            name=conv['agent_name'],
            instructions=conv['instructions'],
            model=llm_model,
            session=session
        )
        
        for i, msg in enumerate(conv['messages'], 1):
            print(f"   Turn {i}: {msg[:50]}...")
            await runner.run(agent=agent, input=msg)
    
    print("\n✅ Sample data generated!")


# ============= DEMO: ANALYTICS DASHBOARD =============

async def demo_analytics_dashboard():
    """
    Demonstrate comprehensive analytics dashboard.
    """
    db_path = "analytics_demo.db"
    
    # Generate sample data
    await generate_sample_data(db_path)
    
    print("\n\n" + "=" * 60)
    print("USAGE ANALYTICS DASHBOARD")
    print("=" * 60)
    
    analytics = UsageAnalytics(db_path)
    
    # ===== Overall Stats =====
    print("\n📊 OVERALL USAGE")
    print("─" * 60)
    
    total_usage = analytics.get_total_usage()
    print(f"Total Conversations: {total_usage['num_conversations']}")
    print(f"Total Agent Runs: {total_usage['num_runs']}")
    print(f"Total Tokens: {total_usage.get('total_tokens', 0):,}")
    print(f"  • Prompt tokens: {total_usage.get('prompt_tokens', 0):,}")
    print(f"  • Completion tokens: {total_usage.get('completion_tokens', 0):,}")
    print(f"Estimated Cost: ${total_usage['estimated_cost']:.4f}")
    
    # ===== Database Stats =====
    print("\n💾 DATABASE STATS")
    print("─" * 60)
    
    print(f"Total Conversations: {analytics.get_conversation_count()}")
    print(f"Total Messages: {analytics.get_message_count()}")
    print(f"Database Size: {analytics.get_database_size()}")
    
    # ===== Top Conversations by Cost =====
    print("\n💰 TOP CONVERSATIONS BY COST")
    print("─" * 60)
    
    top_conversations = analytics.get_top_conversations_by_cost(limit=5)
    for i, conv in enumerate(top_conversations, 1):
        print(f"\n{i}. {conv['conversation_id']}")
        print(f"   Runs: {conv['num_runs']}")
        print(f"   Tokens: {conv['total_tokens']:,}")
        print(f"   Cost: ${conv['estimated_cost']:.4f}")
    
    # ===== Per-Conversation Analysis =====
    print("\n\n🔍 PER-CONVERSATION ANALYSIS")
    print("─" * 60)
    
    for conv_id in ["support-conv-001", "sales-conv-001", "tech-conv-001"]:
        print(f"\n📝 {conv_id}:")
        conv_usage = analytics.get_conversation_usage(conv_id)
        
        if "error" in conv_usage:
            print(f"   {conv_usage['error']}")
        else:
            print(f"   Runs: {conv_usage['num_runs']}")
            print(f"   Total tokens: {conv_usage['total_tokens']:,}")
            print(f"   Avg tokens/run: {conv_usage['avg_tokens_per_run']:.0f}")
            print(f"   Cost: ${conv_usage['estimated_cost']:.4f}")
    
    analytics.close()
    
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    
    print("\n✅ Analytics Capabilities Demonstrated:")
    print("   • Total usage across all conversations")
    print("   • Per-conversation cost tracking")
    print("   • Top conversations by cost")
    print("   • Database size monitoring")
    print("   • Average tokens per agent run")
    
    print("\n💡 Use Cases:")
    print("   • Monitor agent costs in production")
    print("   • Identify expensive conversations for optimization")
    print("   • Generate usage reports for billing")
    print("   • Track token consumption trends")
    print("   • Database capacity planning")


# ============= BONUS: CUSTOM ANALYTICS QUERIES =============

def demo_custom_queries():
    """
    Show custom SQL queries for advanced analytics.
    """
    print("\n\n" + "=" * 60)
    print("CUSTOM ANALYTICS QUERIES")
    print("=" * 60)
    
    db_path = "analytics_demo.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Example: Conversation length distribution
    print("\n📊 Conversation Length Distribution:")
    cursor.execute("""
        SELECT 
            CASE 
                WHEN msg_count <= 5 THEN '1-5 messages'
                WHEN msg_count <= 10 THEN '6-10 messages'
                ELSE '11+ messages'
            END as length_category,
            COUNT(*) as num_conversations
        FROM (
            SELECT conversation_id, COUNT(*) as msg_count
            FROM messages
            GROUP BY conversation_id
        )
        GROUP BY length_category
    """)
    
    for category, count in cursor.fetchall():
        print(f"   {category}: {count} conversations")
    
    # Example: Messages per conversation
    print("\n📈 Average Messages per Conversation:")
    cursor.execute("""
        SELECT AVG(msg_count) as avg_messages
        FROM (
            SELECT conversation_id, COUNT(*) as msg_count
            FROM messages
            GROUP BY conversation_id
        )
    """)
    
    avg_messages = cursor.fetchone()[0]
    print(f"   {avg_messages:.1f} messages/conversation")
    
    conn.close()
    
    print("\n✅ Custom queries allow deep analysis of conversation patterns!")


if __name__ == "__main__":
    asyncio.run(demo_analytics_dashboard())
    demo_custom_queries()
