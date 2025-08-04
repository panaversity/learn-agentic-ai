# Working with Data 02: [CRUD Operations](https://help.getzep.com/graphiti/working-with-data/crud-operations) - Direct Node and Edge Manipulation

Welcome to Step 07! Master direct manipulation of knowledge graph elements.

## 🎯 Learning Objectives

- Master Create, Read, Update, Delete operations on nodes and edges
- Implement precise knowledge graph maintenance for educational systems
- Handle relationship lifecycle management in learning contexts
- Apply CRUD operations for dynamic curriculum updates
- Design knowledge graph maintenance workflows

## 📚 Core Concepts

### Direct Graph Manipulation

Unlike episode-based knowledge creation, CRUD operations provide **direct control** over your knowledge graph structure:

**When to Use CRUD:**
- **Precise Updates**: Modify specific student progress markers
- **Relationship Management**: Add/remove course prerequisites dynamically  
- **Data Correction**: Fix incorrect entity attributes or relationships
- **Bulk Operations**: Efficiently update large sets of related entities
- **Integration**: Sync with external systems (LMS, SIS)

### Graphiti CRUD Classes

```python
from graphiti_core.nodes import EntityNode, EntityEdge, EpisodicNode, EpisodicEdge

# Core classes with full CRUD support:
# - EntityNode: Domain entities (Student, Course, Concept)
# - EntityEdge: Domain relationships (ENROLLED_IN, PREREQUISITE_FOR)  
# - EpisodicNode: Temporal events and episodes
# - EpisodicEdge: Temporal relationship changes
```

## 🚀 Worked Examples

### Educational CRUD Scenarios

```python
# educational_crud_demo.py
import asyncio
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, EntityEdge

async def educational_crud_operations():
    """Schaum's Example: CRUD operations for educational knowledge"""
    
    client = Graphiti(...)
    
    try:
        print("✏️ EDUCATIONAL CRUD OPERATIONS")
        print("=" * 50)
        
        # CREATE: Add new student directly
        student_node = EntityNode(
            name="Sarah Chen",
            uuid="student_sarah_001",
            attributes={
                "major": "Computer Science",
                "year": "Sophomore", 
                "learning_style": "Visual"
            }
        )
        await student_node.save(client.driver)
        print("✅ Created student entity directly")
        
        # CREATE: Add course with prerequisites
        course_node = EntityNode(
            name="CS102 Data Structures",
            uuid="course_cs102",
            attributes={
                "credits": 4,
                "difficulty": "Intermediate",
                "prerequisites": ["CS101"]
            }
        )
        await course_node.save(client.driver)
        
        # CREATE: Enrollment relationship
        enrollment_edge = EntityEdge(
            source_node_uuid="student_sarah_001",
            target_node_uuid="course_cs102", 
            name="ENROLLED_IN",
            attributes={
                "enrollment_date": datetime.now(),
                "status": "Active"
            }
        )
        await enrollment_edge.save(client.driver)
        print("✅ Created enrollment relationship")
        
        # READ: Retrieve and examine entities
        retrieved_student = await EntityNode.get_by_uuid(
            client.driver, "student_sarah_001"
        )
        print(f"📖 Retrieved: {retrieved_student.name}")
        
        # UPDATE: Modify student progress
        retrieved_student.attributes["current_gpa"] = 3.7
        retrieved_student.attributes["courses_completed"] = 3
        await retrieved_student.save(client.driver)
        print("✅ Updated student attributes")
        
        # UPDATE: Change enrollment status
        enrollment_edge.attributes["status"] = "Completed"
        enrollment_edge.attributes["final_grade"] = "A"
        await enrollment_edge.save(client.driver)
        print("✅ Updated enrollment status")
        
        # DELETE: Remove outdated information
        # Note: Careful with deletes in educational context
        # Usually better to mark as inactive
        
        print("📊 CRUD operations completed successfully")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(educational_crud_operations())
```

## 📚 Practice Problems

### Problem 1: Dynamic Curriculum Updates
**Scenario**: Course prerequisites change mid-semester.
**Task**: Use CRUD operations to update prerequisite relationships without affecting enrolled students.

### Problem 2: Student Transfer Management  
**Challenge**: Student transfers between institutions.
**Task**: Design CRUD workflow to migrate student data while preserving learning history.

### Problem 3: Assessment Integration
**Scenario**: Sync assessment results from external LMS.
**Task**: Implement bulk CRUD operations for grade updates.

## 🔧 Advanced Techniques

### Bulk CRUD Operations
```python
async def bulk_grade_update(grade_records):
    """Efficiently update multiple student grades"""
    for record in grade_records:
        assessment_edge = await EntityEdge.get_by_uuid(
            client.driver, record['assessment_id']
        )
        assessment_edge.attributes['score'] = record['score']
        assessment_edge.attributes['updated_at'] = datetime.now()
        await assessment_edge.save(client.driver)
```

### Safe Delete Patterns
```python
async def safe_delete_student(student_uuid):
    """Archive instead of deleting to preserve relationships"""
    student = await EntityNode.get_by_uuid(client.driver, student_uuid)
    student.attributes['status'] = 'Archived'
    student.attributes['archived_date'] = datetime.now()
    await student.save(client.driver)
    # Relationships preserved for historical analysis
```

## 🎯 Next Steps

Continue to **[08_fact_triples](../08_fact_triples/)** to learn precise knowledge representation through direct fact assertion.

**Master's Tip**: CRUD operations give you surgical precision in knowledge graph management. Use them for integration, correction, and dynamic updates while preserving the temporal story told by episodes! 🔧