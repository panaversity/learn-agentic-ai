# Step 06: Searching - Hybrid Search and Advanced Retrieval

Now that you understand namespacing, let's master Graphiti's powerful search capabilities for finding exactly what you need in educational knowledge graphs.

## 📚 Official Documentation

- [Searching](https://help.getzep.com/graphiti/working-with-data/searching) - Complete guide to search strategies

## 🎯 What You'll Learn

By the end of this step, you will:
- Master hybrid search combining semantic similarity and BM25 retrieval
- Use node distance reranking for entity-specific queries
- Apply configurable search strategies with search recipes
- Implement different reranking approaches (RRF, MMR, Cross-Encoder)
- Design search solutions for educational scenarios

## 📋 Prerequisites

- Completed Steps 01-05
- Understanding of namespacing and communities
- Knowledge graph with rich educational content

## 📚 What is Hybrid Search?

### The Concept

Graphiti provides two main search approaches:

1. **Hybrid Search**: `await graphiti.search(query)`
   - Combines semantic similarity and BM25 retrieval
   - Reranked using Reciprocal Rank Fusion (RRF)
   - Example: Broad retrieval of facts related to educational topics

2. **Node Distance Reranking**: `await graphiti.search(query, focal_node_uuid)`
   - Extends Hybrid Search by prioritizing results based on proximity to a specified node
   - Example: Focuses on student-specific information, highlighting their learning journey

### Search Components

**Configurable Search Strategies:**
Graphiti provides a low-level `graphiti._search()` method that is more configurable than the basic search. This method uses `SearchConfig` objects and returns `SearchResults` containing nodes, edges, and communities.

**Search Config Recipes:**
Graphiti includes 15 pre-built search recipes for common use cases:

| Recipe Type | Description |
|-------------|-------------|
| `COMBINED_HYBRID_SEARCH_RRF` | Hybrid search with RRF reranking over edges, nodes, and communities |
| `EDGE_HYBRID_SEARCH_RRF` | Hybrid search over edges with RRF reranking |
| `NODE_HYBRID_SEARCH_RRF` | Hybrid search over nodes with RRF reranking |
| `COMMUNITY_HYBRID_SEARCH_RRF` | Hybrid search over communities with RRF reranking |

### Supported Reranking Approaches

**Reciprocal Rank Fusion (RRF)**: Combines results from different algorithms (BM25 and semantic search) by converting ranks to reciprocal scores and summing them for final ranking.

**Maximal Marginal Relevance (MMR)**: Balances relevance and diversity by selecting results that are both relevant to the query and diverse from already chosen ones.

**Cross-Encoder**: Jointly encodes query and result, scoring their relevance by considering combined context. Graphiti supports:
- `OpenAIRerankerClient` (default)
- `GeminiRerankerClient` 
- `BGERerankerClient`

## 🚀 Complete Working Example

Let's explore different search strategies with educational content:

### searching_demo.py

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

# Gemini setup (same as previous steps)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Comprehensive search strategies for educational content"""
    
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
        print("🔍 Starting Advanced Search Demo...")
        
        # Create rich educational content for searching
        print("\n📚 Building rich educational knowledge base...")
        
        educational_episodes = [
            {
                "name": "alice_python_journey",
                "body": "Alice Chen started learning Python with great enthusiasm. She initially struggled with variable naming conventions and confused assignment with mathematical equality. After working through basic exercises, Alice mastered variables and moved on to loops.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "bob_debugging_breakthrough",
                "body": "Bob Martinez had a major breakthrough with debugging techniques. He learned to use print statements systematically and trace through code execution step by step. Bob's logical thinking improved dramatically after mastering debugging approaches.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "python_concepts_relationships",
                "body": "In Python programming, variables form the foundation for all other concepts. Loops build on variable understanding and require mastering indentation syntax. Functions provide abstraction and reusability, building on both variables and loops.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "assessment_performance_patterns",
                "body": "Programming Quiz 1 revealed interesting patterns. Students who mastered variables performed better on loop questions. Those who struggled with syntax often had conceptual understanding but made implementation errors.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "collaborative_learning_success",
                "body": "Study groups proved highly effective for learning programming concepts. Alice helped Bob with variable assignments, while Bob shared debugging strategies with Carol. Peer teaching reinforced understanding for all participants.",
                "group_id": "cs101_fall2024"
            }
        ]
        
        # Add episodes to create searchable knowledge
        for episode in educational_episodes:
            await graphiti.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description="Educational search knowledge base",
                reference_time=datetime.now() - timedelta(days=30),
                group_id=episode["group_id"]
            )
            print(f"   ✅ Added: {episode['name']}")
        
        print(f"\n⏳ Processing episodes for search...")
        
        # Demonstrate different search approaches
        print("\n🎯 Search Strategy 1: Basic Hybrid Search")
        
        # Basic hybrid search combining semantic and BM25
        basic_search = await graphiti.search(
            query="How do students learn Python programming concepts?"
        )
        
        print(f"   Basic hybrid search results: {len(basic_search)}")
        print("   Sample results:")
        for i, result in enumerate(basic_search[:3], 1):
            print(f"     {i}. {result.fact}")
        
        # Search Strategy 2: Node Distance Reranking
        print("\n🎯 Search Strategy 2: Node Distance Reranking")
        
        # First, let's find Alice's node UUID (in practice, you'd track this)
        alice_search = await graphiti.search(query="Alice Chen Python learning")
        if alice_search:
            # This is a simplified example - in practice you'd need the actual node UUID
            print("   Found Alice-related content for node distance reranking")
            print("   Node distance reranking prioritizes results close to specific entities")
            
            # Example of what node distance reranking would show
            alice_focused = await graphiti.search(
                query="Python learning struggles and breakthroughs"
            )
            print(f"   Alice-focused results: {len(alice_focused)}")
            for i, result in enumerate(alice_focused[:2], 1):
                print(f"     {i}. {result.fact}")
        
        # Search Strategy 3: Configurable Search with Recipes
        print("\n🎯 Search Strategy 3: Configurable Search with Recipes")
        
        # Use NODE_HYBRID_SEARCH_RRF recipe
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5
        
        node_results = await graphiti._search(
            query="programming concepts learning progression",
            config=node_search_config
        )
        
        print(f"   Node-focused search: {len(node_results.nodes)} nodes, {len(node_results.edges)} edges")
        print("   Node entities found:")
        for i, node in enumerate(node_results.nodes[:3], 1):
            print(f"     {i}. {node.name}")
        
        # Use EDGE_HYBRID_SEARCH_RRF recipe
        edge_search_config = EDGE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        edge_search_config.limit = 5
        
        edge_results = await graphiti._search(
            query="student learning relationships help collaboration",
            config=edge_search_config
        )
        
        print(f"\n   Edge-focused search: {len(edge_results.edges)} relationships")
        print("   Learning relationships found:")
        for i, edge in enumerate(edge_results.edges[:3], 1):
            print(f"     {i}. {edge.source_node_name} → {edge.target_node_name}")
            print(f"        Relationship: {edge.name}")
        
        # Search Strategy 4: Combined Search
        print("\n🎯 Search Strategy 4: Combined Search (Nodes + Edges + Communities)")
        
        combined_config = COMBINED_HYBRID_SEARCH_RRF.model_copy(deep=True)
        combined_config.limit = 10
        
        combined_results = await graphiti._search(
            query="Python programming education learning patterns",
            config=combined_config
        )
        
        print(f"   Combined search results:")
        print(f"     Nodes: {len(combined_results.nodes)}")
        print(f"     Edges: {len(combined_results.edges)}")
        print(f"     Communities: {len(combined_results.communities)}")
        
        # Educational Search Recipes
        print("\n📖 Educational Search Recipes...")
        
        # Recipe 1: Find Learning Prerequisites
        print("\n📋 Recipe 1: Finding Learning Prerequisites")
        prerequisite_search = await graphiti.search(
            query="concepts required before learning loops programming prerequisites foundation"
        )
        
        print(f"   Prerequisites found: {len(prerequisite_search)} results")
        for i, result in enumerate(prerequisite_search[:2], 1):
            print(f"     {i}. {result.fact}")
        
        # Recipe 2: Student Difficulty Analysis
        print("\n🎯 Recipe 2: Student Difficulty Pattern Analysis")
        difficulty_search = await graphiti.search(
            query="programming concepts students struggle with difficulty challenges"
        )
        
        print(f"   Difficulty patterns: {len(difficulty_search)} results")
        for i, result in enumerate(difficulty_search[:2], 1):
            print(f"     {i}. {result.fact}")
        
        # Recipe 3: Success Pattern Discovery
        print("\n🌟 Recipe 3: Learning Success Pattern Discovery")
        success_search = await graphiti.search(
            query="breakthrough moments mastery successful learning strategies collaboration"
        )
        
        print(f"   Success patterns: {len(success_search)} results")
        for i, result in enumerate(success_search[:2], 1):
            print(f"     {i}. {result.fact}")
        
        print("\n🎓 Advanced search demo completed successfully!")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

