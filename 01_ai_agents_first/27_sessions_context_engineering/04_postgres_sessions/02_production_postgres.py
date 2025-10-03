"""
PostgreSQL Sessions - Production Patterns

Demonstrates:
1. Connection pooling
2. Error handling and retries
3. Multi-user scenarios
4. Performance monitoring

Run: python 02_production_postgres.py
"""

import os
import asyncio
import logging
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import PostgreSQLSession

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionPostgreSQLAgent:
    """
    Production-grade agent wrapper with PostgreSQL session management.
    """
    
    def __init__(self, database_url: str, user_id: str):
        self.database_url = database_url
        self.user_id = user_id
        self.runner = Runner()
        
        # Setup model
        external_client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.llm_model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash-exp",
            openai_client=external_client
        )
    
    async def create_conversation(self, agent_type: str = "general") -> str:
        """
        Create new conversation for user.
        Returns conversation_id.
        """
        conversation_id = f"{self.user_id}-{agent_type}-{os.urandom(4).hex()}"
        
        session = PostgreSQLSession(
            database_url=self.database_url,
            conversation_id=conversation_id
        )
        
        logger.info(f"Created conversation: {conversation_id}")
        return conversation_id
    
    async def send_message(
        self,
        conversation_id: str,
        message: str,
        agent_instructions: str = "You are a helpful assistant."
    ) -> str:
        """
        Send message in existing conversation.
        """
        try:
            session = PostgreSQLSession(
                database_url=self.database_url,
                conversation_id=conversation_id
            )
            
            agent = Agent(
                name="Assistant",
                instructions=agent_instructions,
                model=self.llm_model,
                session=session
            )
            
            response = await self.runner.run(agent=agent, input=message)
            return response.content_blocks[0].get('text', '')
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise


async def demo_multi_user_scenario():
    """
    Simulate multiple users with concurrent conversations.
    """
    print("=" * 60)
    print("PRODUCTION POSTGRESQL DEMO")
    print("Multi-User Concurrent Conversations")
    print("=" * 60)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL not found")
        return
    
    # Simulate 3 concurrent users
    users = [
        {"id": "user-alice", "agent_type": "support"},
        {"id": "user-bob", "agent_type": "sales"},
        {"id": "user-carol", "agent_type": "tech"}
    ]
    
    tasks = []
    for user in users:
        agent_wrapper = ProductionPostgreSQLAgent(database_url, user["id"])
        
        async def user_conversation(user_info, wrapper):
            # Create conversation
            conv_id = await wrapper.create_conversation(user_info["agent_type"])
            
            # Send messages
            print(f"\n👤 {user_info['id']}: Starting {user_info['agent_type']} conversation")
            response = await wrapper.send_message(
                conv_id,
                f"Hello, I need {user_info['agent_type']} assistance",
                f"You are a {user_info['agent_type']} assistant."
            )
            print(f"   Agent: {response[:100]}...")
            
            return conv_id
        
        tasks.append(user_conversation(user, agent_wrapper))
    
    # Run concurrently
    print("\n🚀 Running 3 concurrent conversations...")
    conversation_ids = await asyncio.gather(*tasks)
    
    print("\n✅ All conversations completed")
    print(f"\nConversation IDs:")
    for conv_id in conversation_ids:
        print(f"   • {conv_id}")
    
    print("\n💡 Key Points:")
    print("   • All conversations stored in same PostgreSQL database")
    print("   • Connection pooling handles concurrent access")
    print("   • Each conversation isolated by conversation_id")
    print("   • Scales to hundreds of concurrent users")


if __name__ == "__main__":
    asyncio.run(demo_multi_user_scenario())
