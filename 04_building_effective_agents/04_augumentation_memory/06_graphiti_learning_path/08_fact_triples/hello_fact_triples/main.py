import asyncio
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode
from graphiti_core.edges import EntityEdge

# Gemini setup (same as previous steps)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Educational fact triple modeling demonstration"""
    
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
        print("📐 Starting Educational Fact Triples Demo...")
        
        namespace = "university_cs_curriculum_2024"
        
        # Create curriculum concepts
        print("\n📚 Creating programming concepts...")
        
        # Variables concept
        variables_uuid = str(uuid.uuid4())
        variables_node = EntityNode(
            uuid=variables_uuid,
            name="Variables",
            group_id=namespace,
            created_at=datetime.now(),
            summary="Basic programming concept for storing data values",
            attributes={"difficulty": "Beginner", "domain": "Programming"}
        )
        
        # Loops concept
        loops_uuid = str(uuid.uuid4())
        loops_node = EntityNode(
            uuid=loops_uuid,
            name="Loops",
            group_id=namespace,
            created_at=datetime.now(),
            summary="Programming concept for repetitive execution",
            attributes={"difficulty": "Intermediate", "domain": "Programming"}
        )
        
        print("   ✅ Created Variables and Loops concepts")
        
        # Create prerequisite relationship using fact triple
        print("\n🔗 Creating prerequisite relationship...")
        
        prereq_uuid = str(uuid.uuid4())
        prereq_edge = EntityEdge(
            uuid=prereq_uuid,
            source_node_uuid=variables_uuid,
            target_node_uuid=loops_uuid,
            group_id=namespace,
            created_at=datetime.now(),
            name="PREREQUISITE_FOR",
            fact="Variables is a prerequisite for Loops",
            attributes={
                "relationship_type": "Prerequisite",
                "strength": "Required"
            }
        )
        
        # Add the fact triple - this handles embeddings automatically!
        res0 = await graphiti.add_triplet(variables_node, prereq_edge, loops_node)
        print("   ✅ Variables → PREREQUISITE_FOR → Loops", res0)
        
        # Create student and mastery relationship
        print("\n👨‍🎓 Creating student mastery relationship...")
        
        # Student entity
        student_uuid = str(uuid.uuid4())
        student_node = EntityNode(
            uuid=student_uuid,
            name="Alice Chen",
            group_id=namespace,
            created_at=datetime.now(),
            summary="Computer Science student",
            attributes={"student_id": "CS2024001", "level": "Sophomore"}
        )
        
        # Mastery relationship
        mastery_uuid = str(uuid.uuid4())
        mastery_edge = EntityEdge(
            uuid=mastery_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=variables_uuid,
            group_id=namespace,
            created_at=datetime.now(),
            name="MASTERED",
            fact="Alice Chen mastered Variables concept",
            attributes={
                "proficiency_score": 95,
                "assessment_date": datetime.now().isoformat()
            }
        )
        
        res1 = await graphiti.add_triplet(student_node, mastery_edge, variables_node)
        print("   ✅ Alice Chen → MASTERED → Variables (Score: 95)", res1)
        
        # Create assessment and completion relationship
        print("\n📊 Creating assessment completion relationship...")
        
        # Assessment entity
        assessment_uuid = str(uuid.uuid4())
        assessment_node = EntityNode(
            uuid=assessment_uuid,
            name="Variables Quiz",
            group_id=namespace,
            created_at=datetime.now(),
            summary="Quiz assessing variable concepts",
            attributes={"assessment_type": "Quiz", "max_score": 100}
        )
        
        # Completion relationship
        completion_uuid = str(uuid.uuid4())
        completion_edge = EntityEdge(
            uuid=completion_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=assessment_uuid,
            group_id=namespace,
            created_at=datetime.now(),
            name="COMPLETED",
            fact="Alice Chen completed Variables Quiz with score 92",
            attributes={
                "score": 92,
                "completion_date": datetime.now().isoformat(),
                "grade": "A"
            }
        )
        
        res2 = await graphiti.add_triplet(student_node, completion_edge, assessment_node)
        print("   ✅ Alice Chen → COMPLETED → Variables Quiz (Score: 92)", res2)
        
        # Validate with search
        print("\n🔍 Validating fact triples with search...")
        
        search_results = await graphiti.search(
            query="Alice Chen Variables mastery prerequisite programming concepts",
            group_ids=[namespace]
        )
        
        print(f"   📊 Found {len(search_results)} results:")
        for i, result in enumerate(search_results[:4], 1):
            print(f"     {i}. {result.fact}")
        
        print("\n✅ Educational fact triples demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())