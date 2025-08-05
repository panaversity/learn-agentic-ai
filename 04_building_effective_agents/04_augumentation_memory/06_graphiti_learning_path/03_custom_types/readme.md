# Step 03: [Custom Entity & Edge Types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types) - Making Knowledge Graphs Domain-Specific

Graphiti allows you to define custom entity types and edge types to better represent your domain-specific knowledge. This enables more structured data extraction and richer semantic relationships in your knowledge graph.

Now that you understand episodes, let's make your knowledge graphs much more precise by defining custom types.We'll use the **memory types you already learned** in Step 01 (STM, episodic, semantic, procedural memory). This bridges theory with practice!

## 🎯 What You'll Learn

By the end of this step, you will:
- Define memory-based entity types (`Student`, `MemoryEvent`) connecting to concepts you know
- Create memory-focused edge types (`MemoryFormation`) with retention and formation attributes
- Use Pydantic models to structure memory data like episodic, semantic, procedural types
- Apply memory-based custom types to episodes for precise knowledge extraction
- See how theory from Step 01 becomes practical Graphiti implementation

## 📚 Why Custom Types Matter

### The Problem with Generic Types

**Without Custom Types:**
```
Generic entities: "person", "thing", "concept", "event"
Generic relationships: "relates_to", "connected_to", "associated_with"
```

**Result:** Vague, hard-to-query knowledge graphs with unclear semantics

### The Power of Custom Types

**With Custom Types:**
```
Educational entities: Student, Course, Instructor, Assignment, Skill
Educational relationships: ENROLLED_IN, TEACHES, COMPLETED, MASTERED, STRUGGLES_WITH
```

**Result:** Precise, queryable, domain-specific knowledge that understands your educational context

### Key Benefits

- **Semantic Precision**: Know exactly what each entity represents
- **Rich Attributes**: Store domain-specific data (GPA, course credits, skill levels)
- **Better Queries**: Search for specific types of information  
- **Guided LLM**: Help AI extract the right types of information from episodes
- **Type Safety**: Validate data structure and catch errors early

## 🏗️ **Understanding Custom Types Architecture**

### Entity Types vs Edge Types

**Entity Types** define "things" in your domain:
- `Student` - a learner with attributes like GPA, major, learning style
- `Course` - a class with credits, difficulty, prerequisites
- `Instructor` - a teacher with experience, specialization, department
- `Skill` - a competency with difficulty level, category

**Edge Types** define "relationships" between things:
- `Enrollment` - student ↔ course relationship with grade, semester, status
- `TeachingAssignment` - instructor ↔ course relationship with schedule, section
- `SkillDevelopment` - student ↔ skill relationship with proficiency, evidence
- `PrerequisiteRelationship` - course ↔ course dependency with strength

### Using Pydantic for Type Definition

Graphiti uses **Pydantic BaseModel** for custom types. This provides:
- **Type validation** - ensures data integrity
- **Rich attributes** - structured fields with descriptions
- **Documentation** - built-in schema generation
- **IDE support** - autocomplete and type checking

So custom entity types and edge types are defined using Pydantic models. Each model represents a specific type with custom attributes.

### [Understand How it works?](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types#how-custom-types-work)


## 🚀 Complete Working Example

Let's build on this concept:

### custom_types_demo.py

```python
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
```

## ▶️ Running the Example

```bash
uv run python main.py
```

## 📊 Expected Output

```
🎓 Starting Custom Types Demo...

🧠 Adding one memory formation episode...
✅ Episode with custom types added!

🔍 Searching for custom type results...

🎯 Custom Type Results: 4 found
  1. Alice Chen is visual learner who prefers episodic memory formation
  2. Alice Chen formed strong procedural memory about Python loops
  3. Memory formation occurred on October 15, 2024 with high importance
  4. Memory event showed strong retention strength

🎓 Custom types demo completed successfully!
```

## See [Best Practices for Defining Custom Entity and Edge Types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types#best-practices)

## 🧪 Try It Yourself

### Exercise 1: Add Semantic Memory Type

Try adding a `SemanticMemory` entity:

