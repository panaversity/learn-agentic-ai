import asyncio
import os
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, Node
from graphiti_core.edges import EntityEdge

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

# === CUSTOM ENTITY TYPES (Educational Domain) ===

class Student(BaseModel):
    """A student with learning characteristics"""
    student_id: str = Field(..., description="Unique student identifier")
    learning_style: str | None = Field(None, description="Visual, auditory, kinesthetic")
    gpa: float | None = Field(None, description="Current GPA")
    year: str | None = Field(None, description="Freshman, Sophomore, Junior, Senior")

class Course(BaseModel):
    """An academic course"""
    course_code: str = Field(..., description="Course identifier like CS101")
    credits: int | None = Field(None, description="Credit hours")
    difficulty: str | None = Field(None, description="Beginner, Intermediate, Advanced")
    department: str | None = Field(None, description="Academic department")

class Topic(BaseModel):
    """A learning topic within a course"""
    topic_id: str = Field(..., description="Unique topic identifier")
    complexity_level: int | None = Field(None, description="1-10 complexity scale")
    prerequisites: list[str] | None = Field(None, description="Required prior topics")

# === CUSTOM EDGE TYPES ===

class Enrollment(BaseModel):
    """Student enrollment in course"""
    enrollment_date: str | None = Field(None, description="When enrolled")
    status: str | None = Field(None, description="Active, Completed, Dropped")
    final_grade: str | None = Field(None, description="Final letter grade")

class Covers(BaseModel):
    """Course covers topic relationship"""
    week_number: int | None = Field(None, description="Which week topic is covered")
    importance: str | None = Field(None, description="Core, Supplemental, Optional")

class Mastery(BaseModel):
    """Student mastery of topic"""
    mastery_level: float | None = Field(None, description="0.0-1.0 mastery score")
    assessment_date: str | None = Field(None, description="When mastery was assessed")

