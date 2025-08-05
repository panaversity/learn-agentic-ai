# Step 06: [Searching the Graph](https://help.getzep.com/graphiti/working-with-data/searching) - Hybrid Search and Advanced Retrieval

Now that you understand namespacing, let's master Graphiti's powerful search capabilities by comparing different strategies on the **same query**.

## 🎯 What You'll Learn

By the end of this step, you will:
- See how different search strategies work on the same query
- Understand hybrid search (semantic + BM25) vs focused approaches
- Compare search recipes (nodes vs edges vs combined)
- Learn when to use each search strategy
- Manually explore search results in Neo4j

### Two Main Search Approaches

1. **Hybrid Search**: `await graphiti.search(query)`
   - Combines semantic similarity and BM25 retrieval
   - Uses Reciprocal Rank Fusion (RRF) for reranking
   - Good for: Broad exploration and general discovery

2. **Node Distance Reranking**: `await graphiti.search(query, focal_node_uuid)`
   - Same as hybrid search but prioritizes results near a specific node
   - Good for: Entity-focused queries (e.g., "What does Alice know about Python?")

### Configurable Search with Recipes

Graphiti provides `graphiti._search()` with **15 pre-built recipes**:

| Recipe Focus | What It Returns | When to Use |
|-------------|-----------------|-------------|
| `NODE_HYBRID_SEARCH_RRF` | Entities/concepts | Finding people, topics, concepts |
| `EDGE_HYBRID_SEARCH_RRF` | Relationships/facts | Finding connections, interactions |
| `COMBINED_HYBRID_SEARCH_RRF` | Everything | Comprehensive exploration |

### Reranking Strategies from [Documentation](https://help.getzep.com/graphiti/working-with-data/searching)

- **RRF (Reciprocal Rank Fusion)**: Combines BM25 + semantic search results
- **MMR (Maximal Marginal Relevance)**: Balances relevance with diversity  
- **Cross-Encoder**: Most accurate but slower semantic scoring

## 🚀 Simple Search Strategy Comparison

Let's compare all search strategies using the **same query** to see the differences:

### main.py

```python
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_RRF, 
    EDGE_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_RRF
)

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Compare search strategies using the same query"""
    
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
                model="gemini-2.5-flash-lite"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🔍 Search Strategy Comparison Demo...")
        
        # Add simple educational content
        print("\n📚 Adding educational knowledge...")
        
        episodes = [
            "Alice is learning Python programming. She understands variables but struggles with loops.",
            "Bob helps Alice with debugging techniques. He explains step-by-step problem solving.",
            "Carol collaborates with Alice and Bob on programming projects using Python functions.",
            "Variables are fundamental concepts in Python. Loops build on variable understanding."
        ]
        
        for i, episode in enumerate(episodes):
            print(f"episode_{i+1}")
            await graphiti.add_episode(
                name=f"episode_{i+1}",
                episode_body=episode,
                source=EpisodeType.text,
                source_description="Educational content",
                reference_time=datetime.now() - timedelta(days=i),
                group_id="cs101"
            )
            await asyncio.sleep(60)  # Simulate processing time
        
        print("✅ Episodes added!")
        print("\n⏳ Processing for search...")
        await asyncio.sleep(60)
        
        # THE SAME QUERY for all strategies
        QUERY = "Alice learning Python programming"
        print(f"\n🎯 **Comparing all strategies with query: '{QUERY}'**\n")
        
        # Strategy 1: Basic Hybrid Search
        print("📖 **Strategy 1: Basic Hybrid Search**")
        basic_results = await graphiti.search(query=QUERY)
        print(f"   Results: {len(basic_results)} found")
        for i, result in enumerate(basic_results, 1):
            print(f"     {i}. {result.fact}")
        
        # Strategy 2: Node-Focused Search  
        print(f"\n🎯 **Strategy 2: Node-Focused Search (entities/concepts)**")
        node_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_config.limit = 10
        
        node_results = await graphiti._search(query=QUERY, config=node_config)
        print(f"   Nodes found: {len(node_results.nodes)}")
        for i, node in enumerate(node_results.nodes, 1):
            print(f"     {i}. {node.name}")
        
        # Strategy 3: Edge-Focused Search
        print(f"\n🔗 **Strategy 3: Edge-Focused Search (relationships)**")
        edge_config = EDGE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        edge_config.limit = 10
        
        edge_results = await graphiti._search(query=QUERY, config=edge_config)
        print(f"   Relationships found: {len(edge_results.edges)}")
        for i, edge in enumerate(edge_results.edges, 1):
            print(f"     {i}. {edge.source_node_uuid} → {edge.target_node_uuid}")
            print(f"        Type: {edge.name}")
        
        # Strategy 4: Combined Search
        print(f"\n🌍 **Strategy 4: Combined Search (everything)**")
        combined_config = COMBINED_HYBRID_SEARCH_RRF.model_copy(deep=True)
        combined_config.limit = 10
        
        combined_results = await graphiti._search(query=QUERY, config=combined_config)
        print(f"   Nodes: {len(combined_results.nodes)}")
        print(f"   Edges: {len(combined_results.edges)}")  
        print(f"   Communities: {len(combined_results.communities)}")
        
        print("\n🎓 Search comparison completed!")
        print("\n👀 Now manually explore search results in Neo4j...")
        
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

```bash
uv run python main.py
```

## 📊 Expected Output

```
🔍 Search Strategy Comparison Demo...

