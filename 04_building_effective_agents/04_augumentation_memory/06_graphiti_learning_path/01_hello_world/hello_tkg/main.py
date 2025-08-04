# 1. Import necessary libraries
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.edges import EntityEdge
# 2. Imports for Gemini integration
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

# 3. Load environment variables
# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

# Neo4j connection parameters
# Make sure Neo4j Desktop is running with a local DBMS started
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

gemini_api_key = os.environ.get('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError('GEMINI_API_KEY must be set')

async def main():
    # Initialize Graphiti with Neo4j connection
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password,
                            llm_client=GeminiClient(
        config=LLMConfig(
            api_key=gemini_api_key,
            model="gemini-2.0-flash"
        )
    ),
    embedder=GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=gemini_api_key,
            embedding_model="embedding-001"
        )
    ),
    cross_encoder=GeminiRerankerClient(
        config=LLMConfig(
            api_key=gemini_api_key,
            model="gemini-2.0-flash-exp"
        )
    )

                        )

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()
        
        # Additional code will go here
        # Add your first episode - a simple text about AI learning
        print("📝 Adding your first episode...")
        await graphiti.add_episode(
            name="hello_world_episode",
            episode_body=(
                "Today I started learning Graphiti, a powerful Python framework for "
                "building temporal knowledge graphs. Graphiti helps AI agents remember "
                "information over time and understand how relationships evolve."
            ),
            source=EpisodeType.text,
            source_description="Learning journal entry",
            reference_time=datetime.now(),
        )

        print("✅ Episode added successfully!")

        # Verify the graph has data
        print("🔍 Verifying the knowledge graph...")

        # Search for information about Graphiti
        search_results: list[EntityEdge] = await graphiti.search(
            query="What is Graphiti?",
            num_results=3
        )


        print(f"🎉 Found {len(search_results)} results")

        # data nodes
        for i, data in enumerate(search_results):
            print(f"  {i}:\nUUID: {data.episodes}")
            print(f"  Fact: {data.fact}")
            print("\n")
            
        # Challenge: [Do Node Search](https://help.getzep.com/graphiti/getting-started/quick-start#node-search-using-search-recipes)
        print("CHALLENGE: Do Node Search using search recipes")

        # Use a predefined search configuration recipe and modify its limit
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5  # Limit to 5 results

        # Execute the node search
        node_search_results = await graphiti._search(
            query='Python Framework',
            config=node_search_config,
        )

        # Print node search results
        print('\nNode Search Results:')
        for node in node_search_results.nodes:
            print(f'Node UUID: {node.uuid}')
            print(f'Node Name: {node.name}')
            node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
            print(f'Content Summary: {node_summary}')
            print(f"Node Labels: {', '.join(node.labels)}")
            print(f'Created At: {node.created_at}')
            if hasattr(node, 'attributes') and node.attributes:
                print('Attributes:')
                for key, value in node.attributes.items():
                    print(f'  {key}: {value}')
            print('---')

    finally:
        # Close the connection
        await graphiti.close()
        print('\nConnection closed')

        pass

if __name__ == '__main__':
    asyncio.run(main())