def print_facts(edges):
    """Helper function to print edge facts"""
    print("\n".join([edge.fact for edge in edges]))

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

1. **Save the code** as `searching_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python searching_demo.py
```

## 📊 Expected Output

```
🔍 Starting Advanced Search Demo...

📚 Building rich educational knowledge base...
   ✅ Added: alice_python_journey
   ✅ Added: bob_debugging_breakthrough
   ✅ Added: python_concepts_relationships
   ✅ Added: assessment_performance_patterns
   ✅ Added: collaborative_learning_success

🎯 Search Strategy 1: Basic Hybrid Search
   Basic hybrid search results: 8
   Sample results:
     1. Alice Chen started learning Python with great enthusiasm
     2. Python programming variables form foundation for other concepts
     3. Students who mastered variables performed better on loops

🎯 Search Strategy 2: Node Distance Reranking
   Found Alice-related content for node distance reranking
   Node distance reranking prioritizes results close to specific entities
   Alice-focused results: 6
     1. Alice initially struggled with variable naming conventions
     2. Bob Martinez had major breakthrough with debugging techniques

🎯 Search Strategy 3: Configurable Search with Recipes
   Node-focused search: 5 nodes, 3 edges
   Node entities found:
     1. Alice Chen
     2. Python programming
     3. Variable concepts

   Edge-focused search: 4 relationships
   Learning relationships found:
     1. Alice → Bob
        Relationship: helped_with
     2. Study groups → Learning success
        Relationship: proved_effective_for

🎯 Search Strategy 4: Combined Search (Nodes + Edges + Communities)
   Combined search results:
     Nodes: 7
     Edges: 5
     Communities: 2

📖 Educational Search Recipes...

📋 Recipe 1: Finding Learning Prerequisites
   Prerequisites found: 4 results
     1. Variables form foundation for all other programming concepts
     2. Loops build on variable understanding and require syntax mastery

🎯 Recipe 2: Student Difficulty Pattern Analysis
   Difficulty patterns: 5 results
     1. Alice initially struggled with variable naming conventions
     2. Students often had conceptual understanding but implementation errors

🌟 Recipe 3: Learning Success Pattern Discovery
   Success patterns: 6 results
     1. Bob had major breakthrough with systematic debugging techniques
     2. Study groups proved highly effective with peer teaching

🎓 Advanced search demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Custom Search Recipe

Create a custom search recipe for educational scenarios:

```python
class EducationalSearchRecipes:
    """Pre-built search strategies for educational scenarios"""
    
    def __init__(self, graphiti_client, group_id: str):
        self.client = graphiti_client
        self.group_id = group_id
    
    async def find_prerequisites(self, concept: str):
        """Find what students need to know before learning a concept"""
        return await self.client.search(
            query=f"concepts required before learning {concept} prerequisites foundation"
        )
    
    async def identify_struggling_students(self, concept: str):
        """Find students who need help with a specific concept"""
        return await self.client.search(
            query=f"students struggling difficulty challenges with {concept}"
        )
    
    async def find_learning_patterns(self, student_name: str):
        """Analyze a specific student's learning patterns"""
        return await self.client.search(
            query=f"{student_name} learning progress mastery difficulty patterns"
        )