📚 Adding educational knowledge...
episode_1
episode_2
episode_3
episode_4
✅ Episodes added!

⏳ Processing for search...

🎯 **Comparing all strategies with query: 'Alice learning Python programming'**

📖 **Strategy 1: Basic Hybrid Search**
   Results: 10 found
     1. Alice is learning Python programming.
     2. Alice ... using Python functions
     3. Bob helps Alice with debugging techniques.
     4. Bob helps Alice with debugging techniques.
     5. Carol ... using Python functions
     6. Alice and Bob collaborate
     7. Bob ... using Python functions
     8. Variables are fundamental concepts in Python.
     9. Carol collaborates with Alice
     10. She understands variables

🎯 **Strategy 2: Node-Focused Search (entities/concepts)**
   Nodes found: 10
     1. Alice
     2. Python programming
     3. Python
     4. Python functions
     5. Carol
     6. step-by-step problem solving
     7. Bob
     8. variables
     9. loops
     10. debugging techniques

🔗 **Strategy 3: Edge-Focused Search (relationships)**
   Relationships found: 10
     1. ce59d916-31a2-44b9-b51a-869da4b9a45b → b46fcb99-bb04-4f25-b9cc-f013c76dd230
        Type: IS_LEARNING
     2. ce59d916-31a2-44b9-b51a-869da4b9a45b → 66291e1e-ae48-4a67-8393-af7f7b74b544
        Type: USES
     3. b8f6c852-c541-4162-b0d3-5ca31f9c7507 → ce59d916-31a2-44b9-b51a-869da4b9a45b
        Type: HELPS
     4. b8f6c852-c541-4162-b0d3-5ca31f9c7507 → 358ae58e-b214-47d3-bf50-d5e0924d5a16
        Type: EXPLAINS
     5. a73f81ed-992d-4f55-ae2e-6f7722131fbd → 66291e1e-ae48-4a67-8393-af7f7b74b544
        Type: USES
     6. ce59d916-31a2-44b9-b51a-869da4b9a45b → b8f6c852-c541-4162-b0d3-5ca31f9c7507
        Type: COLLABORATES_WITH
     7. b8f6c852-c541-4162-b0d3-5ca31f9c7507 → 66291e1e-ae48-4a67-8393-af7f7b74b544
        Type: USES
     8. dfd26e7d-f119-43ea-867f-586a468e683b → ba45355b-f624-4a7a-a455-21745f4e8216
        Type: ARE_FUNDAMENTAL_CONCEPTS_IN
     9. a73f81ed-992d-4f55-ae2e-6f7722131fbd → ce59d916-31a2-44b9-b51a-869da4b9a45b
        Type: COLLABORATES_WITH
     10. ce59d916-31a2-44b9-b51a-869da4b9a45b → dfd26e7d-f119-43ea-867f-586a468e683b
        Type: UNDERSTANDS

🌍 **Strategy 4: Combined Search (everything)**
   Nodes: 10
   Edges: 10
   Communities: 0

🎓 Search comparison completed!

👀 Now manually explore search results in Neo4j...
```

## 🔍 **Manual Exploration in Neo4j**

Open your **Neo4j Browser** and explore the search results:

### **1. See All Search-Related Entities**
```cypher
MATCH (n:Entity) 
WHERE n.name CONTAINS "Alice" OR n.name CONTAINS "Python"
RETURN n.name, n.group_id
```
*Find entities related to your search query*

### **2. Find Relationships Around Alice**
```cypher
MATCH (n:Entity) 
WHERE n.name CONTAINS "Alice" OR n.name CONTAINS "Python"
MATCH (n)-[r]->(m)
RETURN n, r, m
```
*See what Alice is connected to*

## 🧪 Try It Yourself

### Exercise 1: Try Different Queries

Test the same strategies with different queries:

```python
# Test these queries and see how results differ
queries_to_test = [
    "Bob helping debugging",
    "Python variables concepts", 
    "programming collaboration",
    "learning difficulties"
]
```

### Exercise 2: Add More Episodes and Re-Search

Add more complex episodes and see how search results change:

```python
new_episodes = [
    "Alice mastered Python loops after Bob's debugging help.",
    "Carol teaches Alice about Python functions and code organization.",
    "The programming team uses collaborative debugging strategies."
]

