import asyncio
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode
from graphiti_core.edges import EntityEdge

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Simple CRUD operations demonstration"""
    
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
        print("✏️ CRUD Operations Demo...")
        
        # 1. CREATE - Add student and course
        print("\n📝 **CREATE**: Adding student and course...")
        
        student_uuid = str(uuid.uuid4())
        student_name = "Alice Chen"
        
        # Generate embedding for the student name
        student_embedding = await graphiti.embedder.create([student_name])
        
        student_node = EntityNode(
            uuid=student_uuid,
            name=student_name,
            group_id="cs101",
            created_at=datetime.now(),
            summary="Computer Science student",
            attributes={"gpa": 3.5, "year": "Sophomore"},
            name_embedding=student_embedding  # Use generated embedding
        )
        await student_node.save(graphiti.driver)
        print(f"   ✅ Created student: {student_name}")
        
        course_uuid = str(uuid.uuid4())
        course_name = "CS101 Programming"
        
        # Generate embedding for the course name
        course_embedding = await graphiti.embedder.create([course_name])
        
        course_node = EntityNode(
            uuid=course_uuid,
            name=course_name,
            group_id="cs101",
            created_at=datetime.now(),
            summary="Introduction to programming",
            attributes={"credits": 4, "difficulty": "Beginner"},
            name_embedding=course_embedding  # Use generated embedding
        )
        await course_node.save(graphiti.driver)
        print(f"   ✅ Created course: {course_name}")
        
        # Create enrollment relationship
        enrollment_uuid = str(uuid.uuid4())
        enrollment_edge = EntityEdge(
            uuid=enrollment_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=course_uuid,
            group_id="cs101",
            created_at=datetime.now(),
            name="ENROLLED_IN",
            fact="Alice Chen enrolled in CS101 Programming",
            attributes={"status": "Active", "grade": None},
            fact_embedding=await graphiti.embedder.create(["Alice Chen enrolled in CS101 Programming"])  # Generate embedding for the fact
        )
        await enrollment_edge.save(graphiti.driver)
        print(f"   ✅ Created enrollment relationship")
        
        # 2. READ - Retrieve what we created
        print("\n📖 **READ**: Retrieving entities...")
        
        retrieved_student = await EntityNode.get_by_uuid(graphiti.driver, student_uuid)
        if retrieved_student:
            print(f"   📚 Found student: {retrieved_student}")
            print(f"      GPA: {retrieved_student.attributes.get('gpa')}")
        
        retrieved_course = await EntityNode.get_by_uuid(graphiti.driver, course_uuid)
        if retrieved_course:
            print(f"   📚 Found course: {retrieved_course}")
            print(f"      Credits: {retrieved_course.attributes.get('credits')}")
        
        retrieved_enrollment = await EntityEdge.get_by_uuid(graphiti.driver, enrollment_uuid)
        if retrieved_enrollment:
            print(f"   📚 Found enrollment: {retrieved_enrollment}")
            print(f"      Status: {retrieved_enrollment.attributes.get('status')}")
        
        # 3. UPDATE - Modify existing data
        print("\n✏️ **UPDATE**: Modifying data...")
        
        # Update student GPA
        if retrieved_student:
            retrieved_student.attributes["gpa"] = 3.8
            retrieved_student.summary = "Computer Science student with improved GPA"

            if retrieved_student.name_embedding is None:
                retrieved_student.name_embedding = await graphiti.embedder.create([retrieved_student.name])
                print("   ⚠️  Warning: name_embedding was None. Regenerated embedding before saving.")

            await retrieved_student.save(graphiti.driver)
            print(f"   ✅ Updated student GPA to: {retrieved_student.attributes['gpa']}")
        
        print("\n👀 Now manually explore CRUD results in Neo4j...")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())