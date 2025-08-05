# Step 04: [Communities](https://help.getzep.com/graphiti/core-concepts/communities) - Discovering Hidden Patterns Automatically

Now that you have custom types creating precise knowledge graphs, let's see how Graphiti automatically discovers groups of related information called "communities".

## 🎯 What You'll Learn

By the end of this step, you will:
- Understand what communities are and how they form automatically
- Use `build_communities()` to discover hidden patterns in your data
- See how communities group related students, topics, and concepts
- Update communities dynamically as new episodes are added
- Apply community insights to educational scenarios

## 📚 What Are Communities?

### The Concept

**Communities** (represented as `CommunityNode` objects) are groups of related entity nodes that are strongly connected to each other. Graphiti uses the **Leiden algorithm** to automatically determine these groupings by analyzing connection patterns in your knowledge graph.

**Educational Examples:**
- Students who struggle with similar topics
- Concepts that are frequently taught together  
- Skills that naturally build on each other
- Study groups that form around shared interests

### How Communities Form

1. **Add Episodes** → Creates entities and relationships in your knowledge graph
2. **Build Connections** → Entities link through shared experiences and common attributes
3. **Leiden Algorithm Analysis** → Groups strongly connected nodes together using community detection
4. **Generate Summaries** → Each community gets a summary field that collates the summaries of its member entities

### Community Detection Process

**Technical Details:**
- **Algorithm**: Leiden algorithm groups strongly connected nodes
- **Node Representation**: Communities are stored as `CommunityNode` objects
- **Summary Generation**: Communities contain a summary field that synthesizes information from member entities
- **High-Level Insights**: Provides synthesized information in addition to granular facts stored on edges

### Dynamic Community Updates

**Two Update Methods:**

1. **Full Rebuild** (Recommended periodically):
```python
await graphiti.build_communities()  # Removes existing communities, creates new ones
```

2. **Dynamic Updates** (For ongoing additions):
```python
await graphiti.add_episode(
    episode_body="New content...",
    update_communities=True  # Updates existing communities
)
```

**Update Algorithm:**
- When `update_communities=True` is used, new nodes are assigned to communities based on the most represented community among their surrounding nodes
- This methodology is inspired by the **label propagation algorithm**

### Why Communities Matter

- **Pattern Discovery**: Find hidden relationships you didn't know existed
- **Auto-Organization**: Content groups itself meaningfully through algorithmic analysis
- **Better Search**: Focus queries within relevant communities for more targeted results
- **Learning Insights**: Understand how knowledge naturally clusters in your domain
- **High-Level Synthesis**: Get summarized information about what your graph contains

## 🚀 Simple Communities Example

Let's create just enough data to see communities form, then explore them manually:

### communities_demo.py

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
    """Build communities and explore them manually in Neo4j"""
    
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
        print("🏘️ Communities Demo - Building Knowledge Graph...")
        
        # Add just 4 simple episodes to create communities
        episodes = [
            "Alice and Bob are both learning Python programming together.",
            "Alice is helping Charlie connect Python to web backends.", 
            "Bob and Diana are collaborating on a full-stack project."
        ]
        
        print("\n📝 Adding episodes...")
        for i, episode in enumerate(episodes):
            print(f"episode_{i+1}\n")
            await graphiti.add_episode(
                name=f"episode_{i+1}",
                episode_body=episode,
                source=EpisodeType.text,
                source_description="Engineers Collaboration",
                reference_time=datetime.now() - timedelta(days=i)
            )
        
        print("✅ Episodes added!")
        await asyncio.sleep(60)  # Small delay for clarity
        print("\n🔍 Exploring communities...")
        # Build communities to see patterns
        print("\n🔍 Building communities...")
        res = await graphiti.build_communities()
        print("✅ Communities built!")
        
        print(f"Communities found: \n\n {res}\n\n\n")
        print("\n🎓 Communities demo completed!")
        print("\n👀 Now manually explore your Neo4j database...")
                
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

```bash
uv run python communities_demo.py
```

## 📊 Expected Output

```
🏘️ Communities Demo - Building Knowledge Graph...

📝 Adding episodes...
episode_1

episode_2

episode_3

✅ Episodes added!

🔍 Exploring communities...

🔍 Building communities...
✅ Communities built!
Communities found: 

 ([CommunityNode(...)])

👀 Now manually explore your Neo4j database...
```

## 🔍 **Manual Exploration in Neo4j**

Now comes the fun part! Open your **Neo4j Browser** and run these queries:

### **1. See All Nodes and Communities**
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
```
*This shows your entire graph - entities and communities*

### **2. Find Community Nodes**
```cypher
MATCH (c:Community) RETURN c.name, c.summary
```
*See what communities were discovered and their summaries*

### **3. See Entities in Communities**  
```cypher
MATCH (c:Community)-[m:HAS_MEMBER]->(e:Entity) RETURN c, m, e
```
*Shows which entities belong to which communities*

## 🎯 Key Concepts from [Official Documentation](https://help.getzep.com/graphiti/core-concepts/communities)

### How Communities Work

1. **Episode Addition** → Creates entities and relationships
2. **Leiden Algorithm** → Groups strongly connected nodes together
3. **Summary Generation** → Communities contain a summary field that collates member entity summaries
4. **High-Level Synthesis** → Provides synthesized information about what the graph contains

### Two Ways to Update Communities

```python
# Option 1: Full rebuild (removes existing, creates new)
await graphiti.build_communities()

# Option 2: Dynamic update (adds new nodes to existing communities) - GIVING ERROR as of 5 August 2025
await graphiti.add_episode(
    episode_body="New content...",
    update_communities=True  # Uses label propagation algorithm
)
```

### Why Manual Exploration Matters

- **See the Algorithm Work**: Visually understand how Leiden groups entities
- **Validate Results**: Check if communities make educational sense  
- **Learn Neo4j**: Practice Cypher queries for graph analysis
- **Discover Patterns**: Find unexpected connections in your data

## 🤔 Common Questions

**Q: How many communities should I expect from 4 episodes?**
A: Likely 1-2 communities. You need more interconnected data to see multiple distinct communities.

**Q: What should I see in Neo4j Browser?**
A: EntityNodes (Alice, Bob, Charlie, Diana), CommunityNodes, and HAS_MEMBER relationships connecting them.

**Q: Should I use full rebuild or dynamic updates?**
A: Start with full rebuilds (`build_communities()`) to understand the concept. Dynamic updates are for ongoing additions.

**Q: What if I don't see clear communities?**
A: Try adding more episodes with clearer groupings. The algorithm needs enough connections to detect patterns.

## 🎯 Next Steps

**Fantastic work!** You now understand how knowledge naturally clusters and can leverage these patterns for educational insights.

**Ready to isolate different educational contexts?** Continue to **[05_graph_namespacing](../05_graph_namespacing/)** where you'll learn how to create separate graph spaces for different schools, classes, or organizations.

**What's Coming**: Instead of one big knowledge graph, you'll create isolated environments where different educational contexts don't interfere with each other - perfect for multi-tenant educational systems!

---

**Key Takeaway**: Build communities with minimal code, then explore them manually in Neo4j! This hands-on approach teaches both Graphiti concepts and practical graph database skills. 🔍

*"The best way to understand communities is to see them with your own eyes in the graph database."*