# Re-run the same search query and see new results
```

### Exercise 3: Explore Search Recipes

Try different search recipe combinations:

```python
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_MMR,  # Different reranking
    EDGE_HYBRID_SEARCH_MMR,
    COMMUNITY_HYBRID_SEARCH_RRF
)

# Compare RRF vs MMR reranking
query = "Alice learning Python"

rrf_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
mmr_config = NODE_HYBRID_SEARCH_MMR.model_copy(deep=True)

rrf_results = await graphiti._search(query, config=rrf_config)
mmr_results = await graphiti._search(query, config=mmr_config)

print(f"RRF reranking: {len(rrf_results.nodes)} nodes")
print(f"MMR reranking: {len(mmr_results.nodes)} nodes")
```

## 🎯 Key Concepts from [Official Documentation](https://help.getzep.com/graphiti/working-with-data/searching)

### When to Use Each Search Strategy

**Basic Hybrid Search (`graphiti.search()`)**:
- **Good for**: General exploration, broad discovery
- **Returns**: Mixed results (facts from edges)
- **Use when**: You want comprehensive results combining semantic + BM25

**Node-Focused Search (`NODE_HYBRID_SEARCH_RRF`)**:
- **Good for**: Finding entities, concepts, people
- **Returns**: EntityNodes (Alice, Python, Variables)  
- **Use when**: You need to identify key concepts or actors

**Edge-Focused Search (`EDGE_HYBRID_SEARCH_RRF`)**:
- **Good for**: Finding relationships, interactions
- **Returns**: Relationships (Alice → Python, Bob → Alice)
- **Use when**: You want to understand connections and dependencies

**Combined Search (`COMBINED_HYBRID_SEARCH_RRF`)**:
- **Good for**: Comprehensive analysis
- **Returns**: Nodes + Edges + Communities
- **Use when**: You need complete picture of topic

### Search Strategy Comparison Results

From our example with query "Alice learning Python programming":

| Strategy | Focus | Results | Best For |
|----------|-------|---------|----------|
| **Basic Hybrid** | Facts/statements | 6 text results | General discovery |
| **Node-Focused** | Entities | 4 concept nodes | Finding key actors/topics |
| **Edge-Focused** | Relationships | 3 connections | Understanding interactions |
| **Combined** | Everything | 4 nodes + 3 edges + 1 community | Complete analysis |

## ✅ Verification Checklist

- [ ] All four search strategies tested with same query
- [ ] Different result types clearly understood (facts vs nodes vs edges)
- [ ] Search recipe configurations working properly
- [ ] Neo4j queries showing search results visually
- [ ] Comparison table showing strategy differences clearly

## 🤔 Common Questions

**Q: Why do the different strategies return different numbers of results?**
A: Each strategy focuses on different graph elements - basic search returns facts, node search returns entities, edge search returns relationships.

**Q: Which search strategy should I use for educational applications?**
A: Start with basic hybrid search for exploration, then use node-focused to find key concepts, and edge-focused to understand learning relationships.

**Q: What's the benefit of using the same query across strategies?**
A: It shows you different "views" of the same information - facts vs entities vs relationships - helping you understand what each strategy reveals.

**Q: How do I know if my search is working well?**
A: Check if results make sense, try different queries, and use Neo4j to visually explore what was found.

## 📝 What You Learned

✅ **Search Strategy Comparison**: Tested four different approaches on the same query
✅ **Result Type Understanding**: Distinguished between facts, entities, and relationships  
✅ **Search Recipe Configuration**: Used pre-built recipes for focused searches
✅ **Practical Application**: Saw how different strategies reveal different insights
✅ **Visual Exploration**: Used Neo4j queries to explore search results manually

## 🎯 Next Steps

**Outstanding work!** You now master the art of finding exactly what you need in complex educational knowledge graphs.

**Ready to manipulate your knowledge graph directly?** Continue to **[07_crud_operations](../07_crud_operations/)** where you'll learn to create, read, update, and delete nodes and edges with surgical precision.

**What's Coming**: Instead of just searching for information, you'll learn to directly modify your knowledge graph for precise maintenance and integration with external systems!

---

**Key Takeaway**: Different search strategies are like different lenses - each reveals a unique view of the same information. Use the right lens for the right question! 🔍

*"One query, four strategies, four different insights. That's the power of Graphiti search."*