async def main():
    """CRUD operations with custom educational entity types"""
    
    # Initialize Graphiti
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
    
    # Register custom types
    entity_types = [Student, Course, Topic]
    edge_types = [Enrollment, Covers, Mastery]
    
    # Build the edge type map
    edge_type_map = {
        ("Student", "Course"): [Enrollment],
        ("Course", "Topic"): [Covers], 
        ("Student", "Topic"): [Mastery]
    }
    
    try:
        await graphiti.build_indices_and_constraints(True)
        
        # Configure custom types
        graphiti.entity_types = entity_types
        graphiti.relation_types = edge_types
        graphiti.edge_type_map = edge_type_map
        
        print("🎓 **CRUD Operations with Custom Educational Types**")
        
        # === CREATE: Custom Entity Nodes ===
        print("\n📝 **CREATE**: Adding custom educational entities...")
        
        # Create Student with custom attributes
        student_uuid = str(uuid.uuid4())
        student_data = Student(
            student_id="CS2024001",
            learning_style="Visual",
            gpa=3.5,
            year="Sophomore"
        )
        
        student_node = EntityNode(
            labels=["Student"],
            uuid=student_uuid,
            name="Alice Chen",
            group_id="cs101",
            created_at=datetime.now(),
            summary="Computer Science student specializing in algorithms",
            # Store custom type data in attributes
            attributes=student_data.model_dump(),
            name_embedding=await graphiti.embedder.create([student_data.student_id])  # Generate embedding
        )
        await student_node.save(graphiti.driver)
        print(f"   ✅ Created Student: Alice Chen (ID: {student_data.student_id})")
        
        # Create Course with custom attributes
        course_uuid = str(uuid.uuid4())
        course_data = Course(
            course_code="CS101",
            credits=4,
            difficulty="Beginner",
            department="Computer Science"
        )
        
        course_node = EntityNode(
            uuid=course_uuid,
            name="Introduction to Programming",
            group_id="cs101",
            labels=["Course"],
            created_at=datetime.now(),
            summary="Foundational programming course using Python",
            attributes=course_data.model_dump(),
            name_embedding=await graphiti.embedder.create([course_data.course_code])  # Generate embedding
        )
        await course_node.save(graphiti.driver)
        print(f"   ✅ Created Course: {course_data.course_code} - Introduction to Programming")
        
        # Create Topic with custom attributes
        topic_uuid = str(uuid.uuid4())
        topic_data = Topic(
            topic_id="LOOPS001",
            complexity_level=3,
            prerequisites=["VARIABLES001"]
        )
        
        topic_node = EntityNode(
            uuid=topic_uuid,
            name="Python Loops",
            group_id="cs101",
            labels=["Topic"],
            created_at=datetime.now(),
            summary="For loops, while loops, and iteration concepts",
            attributes=topic_data.model_dump(),
            name_embedding=await graphiti.embedder.create([topic_data.topic_id])  # Generate embedding
        )
        await topic_node.save(graphiti.driver)
        print(f"   ✅ Created Topic: {topic_data.topic_id} - Python Loops")
        
        # === CREATE: Custom Relationship Edges ===
        print("\n🔗 **CREATE**: Adding custom educational relationships...")
        
        # Student enrolls in Course
        enrollment_uuid = str(uuid.uuid4())
        enrollment_data = Enrollment(
            enrollment_date=datetime.now().isoformat(),
            status="Active",
            final_grade=None
        )
        
        enrollment_edge = EntityEdge(
            uuid=enrollment_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=course_uuid,
            group_id="cs101",
            created_at=datetime.now(),
            name="ENROLLED_IN",
            fact="Alice Chen enrolled in CS101 Introduction to Programming",
            attributes=enrollment_data.model_dump(),
            fact_embedding=await graphiti.embedder.create(["Alice Chen enrolled in CS101 Introduction to Programming"])  # Generate embedding
        )
        await enrollment_edge.save(graphiti.driver)
        print(f"   ✅ Created Enrollment: Student → Course ({enrollment_data.status})")
        
        # Course covers Topic
        covers_uuid = str(uuid.uuid4())
        covers_data = Covers(
            week_number=3,
            importance="Core"
        )
        
        covers_edge = EntityEdge(
            uuid=covers_uuid,
            source_node_uuid=course_uuid,
            target_node_uuid=topic_uuid,
            group_id="cs101",
            created_at=datetime.now(),
            
            name="COVERS",
            fact="CS101 covers Python Loops in week 3 as core content",
            attributes=covers_data.model_dump(),
            fact_embedding=await graphiti.embedder.create(["CS101 covers Python Loops in week 3 as core content"])  # Generate embedding
        )
        await covers_edge.save(graphiti.driver)
        print(f"   ✅ Created Coverage: Course → Topic (Week {covers_data.week_number})")
        
        # Student masters Topic
        mastery_uuid = str(uuid.uuid4())
        mastery_data = Mastery(
            mastery_level=0.75,
            assessment_date=datetime.now().isoformat()
        )
        
        mastery_edge = EntityEdge(
            uuid=mastery_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=topic_uuid,
            group_id="cs101",
            created_at=datetime.now(),
            name="MASTERS",
            fact="Alice Chen demonstrates 75% mastery of Python Loops",
            attributes=mastery_data.model_dump(),
            fact_embedding=await graphiti.embedder.create(["Alice Chen demonstrates 75% mastery of Python Loops"])  # Generate embedding
        )
        await mastery_edge.save(graphiti.driver)
        print(f"   ✅ Created Mastery: Student → Topic ({mastery_data.mastery_level:.0%})")
        
        # === READ: Retrieve Custom Entities ===
        print("\n📖 **READ**: Retrieving custom entities...")
        
        retrieved_student = await EntityNode.get_by_uuid(graphiti.driver, student_uuid)
        if retrieved_student:
            student_attrs = Student(**retrieved_student.attributes)
            print(f"   📚 Found Student: {retrieved_student.name}")
            print(f"      Student ID: {student_attrs.student_id}")
            print(f"      Learning Style: {student_attrs.learning_style}")
            print(f"      Current GPA: {student_attrs.gpa}")
        
        retrieved_course = await EntityNode.get_by_uuid(graphiti.driver, course_uuid)
        if retrieved_course:
            course_attrs = Course(**retrieved_course.attributes)
            print(f"   📚 Found Course: {retrieved_course.name}")
            print(f"      Course Code: {course_attrs.course_code}")
            print(f"      Credits: {course_attrs.credits}")
            print(f"      Difficulty: {course_attrs.difficulty}")
        
         
        # === VERIFY: Search for Custom Entities ===
        print("\n🔍 **VERIFY**: Searching for custom educational data...")
        
        search_results = await graphiti.search(
            query="Alice Chen CS101 Python loops mastery grade",
            group_ids=["cs101"]
        )
        
        print(f"   📊 Search found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"     {i}. {result.fact}")
        
        print("\n🎓 **Custom CRUD operations completed successfully!**")
        print("\n👀 **Explore custom entities in Neo4j:**")
        print("   MATCH (n:Entity) WHERE n.group_id = 'cs101' RETURN n.name, n.attributes")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())