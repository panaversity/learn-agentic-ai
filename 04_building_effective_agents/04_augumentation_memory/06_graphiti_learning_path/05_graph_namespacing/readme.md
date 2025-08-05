# Step 05: [Graph Namespacing](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) - Multi-Tenant Educational Systems

Graphiti supports the concept of graph namespacing through the use of group_id parameters. This feature allows you to create isolated graph environments within the same Graphiti instance, enabling multiple distinct knowledge graphs to coexist without interference.

Now that you understand communities, let's learn how to create isolated educational environments using `group_id` for multi-tenant systems. Graph namespacing is particularly useful for:

- Multi-tenant applications: Isolate data between different customers or organizations
- Testing environments: Maintain separate development, testing, and production graphs
- Domain-specific knowledge: Create specialized graphs for different domains or use cases
- Team collaboration: Allow different teams to work with their own graph spaces

## The Concept

**Graph namespacing** in Graphiti uses `group_id` parameters to create isolated graph environments within the same Graphiti instance. This enables multiple distinct knowledge graphs to coexist without interference.

**Educational Use Cases:**
- **Multi-Institution Platform**: Different schools using the same TutorsGPT system
- **Course Isolation**: Separate CS101 from MATH201 knowledge graphs
- **Semester Separation**: Fall 2024 vs Spring 2025 student cohorts
- **Privacy Boundaries**: Student data isolation for FERPA compliance
- **Testing Environments**: Separate development, testing, and production graphs

### How Namespacing Works

In Graphiti, every node and edge can be associated with a `group_id`. When you specify a `group_id`, you're effectively creating a namespace for that data. Nodes and edges with the same `group_id` form a cohesive, isolated graph that can be queried and manipulated independently.

### Using group_ids in Graphiti

**Adding Episodes with group_id:**
```python
await graphiti.add_episode(
    name="student_progress",
    episode_body="Alice completed her Python assignment...",
    source=EpisodeType.text,
    group_id="university_a_cs101_fall2024"  # Isolated namespace
)
```

**Adding Fact Triples with group_id:**
```python
# Ensure both nodes and edge share the same group_id
await graphiti.add_triplet(source_node, edge, target_node)
# Where all components have the same group_id
```

**Querying Within a Namespace:**
```python
# Search within specific namespace only
search_results = await graphiti.search(
    query="programming concepts",
    group_id="university_a_cs101_fall2024"  # Only search this namespace
)
```

## 🚀 Simple Namespacing Example

Let's create two separate course environments and see how `group_id` keeps them isolated:

### namespacing_demo.py

```python
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Simple namespace isolation demo"""
    
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
                model="gemini-2.0-flash-lite"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🏫 Namespacing Demo - Creating Isolated Course Environments...")
        
        # Course A: CS101 
        print("\n📘 Adding CS101 episodes...")
        await graphiti.add_episode(
            name="cs101_alice",
            episode_body="Alice is learning Python basics in CS101. She understands variables and loops.",
            source=EpisodeType.text,
            source_description="CS101 student background",
            group_id="course_cs101",  # CS101 namespace
            reference_time=datetime.now() - timedelta(days=2)
        )
        
        await graphiti.add_episode(
            name="cs101_bob",
            episode_body="Bob is struggling with Python functions in CS101. He needs help with parameters.",
            source=EpisodeType.text,
            source_description="CS101 student background",
            group_id="course_cs101",  # CS101 namespace
            reference_time=datetime.now() - timedelta(days=1)
        )

        await asyncio.sleep(60)
        
        # Course B: MATH201
        print("📗 Adding MATH201 episodes...")
        await graphiti.add_episode(
            name="math201_carol",
            episode_body="Carol is studying calculus in MATH201. She excels at derivatives and integration.",
                source=EpisodeType.text,
            source_description="MATH201 student background",
            reference_time=datetime.now() - timedelta(days=3),
            group_id="course_math201"  # MATH201 namespace
        )
        
        await graphiti.add_episode(
            name="math201_diana",
            episode_body="Diana finds linear algebra challenging in MATH201. She needs help with matrices.",
            source=EpisodeType.text,
            source_description="MATH201 student background",
            reference_time=datetime.now() - timedelta(days=2),
            group_id="course_math201"  # MATH201 namespace
        )
        
        print("✅ Episodes added to separate namespaces!")
        await asyncio.sleep(60)
        
        # Search within CS101 namespace only
        print("\n🔍 Searching within CS101 namespace...")
        cs101_results = await graphiti.search(
            query="programming Python students learning",
            group_ids=["course_cs101"],  # Only search CS101
            num_results=10
        )
        
        print(f"CS101 results: {len(cs101_results)} found")
        for result in cs101_results:
            print(f"  • {result.fact}")
        
        # Search within MATH201 namespace only
        print("\n🔍 Searching within MATH201 namespace...")
        math201_results = await graphiti.search(
            query="mathematics calculus students learning",
            group_ids=["course_math201"],  # Only search MATH201
            num_results=10
        )
        
        print(f"MATH201 results: {len(math201_results)} found")
        for result in math201_results:
            print(f"  • {result.fact}")
        
        # Global search (no group_id) - sees everything
        print("\n🌍 Global search (no namespace restriction)...")
        global_results = await graphiti.search(
            query="students learning",
            num_results=10  # No group_id = search all namespaces
        )
        
        print(f"Global results: {len(global_results)} found")
        for result in global_results:
            print(f"  • {result.fact}")
        
        print("\n🎓 Namespacing demo completed!")
        print("\n👀 Now manually explore namespaces in Neo4j...")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

```bash
uv run python namespacing_demo.py
```

## 📊 Expected Output

```
🏫 Namespacing Demo - Creating Isolated Course Environments...