```python
class SemanticMemory(BaseModel):
    """Factual knowledge and concepts"""
    knowledge_domain: Optional[str] = Field(None, description="Programming, math, history, etc.")
    confidence_level: Optional[str] = Field(None, description="High, medium, low")

# Add to your types
entity_types["SemanticMemory"] = SemanticMemory
```

### Exercise 2: Add Memory Recall Episode

Create an episode about retrieving memory:

```python
await graphiti.add_episode(
    name="alice_memory_recall",
    episode_body="Alice recalled her semantic memory about Python syntax with high confidence. This programming knowledge helped her solve a new coding problem.",
    source=EpisodeType.text,
    entity_types=entity_types,
    edge_types=edge_types,
    edge_type_map=edge_type_map
)
```

## 🎯 Key Concepts Explained

### How Custom Types Guide LLM Extraction

**Without Custom Types:**
```
"Alice formed memory about loops" → Generic entities: "person", "thing", "concept"
```

**With Custom Types:**
```
"Alice formed memory about loops" → Specific entities: Student("Alice"), MemoryEvent("Python loops")
                                 → Specific relationship: MemoryFormation(retention_strength="Strong")
```

### Edge Type Mapping Strategy

The `edge_type_map` tells Graphiti which relationships can exist:

```python
edge_type_map = {
    ("Student", "MemoryEvent"): ["MemoryFormation"],  # Students can form memories
    ("Entity", "Entity"): ["RELATES_TO"]              # Fallback for unexpected relationships
}
```

### Benefits of Memory-Based Attributes

Custom types connect to memory theory you already learned:

```python
# Instead of just knowing "Alice learned something"
# You get rich memory formation data:
MemoryFormation(
    formation_date="2024-10-15",
    retention_strength="Strong"
)
```

## ✅ Verification Checklist

- [ ] Two memory-based entity types defined (`Student`, `MemoryEvent`)
- [ ] One memory edge type defined (`MemoryFormation`)
- [ ] Edge type mapping covers Student-MemoryEvent relationship
- [ ] Single memory formation episode processed with custom type guidance
- [ ] Search results show memory-specific entities and relationships

## 🤔 Common Questions

**Q: What's the difference between episodes and custom types?**
A: Episodes are the raw data you input. Custom types guide how Graphiti extracts and structures that data into precise entities and relationships.

**Q: How does this connect to memory theory I learned?**
A: This example uses the same memory concepts from Step 01 - episodic, semantic, procedural memory types. You're applying that theory to Graphiti custom types!

**Q: Why use memory types instead of generic educational types?**
A: Because you already understand memory theory! This bridges what you learned about agentic memory with practical Graphiti implementation.

## 📝 What You Learned

✅ **Memory-Based Custom Types**: Defined 2 memory entities (`Student`, `MemoryEvent`) connecting to theory you know  
✅ **Memory Relationships**: Created 1 meaningful edge type (`MemoryFormation`) with memory-specific attributes
✅ **Theory-to-Practice Bridge**: Applied agentic memory concepts to Graphiti custom types  
✅ **LLM Guidance**: Helped Graphiti extract memory formation patterns from episodes
✅ **Familiar Foundation**: Built on memory types (STM, episodic, semantic, procedural) you already understand

## 🎯 Next Steps

**Excellent progress!** You now have precise, domain-specific knowledge graphs instead of generic entities and relationships.

**Ready to discover patterns automatically?** Continue to **[04_communities](../04_communities/)** where you'll learn how Graphiti automatically finds groups and clusters in your knowledge graph.

**What's Coming**: Instead of manually organizing information, you'll see how Graphiti discovers that certain students struggle with similar topics, or that certain teaching methods work well together - all automatically!

---

**Key Takeaway**: Connect new concepts to what you already know! Using memory types you learned in Step 01 makes Graphiti custom types immediately familiar and practical. 🧠

🔧 **Learning Challenge: Manual Data Insertion (Not LLM Extracted):** Sometimes you have data that should **not** be extracted by the LLM - like `student_id`, `course_code`, `topic_id`. These are system identifiers that you want to **manually control**.

*"The best learning happens when new technical skills build on theoretical foundations you already understand."*