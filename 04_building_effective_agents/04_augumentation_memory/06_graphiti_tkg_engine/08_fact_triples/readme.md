# Working with Data 03: [Adding Fact Triples](https://help.getzep.com/graphiti/working-with-data/adding-fact-triples) - Precise Knowledge Representation

Welcome to Step 08! Master direct fact assertion for precise educational knowledge.

## 🎯 Learning Objectives

- Master direct fact triple creation (subject-predicate-object)
- Implement precise educational relationship assertion  
- Handle structured knowledge from external systems
- Apply fact triples for curriculum and assessment modeling
- Design knowledge validation and consistency checking

## 📚 Core Concepts

### What are Fact Triples?

**Fact Triples** represent knowledge as structured statements: `(Subject, Predicate, Object)`

**Educational Examples:**
- `(Alice, ENROLLED_IN, CS101)`
- `(Variables, PREREQUISITE_FOR, Loops)`  
- `(Python_Quiz_1, ASSESSES, Programming_Fundamentals)`
- `(Sarah, ACHIEVED_MASTERY_IN, Functions)`

**When to Use Fact Triples vs Episodes:**
- **Fact Triples**: Precise, structured knowledge from databases/APIs
- **Episodes**: Natural language content requiring LLM extraction

## 🚀 Worked Examples

### Educational Fact Modeling

```python
# fact_triples_demo.py
import asyncio
from datetime import datetime
from graphiti_core import Graphiti

async def educational_fact_triples():
    """Schaum's Example: Fact triples for educational knowledge"""
    
    client = Graphiti(...)
    
    try:
        print("📐 EDUCATIONAL FACT TRIPLES")
        print("=" * 50)
        
        # Curriculum Structure Facts
        await client.add_fact_triple(
            head_name="Variables",
            head_type="Programming_Concept",
            edge_type="PREREQUISITE_FOR", 
            tail_name="Loops",
            tail_type="Programming_Concept",
            reference_time=datetime.now(),
            group_id="cs101_curriculum"
        )
        
        # Student Progress Facts  
        await client.add_fact_triple(
            head_name="Alice Chen",
            head_type="Student",
            edge_type="COMPLETED",
            tail_name="Python Basics Assignment",
            tail_type="Assessment", 
            reference_time=datetime.now(),
            group_id="cs101_fall2024"
        )
        
        # Course Enrollment Facts
        await client.add_fact_triple(
            head_name="Bob Martinez", 
            head_type="Student",
            edge_type="ENROLLED_IN",
            tail_name="CS101",
            tail_type="Course",
            reference_time=datetime.now(),
            group_id="cs101_fall2024"
        )
        
        print("✅ Educational facts added to knowledge graph")
        
    finally:
        await client.close()
```

## 📚 Practice Problems

### Problem 1: Prerequisite Chain Modeling
**Task**: Model a complete computer science curriculum using fact triples to represent all prerequisite relationships.

### Problem 2: Assessment Outcome Integration
**Task**: Convert LMS assessment data into fact triples representing student competency achievements.

### Problem 3: Learning Path Validation
**Task**: Use fact triples to validate that students have completed prerequisites before advanced topics.

## 🔧 Advanced Techniques

### Batch Fact Addition
```python
async def add_curriculum_facts(curriculum_data):
    """Add multiple curriculum facts efficiently"""
    for relationship in curriculum_data:
        await client.add_fact_triple(
            head_name=relationship['prerequisite'],
            head_type="Concept",
            edge_type="PREREQUISITE_FOR",
            tail_name=relationship['concept'], 
            tail_type="Concept",
            reference_time=datetime.now(),
            group_id=relationship['course_id']
        )
```

### Fact Validation
```python
async def validate_prerequisite_chain(student_id, target_concept):
    """Verify student has completed prerequisite chain"""
    # Search for prerequisite facts
    results = await client.search(
        query=f"prerequisites for {target_concept}",
        group_id=f"student_{student_id}"
    )
    # Validate completion chain
    return check_completion_chain(results)
```

## 🎯 Next Steps

Continue to **[09_mcp_server](../09_mcp_server/)** to integrate Graphiti with AI assistants through the Model Context Protocol.

**Master's Tip**: Fact triples are your precision tools for structured educational knowledge. Use them when you need exact, queryable relationships between known entities! 📐