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
    """Simple namespace isolation demo"""
    
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
                model="gemini-2.0-flash-lite"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🏫 Namespacing Demo - Creating Isolated Course Environments...")
        
        # Course A: CS101 
        print("\n📘 Adding CS101 episodes...")
        await graphiti.add_episode(
            name="cs101_alice",
            episode_body="Alice is learning Python basics in CS101. She understands variables and loops.",
            source=EpisodeType.text,
            source_description="CS101 student background",
            group_id="course_cs101",  # CS101 namespace
            reference_time=datetime.now() - timedelta(days=2)
        )
        
        await graphiti.add_episode(
            name="cs101_bob",
            episode_body="Bob is struggling with Python functions in CS101. He needs help with parameters.",
            source=EpisodeType.text,
            source_description="CS101 student background",
            group_id="course_cs101",  # CS101 namespace
            reference_time=datetime.now() - timedelta(days=1)
        )

        await asyncio.sleep(60)
        
        # Course B: MATH201
        print("📗 Adding MATH201 episodes...")
        await graphiti.add_episode(
            name="math201_carol",
            episode_body="Carol is studying calculus in MATH201. She excels at derivatives and integration.",
                source=EpisodeType.text,
            source_description="MATH201 student background",
            reference_time=datetime.now() - timedelta(days=3),
            group_id="course_math201"  # MATH201 namespace
        )
        
        await graphiti.add_episode(
            name="math201_diana",
            episode_body="Diana finds linear algebra challenging in MATH201. She needs help with matrices.",
            source=EpisodeType.text,
            source_description="MATH201 student background",
            reference_time=datetime.now() - timedelta(days=2),
            group_id="course_math201"  # MATH201 namespace
        )
        
        print("✅ Episodes added to separate namespaces!")
        await asyncio.sleep(60)
        
        # Search within CS101 namespace only
        print("\n🔍 Searching within CS101 namespace...")
        cs101_results = await graphiti.search(
            query="programming Python students learning",
            group_ids=["course_cs101"],  # Only search CS101
            num_results=10
        )
        
        print(f"CS101 results: {len(cs101_results)} found")
        for result in cs101_results:
            print(f"  • {result.fact}")
        
        # Search within MATH201 namespace only
        print("\n🔍 Searching within MATH201 namespace...")
        math201_results = await graphiti.search(
            query="mathematics calculus students learning",
            group_ids=["course_math201"],  # Only search MATH201
            num_results=10
        )
        
        print(f"MATH201 results: {len(math201_results)} found")
        for result in math201_results:
            print(f"  • {result.fact}")
        
        # Global search (no group_id) - sees everything
        print("\n🌍 Global search (no namespace restriction)...")
        global_results = await graphiti.search(
            query="students learning",
            num_results=10  # No group_id = search all namespaces
        )
        
        print(f"Global results: {len(global_results)} found")
        for result in global_results:
            print(f"  • {result.fact}")
        
        print("\n🎓 Namespacing demo completed!")
        print("\n👀 Now manually explore namespaces in Neo4j...")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())