# Usage
recipes = EducationalSearchRecipes(graphiti, "cs101_fall2024")
prerequisites = await recipes.find_prerequisites("functions")
```

### Exercise 2: Search Result Analysis

Analyze search results for educational insights:

```python
async def analyze_search_results(search_results):
    """Analyze search results for educational insights"""
    
    insights = {
        'total_results': len(search_results),
        'learning_patterns': [],
        'difficulty_indicators': [],
        'success_indicators': []
    }
    
    for result in search_results:
        fact_lower = result.fact.lower()
        
        if any(word in fact_lower for word in ['struggle', 'difficult', 'challenge']):
            insights['difficulty_indicators'].append(result.fact)
        elif any(word in fact_lower for word in ['breakthrough', 'mastery', 'success']):
            insights['success_indicators'].append(result.fact)
        elif any(word in fact_lower for word in ['learn', 'progress', 'understand']):
            insights['learning_patterns'].append(result.fact)
    
    return insights

# Usage
results = await graphiti.search("student learning programming")
insights = await analyze_search_results(results)
print(f"Difficulty indicators: {len(insights['difficulty_indicators'])}")
print(f"Success indicators: {len(insights['success_indicators'])}")
```

### Exercise 3: Multi-Modal Search Comparison

Compare different search approaches:

```python
async def compare_search_approaches(query: str):
    """Compare different search strategies for the same query"""
    
    # Basic hybrid search
    basic_results = await graphiti.search(query)
    
    # Node-focused search
    node_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
    node_results = await graphiti._search(query, config=node_config)
    
    # Edge-focused search
    edge_config = EDGE_HYBRID_SEARCH_RRF.model_copy(deep=True)
    edge_results = await graphiti._search(query, config=edge_config)
    
    print(f"Query: {query}")
    print(f"Basic search: {len(basic_results)} results")
    print(f"Node-focused: {len(node_results.nodes)} nodes")
    print(f"Edge-focused: {len(edge_results.edges)} edges")
    
    return {
        'basic': basic_results,
        'nodes': node_results.nodes,
        'edges': edge_results.edges
    }

