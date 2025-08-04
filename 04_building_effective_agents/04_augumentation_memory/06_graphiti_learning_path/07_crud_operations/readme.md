# Step 07: CRUD Operations - Direct Node and Edge Manipulation

Now that you've mastered search, let's learn how to directly create, read, update, and delete nodes and edges for precise knowledge graph management.

## 📚 Official Documentation

- [CRUD Operations](https://help.getzep.com/graphiti/working-with-data/crud-operations) - Complete guide to node and edge manipulation

## 🎯 What You'll Learn

By the end of this step, you will:
- Master Create, Read, Update, Delete operations on nodes and edges
- Understand when to use CRUD vs episodes for knowledge management
- Implement precise knowledge graph maintenance for educational systems
- Handle relationship lifecycle management in learning contexts
- Design integration patterns with external educational systems

## 📋 Prerequisites

- Completed Steps 01-06
- Understanding of search and namespacing
- Knowledge of node and edge concepts

## 📚 What are CRUD Operations?

### The Concept

**CRUD Operations** provide direct control over your knowledge graph structure, allowing you to manipulate individual nodes and edges without going through episode processing.

**CRUD vs Episodes:**
- **Episodes**: Natural language content processed by LLMs to extract entities and relationships
- **CRUD**: Direct manipulation of known entities and relationships with precise control

### When to Use CRUD Operations

**Use CRUD for:**
- **Precise Updates**: Modify specific student progress markers or grades
- **Relationship Management**: Add/remove course prerequisites dynamically  
- **Data Correction**: Fix incorrect entity attributes or relationships
- **Bulk Operations**: Efficiently update large sets of related entities
- **System Integration**: Sync with external systems (LMS, SIS, databases)
- **Real-time Updates**: Immediate updates without LLM processing overhead

### Core CRUD Classes

Graphiti provides several classes for direct graph manipulation:

```python
from graphiti_core.nodes import EntityNode, EntityEdge

# EntityNode: Represents domain entities (Student, Course, Concept)
# EntityEdge: Represents domain relationships (ENROLLED_IN, PREREQUISITE_FOR)
```

### Basic CRUD Operations

**Create**: Add new nodes and edges
**Read**: Retrieve existing nodes and edges by UUID
**Update**: Modify attributes of existing nodes and edges
**Delete**: Remove nodes and edges (use with caution in educational contexts)

## 🚀 Complete Working Example

Let's implement comprehensive CRUD operations for educational knowledge management:

### crud_demo.py

```python
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional
import uuid
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, EntityEdge

# Gemini setup (same as previous steps)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Comprehensive CRUD operations for educational knowledge management"""
    
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
        print("✏️ Starting Educational CRUD Operations Demo...")
        
        # CREATE Operations
        print("\n📝 CREATE: Adding entities and relationships directly...")
        
        # Create student entity
        student_uuid = str(uuid.uuid4())
        student_node = EntityNode(
            uuid=student_uuid,
            name="Sarah Chen",
            group_id="university_cs_fall2024",
            created_at=datetime.now(),
            summary="Computer Science student with strong analytical skills",
            attributes={
                "student_id": "CS2024001",
                "major": "Computer Science",
                "year": "Sophomore", 
                "gpa": 3.5,
                "learning_style": "Visual",
                "enrollment_date": "2024-08-28"
            }
        )
        
        # Save student to graph
        await student_node.save(graphiti.driver)
        print(f"   ✅ Created student: {student_node.name} (UUID: {student_uuid[:8]}...)")
        
        # Create course entity
        course_uuid = str(uuid.uuid4())
        course_node = EntityNode(
            uuid=course_uuid,
            name="CS102 Data Structures",
            group_id="university_cs_fall2024",
            created_at=datetime.now(),
            summary="Intermediate computer science course covering data structures and algorithms",
            attributes={
                "course_code": "CS102",
                "credits": 4,
                "difficulty": "Intermediate",
                "department": "Computer Science",
                "prerequisites": ["CS101"],
                "max_enrollment": 50
            }
        )
        
        await course_node.save(graphiti.driver)
        print(f"   ✅ Created course: {course_node.name} (UUID: {course_uuid[:8]}...)")
        
        # Create instructor entity
        instructor_uuid = str(uuid.uuid4())
        instructor_node = EntityNode(
            uuid=instructor_uuid,
            name="Dr. Maria Rodriguez",
            group_id="university_cs_fall2024",
            created_at=datetime.now(),
            summary="Computer Science professor specializing in algorithms and data structures",
            attributes={
                "employee_id": "PROF001",
                "department": "Computer Science",
                "title": "Associate Professor",
                "years_experience": 12,
                "specialization": "Algorithms and Data Structures",
                "office": "CS Building 301"
            }
        )
        
        await instructor_node.save(graphiti.driver)
        print(f"   ✅ Created instructor: {instructor_node.name} (UUID: {instructor_uuid[:8]}...)")
        
        # Create enrollment relationship
        enrollment_uuid = str(uuid.uuid4())
        enrollment_edge = EntityEdge(
            uuid=enrollment_uuid,
            source_node_uuid=student_uuid,
            target_node_uuid=course_uuid,
            group_id="university_cs_fall2024",
            created_at=datetime.now(),
            name="ENROLLED_IN",
            fact=f"Sarah Chen enrolled in CS102 Data Structures",
            attributes={
                "enrollment_date": datetime.now().isoformat(),
                "status": "Active",
                "semester": "Fall 2024",
                "section": "001"
            }
        )
        
        await enrollment_edge.save(graphiti.driver)
        print(f"   ✅ Created enrollment relationship (UUID: {enrollment_uuid[:8]}...)")
        
        # Create teaching relationship
        teaching_uuid = str(uuid.uuid4())
        teaching_edge = EntityEdge(
            uuid=teaching_uuid,
            source_node_uuid=instructor_uuid,
            target_node_uuid=course_uuid,
            group_id="university_cs_fall2024",
            created_at=datetime.now(),
            name="TEACHES",
            fact=f"Dr. Maria Rodriguez teaches CS102 Data Structures",
            attributes={
                "semester": "Fall 2024",
                "section": "001",
                "class_size": 25,
                "schedule": "MWF 10:00-11:00"
            }
        )
        
        await teaching_edge.save(graphiti.driver)
        print(f"   ✅ Created teaching relationship (UUID: {teaching_uuid[:8]}...)")
        
        # READ Operations
        print("\n📖 READ: Retrieving entities and relationships...")
        
        # Retrieve student by UUID
        retrieved_student = await EntityNode.get_by_uuid(graphiti.driver, student_uuid)
        if retrieved_student:
            print(f"   📚 Retrieved student: {retrieved_student.name}")
            print(f"      Major: {retrieved_student.attributes.get('major')}")
            print(f"      GPA: {retrieved_student.attributes.get('gpa')}")
        
        # Retrieve course by UUID
        retrieved_course = await EntityNode.get_by_uuid(graphiti.driver, course_uuid)
        if retrieved_course:
            print(f"   📚 Retrieved course: {retrieved_course.name}")
            print(f"      Credits: {retrieved_course.attributes.get('credits')}")
            print(f"      Prerequisites: {retrieved_course.attributes.get('prerequisites')}")
        
        # Retrieve enrollment relationship
        retrieved_enrollment = await EntityEdge.get_by_uuid(graphiti.driver, enrollment_uuid)
        if retrieved_enrollment:
            print(f"   📚 Retrieved enrollment: {retrieved_enrollment.name}")
            print(f"      Status: {retrieved_enrollment.attributes.get('status')}")
            print(f"      Semester: {retrieved_enrollment.attributes.get('semester')}")
        
        # UPDATE Operations
        print("\n✏️ UPDATE: Modifying entities and relationships...")
        
        # Update student progress
        if retrieved_student:
            retrieved_student.attributes["gpa"] = 3.7
        retrieved_student.attributes["courses_completed"] = 3
            retrieved_student.attributes["last_updated"] = datetime.now().isoformat()
            retrieved_student.summary = "Computer Science student with strong analytical skills and improving GPA"
            
            await retrieved_student.save(graphiti.driver)
            print(f"   ✅ Updated student GPA: {retrieved_student.attributes['gpa']}")
        
        # Update course enrollment count
        if retrieved_course:
            retrieved_course.attributes["current_enrollment"] = 26
            retrieved_course.attributes["last_updated"] = datetime.now().isoformat()
            
            await retrieved_course.save(graphiti.driver)
            print(f"   ✅ Updated course enrollment: {retrieved_course.attributes['current_enrollment']}")
        
        # Update enrollment status (e.g., add midterm grade)
        if retrieved_enrollment:
            retrieved_enrollment.attributes["midterm_grade"] = "B+"
            retrieved_enrollment.attributes["attendance_rate"] = 0.95
            retrieved_enrollment.attributes["last_updated"] = datetime.now().isoformat()
            
            await retrieved_enrollment.save(graphiti.driver)
            print(f"   ✅ Updated enrollment with midterm grade: {retrieved_enrollment.attributes['midterm_grade']}")
        
        # Demonstrate bulk update operations
        print("\n📦 BULK OPERATIONS: Efficient batch updates...")
        
        # Create multiple assessment records
        assessment_uuids = []
        for i in range(3):
            assessment_uuid = str(uuid.uuid4())
            assessment_edge = EntityEdge(
                uuid=assessment_uuid,
                source_node_uuid=student_uuid,
                target_node_uuid=course_uuid,
                group_id="university_cs_fall2024",
                created_at=datetime.now(),
                name="COMPLETED_ASSESSMENT",
                fact=f"Sarah Chen completed Quiz {i+1} in CS102",
                attributes={
                    "assessment_type": "Quiz",
                    "assessment_number": i + 1,
                    "score": 85 + (i * 5),  # Improving scores
                    "max_score": 100,
                    "completion_date": (datetime.now() - timedelta(days=20-i*7)).isoformat()
                }
            )
            
            await assessment_edge.save(graphiti.driver)
            assessment_uuids.append(assessment_uuid)
            print(f"   ✅ Created assessment {i+1}: Score {assessment_edge.attributes['score']}/100")
        
        # Integration with External Systems
        print("\n🔗 INTEGRATION: Syncing with external educational systems...")
        
        # Simulate LMS grade sync
        lms_grades = [
            {"student_id": "CS2024001", "assignment": "Homework 1", "score": 92},
            {"student_id": "CS2024001", "assignment": "Homework 2", "score": 88},
            {"student_id": "CS2024001", "assignment": "Project 1", "score": 95}
        ]
        
        for grade_record in lms_grades:
            grade_uuid = str(uuid.uuid4())
            grade_edge = EntityEdge(
                uuid=grade_uuid,
                source_node_uuid=student_uuid,
                target_node_uuid=course_uuid,
                group_id="university_cs_fall2024",
                created_at=datetime.now(),
                name="RECEIVED_GRADE",
                fact=f"Sarah Chen received {grade_record['score']} on {grade_record['assignment']}",
                attributes={
                    "assignment_name": grade_record['assignment'],
                    "score": grade_record['score'],
                    "max_score": 100,
                    "source_system": "LMS",
                    "sync_date": datetime.now().isoformat()
                }
            )
            
            await grade_edge.save(graphiti.driver)
            print(f"   ✅ Synced from LMS: {grade_record['assignment']} - {grade_record['score']}/100")
        
        # Safe archiving instead of deletion
        print("\n🗄️ ARCHIVING: Safe data management (instead of deletion)...")
        
        # Archive a completed assessment (don't delete - preserve for analytics)
        if assessment_uuids:
            archived_assessment = await EntityEdge.get_by_uuid(graphiti.driver, assessment_uuids[0])
            if archived_assessment:
                archived_assessment.attributes["status"] = "Archived"
                archived_assessment.attributes["archived_date"] = datetime.now().isoformat()
                archived_assessment.attributes["archive_reason"] = "Semester completed"
                
                await archived_assessment.save(graphiti.driver)
                print(f"   ✅ Archived assessment (preserved for historical analysis)")
        
        # Verify all operations with search
        print("\n🔍 VERIFICATION: Confirming CRUD operations with search...")
        
        verification_search = await graphiti.search(
            query="Sarah Chen CS102 grades assignments progress",
            group_id="university_cs_fall2024"
        )
        
        print(f"   📊 Verification search found {len(verification_search)} results:")
        for i, result in enumerate(verification_search[:5], 1):
            print(f"     {i}. {result.fact}")
        
        print("\n✅ Educational CRUD operations demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during CRUD operations: {e}")
        print("\n🔧 Troubleshooting CRUD operations:")
        print("   1. Verify database connection and permissions")
        print("   2. Check UUID formats and entity relationships")
        print("   3. Ensure required attributes are properly set")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

1. **Save the code** as `crud_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python crud_demo.py
```

## 📊 Expected Output

```
✏️ Starting Educational CRUD Operations Demo...

📝 CREATE: Adding entities and relationships directly...
   ✅ Created student: Sarah Chen (UUID: a1b2c3d4...)
   ✅ Created course: CS102 Data Structures (UUID: e5f6g7h8...)
   ✅ Created instructor: Dr. Maria Rodriguez (UUID: i9j0k1l2...)
   ✅ Created enrollment relationship (UUID: m3n4o5p6...)
   ✅ Created teaching relationship (UUID: q7r8s9t0...)

📖 READ: Retrieving entities and relationships...
   📚 Retrieved student: Sarah Chen
      Major: Computer Science
      GPA: 3.5
   📚 Retrieved course: CS102 Data Structures
      Credits: 4
      Prerequisites: ['CS101']
   📚 Retrieved enrollment: ENROLLED_IN
      Status: Active
      Semester: Fall 2024

✏️ UPDATE: Modifying entities and relationships...
   ✅ Updated student GPA: 3.7
   ✅ Updated course enrollment: 26
   ✅ Updated enrollment with midterm grade: B+

📦 BULK OPERATIONS: Efficient batch updates...
   ✅ Created assessment 1: Score 85/100
   ✅ Created assessment 2: Score 90/100
   ✅ Created assessment 3: Score 95/100

🔗 INTEGRATION: Syncing with external educational systems...
   ✅ Synced from LMS: Homework 1 - 92/100
   ✅ Synced from LMS: Homework 2 - 88/100
   ✅ Synced from LMS: Project 1 - 95/100

🗄️ ARCHIVING: Safe data management (instead of deletion)...
   ✅ Archived assessment (preserved for historical analysis)

🔍 VERIFICATION: Confirming CRUD operations with search...
   📊 Verification search found 8 results:
     1. Sarah Chen enrolled in CS102 Data Structures
     2. Sarah Chen completed Quiz 1 in CS102
     3. Sarah Chen received 92 on Homework 1
     4. Dr. Maria Rodriguez teaches CS102 Data Structures
     5. Sarah Chen's GPA improved to 3.7

✅ Educational CRUD operations demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Student Transfer Management

Implement a student transfer workflow:

```python
async def transfer_student(student_uuid: str, from_course_uuid: str, to_course_uuid: str):
    """Transfer student between courses with history preservation"""
    
    # Read current enrollment
    current_enrollment = await find_enrollment(student_uuid, from_course_uuid)
    
    if current_enrollment:
        # Update old enrollment status
        current_enrollment.attributes["status"] = "Transferred"
        current_enrollment.attributes["transfer_date"] = datetime.now().isoformat()
        await current_enrollment.save(graphiti.driver)
        
        # Create new enrollment
        new_enrollment = EntityEdge(
            uuid=str(uuid.uuid4()),
            source_node_uuid=student_uuid,
            target_node_uuid=to_course_uuid,
            name="ENROLLED_IN",
            fact=f"Student transferred to new course",
            attributes={
                "enrollment_date": datetime.now().isoformat(),
                "status": "Active",
                "transfer_from": from_course_uuid
            }
        )
        await new_enrollment.save(graphiti.driver)
        
        print(f"✅ Student transferred successfully")

# Usage
await transfer_student(student_uuid, old_course_uuid, new_course_uuid)
```

### Exercise 2: Bulk Grade Updates

Implement efficient bulk grade updates from external systems:

```python
async def bulk_grade_update(grade_records: list):
    """Efficiently update multiple student grades"""
    
    updated_count = 0
    
    for record in grade_records:
        try:
            # Find existing grade edge or create new one
            grade_edge = await find_or_create_grade_edge(
                student_uuid=record['student_uuid'],
                course_uuid=record['course_uuid'],
                assignment=record['assignment']
            )
            
            # Update grade information
            grade_edge.attributes.update({
                'score': record['score'],
                'max_score': record.get('max_score', 100),
                'graded_date': record.get('graded_date', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat()
            })
            
            await grade_edge.save(graphiti.driver)
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update grade for {record}: {e}")
    
    print(f"✅ Updated {updated_count} grades successfully")

# Usage
grade_data = [
    {"student_uuid": "...", "course_uuid": "...", "assignment": "Midterm", "score": 87},
    {"student_uuid": "...", "course_uuid": "...", "assignment": "Final", "score": 92}
]
await bulk_grade_update(grade_data)
```

### Exercise 3: Safe Delete Patterns

Implement archiving instead of deletion:

```python
async def safe_archive_student(student_uuid: str, reason: str = "Graduation"):
    """Archive student instead of deleting to preserve relationships"""
    
    student = await EntityNode.get_by_uuid(graphiti.driver, student_uuid)
    if student:
        # Update student status to archived
        student.attributes.update({
            'status': 'Archived',
            'archived_date': datetime.now().isoformat(),
            'archive_reason': reason,
            'original_status': student.attributes.get('status', 'Active')
        })
        
        await student.save(graphiti.driver)
        
        # Archive all related enrollments
        enrollments = await find_student_enrollments(student_uuid)
        for enrollment in enrollments:
            enrollment.attributes.update({
                'status': 'Archived',
                'archived_date': datetime.now().isoformat()
            })
            await enrollment.save(graphiti.driver)
        
        print(f"✅ Archived student {student.name} and {len(enrollments)} enrollments")

# Usage
await safe_archive_student(student_uuid, "Graduation")
```

## 🎯 Key Concepts Explained

### CRUD vs Episodes Decision Matrix

| Use CRUD When | Use Episodes When |
|---------------|-------------------|
| Precise updates needed | Natural language content |
| External system integration | LLM processing beneficial |
| Real-time performance critical | Rich context extraction needed |
| Known entity relationships | Unstructured information |
| Bulk operations required | Semantic relationship discovery |

### Best Practices for Educational CRUD

1. **Preserve History**: Archive instead of delete for educational compliance
2. **Validate Relationships**: Ensure referential integrity between students, courses, etc.
3. **Batch Operations**: Use bulk updates for performance with large datasets
4. **Audit Trails**: Track all modifications with timestamps and reasons
5. **Error Handling**: Implement robust error handling for system integration

### Integration Patterns

**LMS Integration**: Sync grades, assignments, and enrollment status
**SIS Integration**: Update student information, course catalogs, and schedules
**Assessment Systems**: Import quiz results, project scores, and feedback
**Analytics Platforms**: Export learning analytics and performance metrics

## ✅ Verification Checklist

- [ ] Create operations working for nodes and edges
- [ ] Read operations retrieving entities by UUID
- [ ] Update operations modifying attributes correctly
- [ ] Bulk operations implemented for efficiency
- [ ] Integration patterns demonstrated with external systems
- [ ] Safe archiving patterns instead of deletion

## 🤔 Common Questions

**Q: When should I use CRUD instead of episodes?**
A: Use CRUD for precise updates, system integration, and when you know exact entities and relationships. Use episodes for natural language content requiring LLM processing.

**Q: How do I handle referential integrity?**
A: Always verify that referenced UUIDs exist before creating relationships, and use transactions when creating multiple related entities.

**Q: Should I ever delete educational data?**
A: Rarely. Archive data instead to preserve learning history and comply with educational record-keeping requirements.

**Q: How do I handle concurrent updates?**
A: Implement optimistic locking by checking timestamps before updates, and handle conflicts gracefully.

## 📝 What You Learned

✅ **Direct Graph Control**: Created, read, updated entities and relationships with precision
✅ **Educational Data Management**: Implemented student, course, and instructor management patterns
✅ **System Integration**: Synced with external educational systems (LMS, SIS)
✅ **Bulk Operations**: Efficiently handled large-scale data updates
✅ **Safe Data Practices**: Archived instead of deleting for compliance and analytics

## 🎯 Next Steps

**Excellent work!** You now have surgical precision in knowledge graph management for educational systems.

**Ready to create structured knowledge directly?** Continue to **[08_fact_triples](../08_fact_triples/)** where you'll learn to assert precise facts using subject-predicate-object triples.

**What's Coming**: Instead of natural language processing, you'll learn to directly assert structured knowledge relationships for curriculum modeling and assessment integration!

---

**Key Takeaway**: CRUD operations give you surgical precision in knowledge graph management. Use them for integration, correction, and dynamic updates while preserving the temporal story told by episodes! 🔧

*"With great power comes great responsibility - use CRUD operations wisely to maintain data integrity and educational compliance."*