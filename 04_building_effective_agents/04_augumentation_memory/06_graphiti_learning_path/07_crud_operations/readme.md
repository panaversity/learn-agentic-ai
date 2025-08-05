# Step 07: [CRUD Operations](https://help.getzep.com/graphiti/working-with-data/crud-operations) - Direct Node and Edge Manipulation

Now that you've mastered search, let's learn how to directly create, read, update, and delete nodes and edges with surgical precision.

## 🎯 What You'll Learn

By the end of this step, you will:
- Create, read, update, and delete nodes and edges directly
- Understand when to use CRUD vs episodes
- See practical examples of direct graph manipulation
- Learn safe practices for educational data management
- Manually explore CRUD results in Neo4j

## 📋 Prerequisites

- Completed Steps 01-06
- Understanding of search and namespacing
- Knowledge of node and edge concepts

### What is CRUD?

**CRUD** = **C**reate, **R**ead, **U**pdate, **D**elete - direct manipulation of nodes and edges

### CRUD vs Episodes

| CRUD Operations | Episodes |
|----------------|----------|
| Direct control | Natural language processing |
| Precise updates | LLM extracts entities/relationships |
| Known entities | Unstructured content |
| System integration | Rich context discovery |

### Core Classes from [Documentation](https://help.getzep.com/graphiti/working-with-data/crud-operations)

```python
from graphiti_core.nodes import EntityNode, EntityEdge

# EntityNode: Direct node manipulation
# EntityEdge: Direct relationship manipulation
```

### Basic Operations

- **Create**: `node.save(driver)` - Add new nodes/edges
- **Read**: `EntityNode.get_by_uuid(driver, uuid)` - Retrieve by UUID
- **Update**: Modify attributes, then `node.save(driver)` 
- **Delete**: `node.delete(driver)` - Remove (use carefully!)

### When to Use CRUD

**Good for**: Precise updates, system integration, corrections, bulk operations
**Not for**: Natural language content that needs LLM processing

## 🚀 Simple CRUD Example

Let's see all CRUD operations in action with a simple student-course scenario:

### crud_demo.py

```python
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
```

## ▶️ Running the Example

```bash
uv run python crud_demo.py
```

## 📊 Expected Output

```
✏️ CRUD Operations Demo...

📝 **CREATE**: Adding student and course...
   ✅ Created student: Alice Chen
   ✅ Created course: CS101 Programming
   ✅ Created enrollment relationship

📖 **READ**: Retrieving entities...
   📚 Found student: Alice Chen
      GPA: 3.5
   📚 Found course: CS101 Programming
      Credits: 4
   📚 Found enrollment: ENROLLED_IN
      Status: Active

✏️ **UPDATE**: Modifying data...
   ✅ Updated student GPA to: 3.8

👀 Now manually explore CRUD results in Neo4j...
```

## 🔍 **Manual Exploration in Neo4j**

Open your **Neo4j Browser** and explore the CRUD results:

### **1. See All Created Entities**
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
```
*Shows all entities created by CRUD operations*


## 🚀 Advanced: CRUD with Custom Entity Types

Want to combine the power of custom entities (from Step 03) with CRUD operations? Here's how: custom_crud_demo.py

**Why This is Powerful:**
- **Type Safety**: Pydantic models ensure data consistency
- **Domain Modeling**: Educational entities with proper attributes
- **Validation**: Automatic validation of educational data
- **IDE Support**: Full autocomplete and type checking

### ▶️ Running the Custom CRUD Demo

```bash
# Run the enhanced version with custom types
uv run python custom_crud_demo.py
```


## 🎯 Key Concepts from [Official Documentation](https://help.getzep.com/graphiti/working-with-data/crud-operations)

### Core CRUD Classes

According to the documentation, Graphiti uses **8 core classes**:
- `Node`, `EpisodicNode`, `EntityNode` 
- `Edge`, `EpisodicEdge`, `EntityEdge`
- `CommunityNode`, `CommunityEdge`

**For direct manipulation**, we use:
- `EntityNode` and `EntityEdge` (fully supported CRUD)

### Key Methods from Documentation

1. **Save Method**: `await node.save(driver)` 
   - Performs find-or-create based on UUID
   - Updates all data from the class to graph

2. **Delete Method**: `await node.delete(driver)`
   - Hard deletes nodes and edges  
   - Use with caution (prefer archiving)

3. **Get by UUID**: `await EntityNode.get_by_uuid(driver, uuid)`
   - Class method to retrieve by UUID
   - Returns the specific entity

### When to Use CRUD vs Episodes

| Scenario | Use CRUD | Use Episodes |
|----------|----------|--------------|
| **Precise Updates** | ✅ Student GPA changes | ❌ |
| **System Integration** | ✅ LMS grade sync | ❌ |
| **Natural Language** | ❌ | ✅ Learning stories |
| **Known Relationships** | ✅ Enrollment status | ❌ |
| **Bulk Operations** | ✅ Grade imports | ❌ |
| **Rich Context** | ❌ | ✅ Student interactions |

## ✅ Verification Checklist

- [ ] CREATE: Student and course nodes created successfully
- [ ] READ: Entities retrieved by UUID with correct attributes
- [ ] UPDATE: Attributes modified and saved properly
- [ ] VERIFY: Search confirms all CRUD operations worked
- [ ] ARCHIVE: Safe data management instead of deletion
- [ ] Neo4j queries showing CRUD results clearly

## 🤔 Common Questions

**Q: What's the difference between CRUD and episodes?**
A: CRUD gives you direct control for precise updates, while episodes process natural language to extract entities and relationships automatically.

**Q: Why archive instead of delete?**
A: Educational data has legal and analytical value. Archiving preserves history while marking data as inactive.

**Q: How do I know if my CRUD operations worked?**
A: Use search to verify changes, check Neo4j directly, and ensure UUIDs match what you expect.

**Q: Can I mix CRUD and episodes in the same application?**
A: Yes! Use CRUD for structured updates (grades, enrollment) and episodes for rich content (learning interactions, discussions).

**Q: I'm getting "vector must not be null" error - what's wrong?**
A: You need to generate embeddings for EntityNode names. Use `await graphiti.embedder.create([name])` before creating the node.

**Q: Do I always need to generate embeddings manually?**
A: Only for direct CRUD operations. Episodes handle embeddings automatically during LLM processing.

## 📝 What You Learned

✅ **CRUD Operations**: Created, read, updated, and archived nodes and edges directly
✅ **Educational Data Management**: Managed student-course relationships with precision
✅ **UUID-Based Retrieval**: Found and modified specific entities by their unique identifiers
✅ **Custom Entity Types**: Combined Pydantic models with CRUD for type-safe operations
✅ **Safe Data Practices**: Archived instead of deleting to preserve educational records
✅ **Verification Patterns**: Used search to confirm CRUD operations worked correctly

## 🎯 Next Steps

**Excellent work!** You now have surgical precision in knowledge graph management for educational systems.

**Ready to create structured knowledge directly?** Continue to **[08_fact_triples](../08_fact_triples/)** where you'll learn to assert precise facts using subject-predicate-object triples.

**What's Coming**: Instead of natural language processing, you'll learn to directly assert structured knowledge relationships for curriculum modeling and assessment integration!

---

**Key Takeaway**: CRUD operations give you surgical precision for direct graph manipulation. Use them when you know exactly what to change, and episodes when you want LLM intelligence to extract meaning! 🔧

*"CRUD for precision, episodes for intelligence - the perfect combination for educational knowledge graphs."*