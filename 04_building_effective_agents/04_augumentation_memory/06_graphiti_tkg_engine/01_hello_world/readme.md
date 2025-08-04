# Step 01: Hello World - Your First Graphiti Program

Welcome to Graphiti! In this step, you'll create your first temporal knowledge graph and see how it works.

## 📚 Official Documentation
- [Graphiti Getting Started](https://help.getzep.com/graphiti/getting-started/welcome) - Official introduction to Graphiti
- [Quick Start Guide](https://help.getzep.com/graphiti/getting-started/quick-start) - How to install Graphiti Core

## 🎯 What You'll Learn

By the end of this step, you will:
- Install and set up Graphiti
- Add your first episode to create a knowledge graph
- Search the graph to retrieve information
- Understand the basic Graphiti workflow: text → graph → search

## 📋 Prerequisites

- Python 3.10+ installed
- Neo4j database running (local or AuraDB)
- Gemini API key
- Basic Python knowledge

## 🛠️ Setup

### 1. Setup Project and Install Graphiti

```bash
uv init hello_tkg

uv add graphiti-core
```

### 2. Environment Variables

Create a `.env` file or export these variables:

```bash
export GEMINI_API_KEY="your-openai-api-key"
export NEO4J_URI="neo4j://localhost:7687"  # or your AuraDB URI
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-neo4j-password"
```

## 🚀 Hello World Example

Let's create your first Graphiti program that adds a simple episode and verifies it works:

### hello_graphiti.py

```python
import asyncio
import os
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def hello_graphiti():
    """Your first Graphiti program - Hello World!"""
    
    # Initialize Graphiti client
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("🚀 Starting Hello World Graphiti Example...")
        
        # Build the initial graph (creates indices)
        print("🔧 Building initial graph structure...")
        await client.build_indices_and_constraints()
        
        # Add your first episode - a simple text about AI learning
        print("📝 Adding your first episode...")
        await client.add_episode(
            name="hello_world_episode",
            episode_body=(
                "Today I started learning Graphiti, a powerful Python framework for "
                "building temporal knowledge graphs. Graphiti helps AI agents remember "
                "information over time and understand how relationships evolve."
            ),
            source=EpisodeType.text,
            source_description="Learning journal entry",
            reference_time=datetime.now(),
        )
        
        print("✅ Episode added successfully!")
        
        # Verify the graph has data
        print("🔍 Verifying the knowledge graph...")
        
        # Search for information about Graphiti
        search_results = await client.search(
            query="What is Graphiti?",
            limit=3
        )
        
        if search_results.nodes or search_results.edges:
            print(f"🎉 Success! Found {len(search_results.nodes)} nodes and {len(search_results.edges)} edges")
            print("\n📊 Graph Contents:")
            
            # Display nodes
            for i, node in enumerate(search_results.nodes[:3], 1):
                print(f"  Node {i}: {node.name}")
            
            # Display edges
            for i, edge in enumerate(search_results.edges[:3], 1):
                print(f"  Edge {i}: {edge.source_node_name} → {edge.target_node_name} ({edge.name})")
                
        else:
            print("⚠️ No data found. The episode may still be processing.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Close the client
        await client.close()
        print("🔒 Graphiti client closed.")

if __name__ == "__main__":
    # Run the hello world example
    asyncio.run(hello_graphiti())
```

## ▶️ Running Your First Program

1. **Save the code** as `hello_graphiti.py`
2. **Set your environment variables** (see Setup section)
3. **Run the program**:

```bash
python hello_graphiti.py
```

## 📊 Expected Output

You should see something like:

```
🚀 Starting Hello World Graphiti Example...
🔧 Building initial graph structure...
📝 Adding your first episode...
✅ Episode added successfully!
🔍 Verifying the knowledge graph...
🎉 Success! Found 3 nodes and 2 edges
📊 Graph Contents:
  Node 1: Graphiti
  Node 2: Python framework
  Node 3: temporal knowledge graphs
  Edge 1: Graphiti → Python framework (is_a)
  Edge 2: Graphiti → temporal knowledge graphs (helps_with)
🔒 Graphiti client closed.
```

## 🔍 What Just Happened?

Let's break down what your first Graphiti program did:

### 1. **Client Setup**
```python
client = Graphiti(uri=..., user=..., password=...)
```
- Connected to your Neo4j database
- Initialized the Graphiti framework

### 2. **Graph Structure Setup**
```python
await client.build_indices_and_constraints()
```
- Created necessary database indices for performance
- Set up constraints for data integrity

### 3. **Episode Addition**
```python
await client.add_episode(...)
```
- Added text content to the knowledge graph
- Graphiti automatically extracted entities and relationships
- Created nodes for concepts like "Graphiti", "Python framework", etc.
- Created edges showing relationships between concepts

### 4. **Knowledge Retrieval**
```python
search_results = await client.search(query="What is Graphiti?")
```
- Performed semantic search on the knowledge graph
- Retrieved relevant nodes and edges
- Demonstrated that information was successfully stored and can be retrieved

**Key Point**: Text goes in → Graphiti processes it → Structured knowledge comes out that you can search!

## 🧪 Try It Yourself

### Experiment 1: Add More Content

Modify the episode body to include different information:

```python
episode_body = (
    "I'm building a TutorsGPT system that needs to remember student interactions. "
    "The system should track learning progress, personalize content, and adapt "
    "to individual student needs over time."
)
```

### Experiment 2: Search Different Queries

Try different search queries:

```python
# Search for specific concepts
search_results = await client.search(query="student learning progress")

# Search for relationships
search_results = await client.search(query="what adapts to student needs?")
```

### Experiment 3: Add Multiple Episodes

Try adding multiple episodes and see how they connect:

```python
# Episode 1
await client.add_episode(
    name="alice_starts", 
    episode_body="Alice started learning Python programming",
    reference_time=datetime.now() - timedelta(days=7)
)

# Episode 2
await client.add_episode(
    name="alice_progress",
    episode_body="Alice completed her first Python project successfully",
    reference_time=datetime.now()
)

# Search for Alice's journey
results = await client.search("Tell me about Alice's Python learning")
```

## ✅ Verification Checklist

- [ ] Graphiti installed successfully
- [ ] Environment variables configured
- [ ] Neo4j database accessible
- [ ] Program runs without errors
- [ ] Knowledge graph contains nodes and edges
- [ ] Search returns relevant results

## 🤔 Common Questions

**Q: Why didn't I manually create nodes and edges?**
A: Graphiti uses LLMs to automatically extract entities and relationships from text. This is the magic of Graphiti - it understands content semantically!

**Q: How does Graphiti know what entities to extract?**
A: It uses your LLM (OpenAI by default) to analyze the text and identify important concepts and their relationships.

**Q: Can I see the raw Neo4j graph?**
A: Yes! Open Neo4j Browser and run `MATCH (n) RETURN n LIMIT 25` to see the raw graph structure.

## 🎯 Next Steps

Congratulations! You've successfully:
- ✅ Created your first Graphiti knowledge graph
- ✅ Added an episode with automatic entity extraction
- ✅ Performed semantic search on the graph
- ✅ Verified the system works end-to-end

**Ready for the next step?** Move on to **[02_episodes_and_entities](../02_episodes_and_entities/)** to dive deeper into how Graphiti extracts and organizes information.

## 📝 Key Takeaways

1. **Graphiti is automatic** - You provide text, it creates the knowledge graph
2. **Episodes are the input** - Text gets processed into structured knowledge
3. **Search is semantic** - Finds relevant information, not just keyword matches
4. **Everything is temporal** - Knowledge builds up over time
5. **LLMs do the work** - Automatic entity and relationship extraction

## 🎯 What You Learned

- How to install and configure Graphiti
- How to add episodes to create knowledge graphs
- How to search the graph to retrieve information
- The basic workflow: text → episodes → knowledge graph → search

---

**Congratulations!** You've successfully created your first temporal knowledge graph! 🎉

**Ready for the next step?** Continue to **[02_adding_episodes](../02_adding_episodes/)** to learn about different types of episodes and how they create different knowledge structures.

---

*"The best way to learn Graphiti is to start simple and build up your understanding step by step."*