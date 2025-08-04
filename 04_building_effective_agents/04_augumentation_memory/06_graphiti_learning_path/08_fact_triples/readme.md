# Step 08: Adding Fact Triples - Precise Knowledge Representation

Now that you understand CRUD operations, let's learn how to add structured knowledge using fact triples for precise educational relationship modeling.

## 📚 Official Documentation

- [Adding Fact Triples](https://help.getzep.com/graphiti/working-with-data/adding-fact-triples) - Complete guide to fact triple creation

## 🎯 What You'll Learn

By the end of this step, you will:
- Master direct fact triple creation using subject-predicate-object structure
- Understand when to use fact triples vs episodes vs CRUD operations
- Implement precise educational relationship assertion  
- Handle structured knowledge from external educational systems
- Design curriculum and assessment modeling with fact triples

## 📋 Prerequisites

- Completed Steps 01-07
- Understanding of CRUD operations and search
- Knowledge of RDF/semantic web concepts (helpful but not required)

## 📚 What are Fact Triples?

### The Concept

**Fact Triples** represent knowledge as structured statements in the form: `(Subject, Predicate, Object)`

This creates precise, queryable relationships between known entities without requiring LLM processing.

**Educational Examples:**
- `(Alice, ENROLLED_IN, CS101)`
- `(Variables, PREREQUISITE_FOR, Loops)`  
- `(Python_Quiz_1, ASSESSES, Programming_Fundamentals)`
- `(Sarah, ACHIEVED_MASTERY_IN, Functions)`

### Fact Triples vs Other Approaches

| Method | Use When | Example |
|--------|----------|---------|
| **Fact Triples** | Precise, structured knowledge from databases/APIs | `(Student_123, COMPLETED, Assignment_456)` |
| **Episodes** | Natural language content requiring LLM extraction | "Alice struggled with loops but mastered them after practice" |
| **CRUD** | Direct manipulation of existing nodes/edges | Update student GPA from 3.5 to 3.7 |

### Adding Fact Triples in Graphiti

Graphiti provides the `add_triplet()` method for adding fact triples:

```python
# Method signature
await graphiti.add_triplet(source_node, edge, target_node)
```

Where:
- `source_node`: EntityNode representing the subject
- `edge`: EntityEdge representing the predicate/relationship
- `target_node`: EntityNode representing the object

All components should share the same `group_id` for proper namespace isolation.

## 🚀 Complete Working Example

Let's implement fact triple modeling for educational systems:

### fact_triples_demo.py

```python
import asyncio
import os
from datetime import datetime
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
    """Educational fact triple modeling demonstration"""
    
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
        await variables_node.save(graphiti.driver)
        
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
        await loops_node.save(graphiti.driver)
        
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
        
        # Add the fact triple
        await graphiti.add_triplet(variables_node, prereq_edge, loops_node)
        print("   ✅ Variables → PREREQUISITE_FOR → Loops")
        
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
        await student_node.save(graphiti.driver)
        
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
        
        await graphiti.add_triplet(student_node, mastery_edge, variables_node)
        print("   ✅ Alice Chen → MASTERED → Variables (Score: 95)")
        
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
        await assessment_node.save(graphiti.driver)
        
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
        
        await graphiti.add_triplet(student_node, completion_edge, assessment_node)
        print("   ✅ Alice Chen → COMPLETED → Variables Quiz (Score: 92)")
        
        # Validate with search
        print("\n🔍 Validating fact triples with search...")
        
        search_results = await graphiti.search(
            query="Alice Chen Variables mastery prerequisite programming concepts",
            group_id=namespace
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
```

## ▶️ Running the Example

1. **Save the code** as `fact_triples_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python fact_triples_demo.py
```

## 📊 Expected Output

```
📐 Starting Educational Fact Triples Demo...

📚 Creating programming concepts...
   ✅ Created Variables and Loops concepts

🔗 Creating prerequisite relationship...
   ✅ Variables → PREREQUISITE_FOR → Loops

👨‍🎓 Creating student mastery relationship...
   ✅ Alice Chen → MASTERED → Variables (Score: 95)

📊 Creating assessment completion relationship...
   ✅ Alice Chen → COMPLETED → Variables Quiz (Score: 92)

🔍 Validating fact triples with search...
   📊 Found 4 results:
     1. Variables is a prerequisite for Loops
     2. Alice Chen mastered Variables concept
     3. Alice Chen completed Variables Quiz with score 92
     4. Variables concept is basic programming foundation

✅ Educational fact triples demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Prerequisite Chain Validation

Create a system to validate learning prerequisites:

```python
async def validate_prerequisites(student_uuid: str, target_concept: str):
    """Verify student has completed prerequisite chain"""
    
    # Find prerequisites for target concept
    prereq_search = await graphiti.search(
        query=f"prerequisites required before {target_concept}"
    )
    
    # Check student mastery
    mastery_search = await graphiti.search(
        query=f"student mastered {target_concept} prerequisites"
    )
    
    return len(mastery_search) > 0
```

### Exercise 2: Assessment Integration

Convert external assessment data to fact triples:

```python
async def integrate_assessment_data(assessment_records: list):
    """Convert LMS data to fact triples"""
    
    for record in assessment_records:
        # Create student, assessment nodes
        student_node = await create_student_node(record['student_id'])
        assessment_node = await create_assessment_node(record['assessment'])
        
        # Create completion fact triple
        completion_edge = EntityEdge(
            uuid=str(uuid.uuid4()),
            source_node_uuid=student_node.uuid,
            target_node_uuid=assessment_node.uuid,
            name="ACHIEVED_SCORE",
            fact=f"Student achieved {record['score']} on {record['assessment']}",
            attributes={"score": record['score'], "date": record['date']}
        )
        
        await graphiti.add_triplet(student_node, completion_edge, assessment_node)
```

## 🎯 Key Concepts Explained

### When to Use Fact Triples

**Use Fact Triples for:**
- Known, structured relationships from databases
- Curriculum prerequisite chains
- Assessment results and grades
- Student enrollment and completion records
- Competency and mastery tracking

**Use Episodes for:**
- Natural language learning content
- Student reflections and feedback
- Unstructured educational narratives

### Best Practices

1. **Consistent Naming**: Use standardized predicate names
2. **Rich Attributes**: Include metadata like scores and dates
3. **Namespace Isolation**: Use consistent `group_id`
4. **Validation**: Verify entities exist before creating relationships
5. **Temporal Tracking**: Include timestamps for educational compliance

## ✅ Verification Checklist

- [ ] Fact triples created with subject-predicate-object structure
- [ ] Educational relationships modeled (prerequisites, mastery)
- [ ] Assessment results integrated using fact triples
- [ ] Search queries validate fact triple creation
- [ ] Namespace isolation maintained

## 🤔 Common Questions

**Q: When should I use fact triples instead of episodes?**
A: Use fact triples for structured, known relationships from databases. Use episodes for natural language content.

**Q: How do I handle many-to-many relationships?**
A: Create multiple fact triples. One student enrolled in multiple courses = multiple ENROLLED_IN triples.

**Q: Can I update fact triples?**
A: Yes, but often better to create new triples with timestamps to maintain history.

## 📝 What You Learned

✅ **Structured Knowledge**: Created precise subject-predicate-object relationships
✅ **Educational Modeling**: Modeled prerequisites, mastery, and assessments
✅ **System Integration**: Converted external data to structured knowledge
✅ **Validation**: Used search to verify fact triple creation

## 🎯 Next Steps

**Outstanding work!** You now master precise knowledge representation using fact triples.

**Ready to integrate with AI assistants?** Continue to **[09_mcp_server](../09_mcp_server/)** where you'll expose your Graphiti knowledge through the Model Context Protocol.

**What's Coming**: Make your knowledge accessible to AI assistants and agents through standardized protocols!

---

**Key Takeaway**: Fact triples are precision tools for structured educational knowledge. Use them for exact, queryable relationships between known entities! 📐

*"Structured knowledge enables structured learning - fact triples turn educational data into actionable insights."*