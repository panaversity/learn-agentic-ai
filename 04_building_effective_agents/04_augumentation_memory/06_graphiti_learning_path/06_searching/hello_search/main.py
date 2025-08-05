import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_RRF, 
    EDGE_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_RRF
)

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Compare search strategies using the same query"""
    
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
                model="gemini-2.5-flash-lite"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🔍 Search Strategy Comparison Demo...")
        
        # Add simple educational content
        print("\n📚 Adding educational knowledge...")
        
        episodes = [
            "Alice is learning Python programming. She understands variables but struggles with loops.",
            "Bob helps Alice with debugging techniques. He explains step-by-step problem solving.",
            "Carol collaborates with Alice and Bob on programming projects using Python functions.",
            "Variables are fundamental concepts in Python. Loops build on variable understanding."
        ]
        
        for i, episode in enumerate(episodes):
            print(f"episode_{i+1}")
            await graphiti.add_episode(
                name=f"episode_{i+1}",
                episode_body=episode,
                source=EpisodeType.text,
                source_description="Educational content",
                reference_time=datetime.now() - timedelta(days=i),
                group_id="cs101"
            )
            await asyncio.sleep(60)  # Simulate processing time
        
        print("✅ Episodes added!")
        print("\n⏳ Processing for search...")
        await asyncio.sleep(60)
        
        # THE SAME QUERY for all strategies
        QUERY = "Alice learning Python programming"
        print(f"\n🎯 **Comparing all strategies with query: '{QUERY}'**\n")
        
        # Strategy 1: Basic Hybrid Search
        print("📖 **Strategy 1: Basic Hybrid Search**")
        basic_results = await graphiti.search(query=QUERY)
        print(f"   Results: {len(basic_results)} found")
        for i, result in enumerate(basic_results, 1):
            print(f"     {i}. {result.fact}")
        
        # Strategy 2: Node-Focused Search  
        print(f"\n🎯 **Strategy 2: Node-Focused Search (entities/concepts)**")
        node_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_config.limit = 10
        
        node_results = await graphiti._search(query=QUERY, config=node_config)
        print(f"   Nodes found: {len(node_results.nodes)}")
        for i, node in enumerate(node_results.nodes, 1):
            print(f"     {i}. {node.name}")
        
        # Strategy 3: Edge-Focused Search
        print(f"\n🔗 **Strategy 3: Edge-Focused Search (relationships)**")
        edge_config = EDGE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        edge_config.limit = 10
        
        edge_results = await graphiti._search(query=QUERY, config=edge_config)
        print(f"   Relationships found: {len(edge_results.edges)}")
        for i, edge in enumerate(edge_results.edges, 1):
            print(f"     {i}. {edge.source_node_uuid} → {edge.target_node_uuid}")
            print(f"        Type: {edge.name}")
        
        # Strategy 4: Combined Search
        print(f"\n🌍 **Strategy 4: Combined Search (everything)**")
        combined_config = COMBINED_HYBRID_SEARCH_RRF.model_copy(deep=True)
        combined_config.limit = 10
        
        combined_results = await graphiti._search(query=QUERY, config=combined_config)
        print(f"   Nodes: {len(combined_results.nodes)}")
        print(f"   Edges: {len(combined_results.edges)}")  
        print(f"   Communities: {len(combined_results.communities)}")
        
        print("\n🎓 Search comparison completed!")
        print("\n👀 Now manually explore search results in Neo4j...")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())