📘 Adding CS101 episodes...
📗 Adding MATH201 episodes...
✅ Episodes added to separate namespaces!

🔍 Searching within CS101 namespace...
CS101 results: 9 found
  • Alice is learning Python basics in CS101
  • Alice is learning Python basics
  • Python functions in CS101
  • Python functions... parameters
  • Bob is struggling with Python functions
  • Bob is in CS101
  • She understands variables
  • He needs help with parameters
  • She understands loops

🔍 Searching within MATH201 namespace...
MATH201 results: 8 found
  • calculus in MATH201
  • Carol is studying calculus
  • Carol is studying in MATH201
  • linear algebra challenging in MATH201
  • Diana finds linear algebra challenging
  • She needs help with matrices
  • She excels at derivatives
  • She excels at integration

🌍 Global search (no namespace restriction)...
Global results: 10 found
  • Carol is studying in MATH201
  • calculus in MATH201
  • Carol is studying calculus
  • Alice is learning Python basics in CS101
  • Bob is in CS101
  • Alice is learning Python basics
  • linear algebra challenging in MATH201
  • She understands variables
  • Python functions in CS101
  • She needs help with matrices

🎓 Namespacing demo completed!

👀 Now manually explore namespaces in Neo4j...
```

## 🔍 **Manual Exploration in Neo4j**

Open your **Neo4j Browser** and run these queries to see namespace isolation:

### **1. See All Nodes with Their Namespaces**
```cypher
MATCH (n:Entity) 
RETURN n.name, n.group_id
ORDER BY n.group_id
```

```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
```

*Shows each entity and which namespace it belongs to*

### **2. Find All Nodes in CS101 Namespace**
```cypher
MATCH (n:Entity) 
MATCH (n)-[r]->(m)
WHERE n.group_id = "course_cs101"
RETURN n, r, m
```
*Only shows CS101 entities*

## 🤔 Common Questions

**Q: What happens if I don't specify a group_id?**
A: The entity/episode goes to the default namespace and appears in global searches (searches without `group_id`).

**Q: Can CS101 students see MATH201 data?**
A: No! That's the point of namespacing - complete isolation between courses for privacy and organization.

**Q: How do I search across multiple specific namespaces?**
A: You need to make separate searches for each namespace and combine results in your application code.

**Q: Why use namespaces instead of separate databases?**
A: Namespaces are lighter weight and allow global analytics when needed, while still maintaining isolation.

## 🎯 Next Steps

**Excellent work!** You now understand how to create scalable, privacy-preserving educational systems with proper data isolation.

**Ready to master advanced search techniques?** Continue to **[06_searching](../06_searching/)** where you'll learn Graphiti's powerful hybrid search capabilities and result optimization techniques.

**What's Coming**: Instead of basic searches, you'll learn semantic search, keyword search, reranking strategies, and search recipes tailored for educational scenarios!

---

**Key Takeaway**: Namespaces are like "course classrooms" in your knowledge graph - each course gets its own isolated space, but you can still do university-wide analytics when needed! 🏫

*"Namespaces solve the multi-tenant challenge: complete privacy when needed, global insights when appropriate."*