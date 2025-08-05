import asyncio
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

# === CUSTOM ENTITY TYPES (Based on Student Memory Types) ===

class Student(BaseModel):
    """A learner with memory capabilities"""
    learning_style: str | None = Field(None, description="Visual, auditory, kinesthetic, etc.")
    memory_preference: str | None = Field(None, description="Episodic, semantic, procedural")

class MemoryEvent(BaseModel):
    """A specific learning experience or memory"""
    memory_type: str | None = Field(None, description="STM, episodic, semantic, procedural")
    importance_level: str | None = Field(None, description="High, medium, low")

# === CUSTOM EDGE TYPES ===

class MemoryFormation(BaseModel):
    """Student forms memory relationship"""
    formation_date: str | None = Field(None, description="When memory was formed")
    retention_strength: str | None = Field(None, description="Strong, moderate, weak")

async def main():
    """Complete example using custom educational types"""
    
    # Initialize Graphiti (same setup as previous steps)
    graphiti = Graphiti(
        os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
        os.environ.get('NEO4J_USER', 'neo4j'),
        os.environ.get('NEO4J_PASSWORD', 'password'),
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash"
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
                model="gemini-2.0-flash-exp"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🎓 Starting Custom Types Demo...")
        
        # Define our custom type mappings (memory-focused!)
        entity_types = {
            "Student": Student,
            "MemoryEvent": MemoryEvent
        }
        
        edge_types = {
            "MemoryFormation": MemoryFormation
        }
        
        # Define which edge types can exist between entity types
        edge_type_map = {
            ("Student", "MemoryEvent"): ["MemoryFormation"],
            ("Entity", "Entity"): ["RELATES_TO"]  # Fallback for unexpected relationships
        }
        
        # 1. SINGLE MEMORY FORMATION EPISODE with custom types
        print("\n🧠 Adding one memory formation episode...")
        await graphiti.add_episode(
            name="alice_memory_formation",
            episode_body=(
                "Alice Chen is a visual learner who prefers episodic memory formation. "
                "She formed a strong procedural memory about Python loops on October 15, 2024. "
                "This was a high-importance memory event that showed strong retention strength."
            ),
            source=EpisodeType.text,
            source_description="Student memory formation example",
            reference_time=datetime.now() - timedelta(days=30),
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map
        )
        
        print("✅ Episode with custom types added!")
        
        # SEARCH WITH CUSTOM TYPES
        print("\n🔍 Searching for custom type results...")
        
        # Simple search to see our memory-based custom types in action
        results = await graphiti.search(
            query="Alice Chen memory formation procedural episodic learning visual",
            num_results=6
        )
        
        print(f"\n🎯 Custom Type Results: {len(results)} found")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.fact}")
        
        print("\n🎓 Custom types demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   1. Verify Pydantic models are properly defined")
        print("   2. Check that entity_types and edge_types dictionaries are correct")
        print("   3. Ensure edge_type_map covers your expected relationships")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())