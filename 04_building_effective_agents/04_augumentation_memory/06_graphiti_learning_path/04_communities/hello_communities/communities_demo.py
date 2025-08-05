import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Build communities and explore them manually in Neo4j"""
    
    # Initialize Graphiti (same setup as previous steps)
    graphiti = Graphiti(
        os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
        os.environ.get('NEO4J_USER', 'neo4j'),
        os.environ.get('NEO4J_PASSWORD', 'password'),
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.5-flash"
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🏘️ Communities Demo - Building Knowledge Graph...")
        
        # Add just 4 simple episodes to create communities
        episodes = [
            "Alice and Bob are both learning Python programming together.",
            "Alice is helping Charlie connect Python to web backends.", 
            "Bob and Diana are collaborating on a full-stack project."
        ]
        
        print("\n📝 Adding episodes...")
        for i, episode in enumerate(episodes):
            print(f"episode_{i+1}\n")
            await graphiti.add_episode(
                name=f"episode_{i+1}",
                episode_body=episode,
                source=EpisodeType.text,
                source_description="Engineers Collaboration",
                reference_time=datetime.now() - timedelta(days=i)
            )
        
        print("✅ Episodes added!")
        await asyncio.sleep(60)  # Small delay for clarity
        print("\n🔍 Exploring communities...")
        # Build communities to see patterns
        print("\n🔍 Building communities...")
        res = await graphiti.build_communities()
        print("✅ Communities built!")
        
        print(f"Communities found: \n\n {res}\n\n\n")
        print("\n🎓 Communities demo completed!")
        print("\n👀 Now manually explore your Neo4j database...")
                
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