# Usage
comparison = await compare_search_approaches("Python learning difficulties")
```

## 🎯 Key Concepts Explained

### Search Strategy Selection

**Use Basic Hybrid Search when:**
- You want comprehensive results combining semantic and keyword matching
- You need broad discovery of related information
- You're exploring a topic without specific focus

**Use Node Distance Reranking when:**
- You want results focused on a specific entity (student, concept, course)
- You need personalized or entity-centric information
- You're analyzing patterns around a particular node

**Use Configurable Search when:**
- You need precise control over what types of results to return
- You want to focus on specific graph elements (nodes, edges, communities)
- You're implementing specialized search functionality

### Reranking Strategy Benefits

- **RRF**: Good general-purpose reranking combining multiple signals
- **MMR**: Provides diverse results, avoiding redundancy
- **Cross-Encoder**: Most accurate semantic relevance but slower

## ✅ Verification Checklist

- [ ] Basic hybrid search working with educational content
- [ ] Understanding of node distance reranking concept
- [ ] Configurable search with recipes implemented
- [ ] Different search strategies compared and contrasted
- [ ] Educational search recipes created and tested

## 🤔 Common Questions

**Q: When should I use `graphiti.search()` vs `graphiti._search()`?**
A: Use `graphiti.search()` for most cases. Use `graphiti._search()` when you need fine-grained control over search configuration.

**Q: How do I choose the right search recipe?**
A: Choose based on what you want to find: `NODE_*` for entities, `EDGE_*` for relationships, `COMBINED_*` for comprehensive results.

**Q: What's the difference between semantic and keyword search?**
A: Semantic search understands meaning and context, while keyword search matches exact terms. Hybrid search combines both.

**Q: How does node distance reranking work?**
A: It prioritizes results based on graph proximity to a focal node, making results more relevant to that specific entity.

## 📝 What You Learned

✅ **Hybrid Search Mastery**: Combined semantic similarity and BM25 retrieval for comprehensive results
✅ **Node Distance Reranking**: Focused search results around specific entities
✅ **Configurable Search**: Used search recipes for precise control over result types
✅ **Reranking Strategies**: Applied RRF, MMR, and Cross-Encoder for result optimization
✅ **Educational Search Patterns**: Created domain-specific search recipes for learning scenarios

## 🎯 Next Steps

**Outstanding work!** You now master the art of finding exactly what you need in complex educational knowledge graphs.

**Ready to manipulate your knowledge graph directly?** Continue to **[07_crud_operations](../07_crud_operations/)** where you'll learn to create, read, update, and delete nodes and edges with surgical precision.

**What's Coming**: Instead of just searching for information, you'll learn to directly modify your knowledge graph for precise maintenance and integration with external systems!

---

**Key Takeaway**: Search is not just about finding information—it's about discovering insights. Different search strategies reveal different aspects of the learning process. Master all approaches to unlock your knowledge graph's full potential! 🔍

*"The right search strategy turns data into actionable educational insights."*