# Working with Data 01: [Searching the Graph](https://help.getzep.com/graphiti/working-with-data/searching) - Hybrid Search and Advanced Retrieval

Welcome to Step 06! This step uses **Socratic questioning** and **Zone of Proximal Development** to master Graphiti's search capabilities.

## 🎯 Learning Objectives

By the end of this step, you will:
- Master hybrid search combining semantic, keyword, and graph-based retrieval
- Implement advanced search strategies for educational content
- Use reranking techniques for result optimization
- Design search recipes for specific educational scenarios
- Apply search analytics for learning insights

## 📚 Core Concepts (Building on Namespacing)

### What is Hybrid Search?

**Hybrid Search** in Graphiti combines multiple search modalities to find the most relevant information:

1. **Semantic Search** - Understanding meaning and context
2. **Keyword Search (BM25)** - Traditional text matching
3. **Graph-Based Search** - Relationship traversal and community-aware retrieval
4. **Temporal Search** - Time-aware relevance

**Educational Power:**
- **Concept Discovery**: Find related learning concepts semantically
- **Precision Matching**: Exact terminology when needed
- **Learning Pathways**: Graph traversal reveals prerequisite chains
- **Historical Context**: Temporal search tracks learning progression

### Search Components in Graphiti

**Search Scope Options:**
- `scope='nodes'` - Search entities only
- `scope='edges'` - Search relationships only  
- `scope='both'` - Search entities and relationships (default)

**Reranking Strategies:**
- `reranker='mmr'` - Maximum Marginal Relevance (diversity)
- `reranker='cross_encoder'` - Deep semantic reranking
- `reranker='none'` - No additional reranking

**Search Filters:**
- `search_filters={'node_types': ['Student']}` - Filter by entity types
- `search_filters={'edge_types': ['ENROLLED_IN']}` - Filter by relationship types
- `community_ids=[...]` - Search within specific communities
- `group_id='...'` - Namespace-constrained search

## 🚀 Worked Examples (Schaum's Method)

### Example 1: Educational Search Strategies

```python
# educational_search_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def educational_search_strategies():
    """Schaum's Worked Example: Advanced search for educational content"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("🔍 SCHAUM'S EXAMPLE: Educational Search Strategies")
        print("=" * 60)
        
        await client.build_indices_and_constraints()
        
        # First, create rich educational content for searching
        print("\n📚 Phase 1: Building rich educational knowledge base...")
        
        educational_episodes = [
            {
                "name": "python_variables_concept",
                "body": "Variables in Python store data values. Students learn variable assignment using the equals operator. Common variable types include strings, integers, floats, and booleans. Variables are fundamental to all programming concepts and enable data manipulation.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "alice_variables_struggle",
                "body": "Alice Chen initially struggled with variable naming conventions in Python. She confused variable assignment with mathematical equality. After practice with meaningful variable names, Alice mastered the concept and helped other students.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "loops_programming_concept",
                "body": "For loops and while loops enable repetition in programming. Students use loops to iterate through data structures like lists and strings. Loop concepts build on variable understanding and require mastering indentation syntax.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "bob_loops_breakthrough",
                "body": "Bob Martinez had a breakthrough moment with loops when working on a DNA sequence analysis project. He realized loops could automate repetitive tasks and connected the concept to real-world problem solving.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "functions_abstraction_concept",
                "body": "Functions provide abstraction and code reusability in programming. Students learn to define functions with parameters and return values. Functions build on variables and loops, enabling modular programming design.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "debugging_systematic_approach",
                "body": "Debugging requires systematic thinking and careful observation. Students learn to use print statements, trace through code execution, and identify logical errors. Debugging skills improve with practice and methodical approaches.",
                "group_id": "cs101_fall2024"
            },
            {
                "name": "assessment_quiz_performance",
                "body": "Programming Quiz 1 tested variable assignment, loop construction, and basic function definition. Student performance varied: some excelled at syntax, others at problem-solving logic. Quiz results guided individualized learning plans.",
                "group_id": "cs101_fall2024"
            }
        ]
        
        # Add episodes to create searchable knowledge
        for episode in educational_episodes:
            await client.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description="Educational search knowledge base",
                reference_time=datetime.now() - timedelta(days=30),
                group_id=episode["group_id"]
            )
            print(f"   ✅ Added: {episode['name']}")
        
        print(f"\n⏳ Processing {len(educational_episodes)} episodes for search...")
        await asyncio.sleep(6)
        
        # Phase 2: Demonstrate different search strategies
        print("\n🎯 Phase 2: Exploring search strategies...")
        
        # Strategy 1: Semantic Search for Concepts
        print("\n🧠 Strategy 1: Semantic Search for Learning Concepts")
        semantic_search = await client.search(
            query="How do programming concepts build on each other?",
            scope='both',  # Search nodes and edges
            limit=8,
            group_id="cs101_fall2024"
        )
        
        print(f"   Semantic results: {len(semantic_search.nodes)} entities, {len(semantic_search.edges)} relationships")
        print(f"   Conceptual entities found:")
        for node in semantic_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Strategy 2: Keyword Search for Specific Terms
        print("\n🔤 Strategy 2: Keyword Search for Specific Programming Terms")
        keyword_search = await client.search(
            query="Python variables assignment equals operator",
            scope='nodes',
            limit=6,
            group_id="cs101_fall2024"
        )
        
        print(f"   Keyword results: {len(keyword_search.nodes)} entities")
        print(f"   Variable-related entities:")
        for node in keyword_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Strategy 3: Relationship-Focused Search
        print("\n🔗 Strategy 3: Relationship-Focused Search")
        relationship_search = await client.search(
            query="student learning progression difficulty breakthrough",
            scope='edges',  # Focus on relationships
            limit=10,
            group_id="cs101_fall2024"
        )
        
        print(f"   Relationship results: {len(relationship_search.edges)} relationships")
        print(f"   Learning progression relationships:")
        for edge in relationship_search.edges[:4]:
            print(f"     • {edge.source_node_name} → {edge.target_node_name} ({edge.name})")
        
        # Strategy 4: Filtered Search by Entity Types
        print("\n🎯 Strategy 4: Entity Type-Filtered Search")
        try:
            filtered_search = await client.search(
                query="student programming learning experience",
                scope='nodes',
                search_filters={'node_types': ['Student']},  # Only student entities
                limit=5,
                group_id="cs101_fall2024"
            )
            
            print(f"   Student-filtered results: {len(filtered_search.nodes)} student entities")
            for node in filtered_search.nodes:
                print(f"     • {node.name}")
                
        except Exception as e:
            print(f"   Note: Entity filtering may require custom types: {e}")
        
        # Strategy 5: Community-Constrained Search
        print("\n🏘️ Strategy 5: Community-Constrained Search")
        
        # First build communities
        communities = await client.build_communities(group_id="cs101_fall2024")
        
        if communities:
            community_search = await client.search(
                query="programming concepts relationships prerequisites",
                community_ids=[communities[0].uuid],
                limit=8,
                group_id="cs101_fall2024"
            )
            
            print(f"   Community-constrained results: {len(community_search.nodes)} entities")
            print(f"   Community entities:")
            for node in community_search.nodes[:4]:
                print(f"     • {node.name}")
        else:
            print("   No communities detected yet")
        
        # Phase 3: Advanced Search Techniques
        print("\n🚀 Phase 3: Advanced search techniques...")
        
        # Technique 1: Multi-Modal Search with Reranking
        print("\n🎨 Advanced Technique 1: Semantic Search with Cross-Encoder Reranking")
        reranked_search = await client.search(
            query="What programming concepts do students find most challenging?",
            scope='both',
            reranker='cross_encoder',  # Deep semantic reranking
            limit=10,
            group_id="cs101_fall2024"
        )
        
        print(f"   Reranked results: {len(reranked_search.nodes)} entities")
        print(f"   Challenging concept entities (reranked by relevance):")
        for node in reranked_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Technique 2: Diverse Results with MMR
        print("\n🌈 Advanced Technique 2: Maximum Marginal Relevance for Diversity")
        diverse_search = await client.search(
            query="programming learning assessment performance",
            reranker='mmr',  # Maximize diversity
            limit=8,
            group_id="cs101_fall2024"
        )
        
        print(f"   Diverse results: {len(diverse_search.nodes)} entities")
        print(f"   Diverse learning entities:")
        for node in diverse_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Technique 3: Temporal-Aware Search
        print("\n⏰ Advanced Technique 3: Learning Progression Analysis")
        progression_search = await client.search(
            query="student learning journey from struggle to mastery over time",
            scope='both',
            limit=12,
            group_id="cs101_fall2024"
        )
        
        print(f"   Temporal progression results: {len(progression_search.nodes)} entities")
        progression_edges = [e for e in progression_search.edges if 'progress' in e.name.lower() or 'master' in e.name.lower()]
        print(f"   Learning progression relationships: {len(progression_edges)}")
        
        # Phase 4: Educational Search Recipes
        print("\n📖 Phase 4: Educational Search Recipes...")
        
        # Recipe 1: Find Learning Prerequisites
        print("\n📋 Recipe 1: Finding Learning Prerequisites")
        prerequisite_search = await client.search(
            query="concepts that must be learned before functions programming prerequisites",
            scope='both',
            limit=6,
            group_id="cs101_fall2024"
        )
        
        print(f"   Prerequisites found: {len(prerequisite_search.nodes)} concepts")
        prerequisite_edges = [e for e in prerequisite_search.edges if 'before' in e.name.lower() or 'require' in e.name.lower()]
        print(f"   Prerequisite relationships: {len(prerequisite_edges)}")
        
        # Recipe 2: Student Difficulty Analysis
        print("\n🎯 Recipe 2: Student Difficulty Pattern Analysis")
        difficulty_search = await client.search(
            query="which programming concepts do students struggle with most",
            scope='both',
            limit=8,
            group_id="cs101_fall2024"
        )
        
        print(f"   Difficulty analysis: {len(difficulty_search.nodes)} entities")
        struggle_relationships = [e for e in difficulty_search.edges if 'struggle' in e.name.lower() or 'difficult' in e.name.lower()]
        print(f"   Struggle patterns: {len(struggle_relationships)}")
        
        # Recipe 3: Success Pattern Discovery
        print("\n🌟 Recipe 3: Learning Success Pattern Discovery")
        success_search = await client.search(
            query="breakthrough moments mastery successful learning strategies",
            scope='both',
            limit=8,
            group_id="cs101_fall2024"
        )
        
        print(f"   Success patterns: {len(success_search.nodes)} entities")
        success_relationships = [e for e in success_search.edges if 'breakthrough' in e.name.lower() or 'master' in e.name.lower()]
        print(f"   Success relationships: {len(success_relationships)}")
        
        # Socratic Questions for Deep Understanding
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • How does semantic search reveal conceptual relationships?")
        print(f"   • When would you use keyword vs. semantic search in education?")
        print(f"   • How can community-constrained search improve learning recommendations?")
        print(f"   • What patterns emerge from relationship-focused searches?")
        print(f"   • How might reranking strategies affect educational discovery?")
        
        print(f"\n💡 SEARCH STRATEGY INSIGHTS:")
        print(f"   • Hybrid search combines precision and discovery")
        print(f"   • Different scopes reveal different educational insights")
        print(f"   • Reranking optimizes relevance for specific educational goals")
        print(f"   • Community and namespace constraints improve search focus")
        print(f"   • Educational search recipes solve common learning analytics needs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting search:")
        print("   1. Verify sufficient content exists for meaningful search")
        print("   2. Check that entities and relationships have been extracted")
        print("   3. Ensure search parameters match your data structure")
        
    finally:
        await client.close()
        print("\n🔒 Educational search demo completed")

if __name__ == "__main__":
    asyncio.run(educational_search_strategies())
```

## 📚 Practice Problems (Zone of Proximal Development)

### Problem 1: Learning Path Discovery
**Scenario**: A student asks "What should I learn before attempting machine learning?"

**Your Task**: Design search strategies to:
1. Find prerequisite concepts using semantic search
2. Identify the optimal learning sequence
3. Locate students who successfully made this transition

### Problem 2: Personalized Content Recommendation
**Challenge**: Recommend learning materials based on a student's current knowledge and struggles.

**Your Task**:
1. Search for similar student learning patterns
2. Find content that helped students with similar difficulties
3. Use community-based search for contextual recommendations

### Problem 3: Instructor Analytics Dashboard
**Scenario**: An instructor wants insights into how students are progressing through course concepts.

**Your Task**:
1. Design searches to identify knowledge gaps
2. Find concepts students consistently struggle with
3. Discover successful learning interventions

## 🔧 Advanced Techniques

### Custom Search Recipes

```python
class EducationalSearchRecipes:
    """Pre-built search strategies for common educational scenarios"""
    
    def __init__(self, client: Graphiti, group_id: str):
        self.client = client
        self.group_id = group_id
    
    async def find_prerequisites(self, concept: str):
        """Find what students need to know before learning a concept"""
        return await self.client.search(
            query=f"concepts required before learning {concept} prerequisites foundation",
            scope='both',
            reranker='cross_encoder',
            limit=10,
            group_id=self.group_id
        )
    
    async def identify_struggling_students(self, concept: str):
        """Find students who need help with a specific concept"""
        return await self.client.search(
            query=f"students struggling difficulty challenges with {concept}",
            scope='both',
            search_filters={'node_types': ['Student']},
            limit=15,
            group_id=self.group_id
        )
    
    async def find_learning_patterns(self, student_name: str):
        """Analyze a specific student's learning patterns"""
        return await self.client.search(
            query=f"{student_name} learning progress mastery difficulty patterns",
            scope='both',
            reranker='mmr',  # Diverse perspectives
            limit=20,
            group_id=self.group_id
        )
    
    async def discover_teaching_strategies(self, concept: str):
        """Find effective teaching approaches for a concept"""
        return await self.client.search(
            query=f"effective teaching strategies methods for {concept} successful approaches",
            scope='both',
            limit=12,
            group_id=self.group_id
        )
```

### Search Result Analysis

```python
async def analyze_search_results(search_results):
    """Analyze search results for educational insights"""
    
    insights = {
        'total_entities': len(search_results.nodes),
        'total_relationships': len(search_results.edges),
        'entity_types': {},
        'relationship_types': {},
        'learning_patterns': []
    }
    
    # Categorize entities
    for node in search_results.nodes:
        entity_type = classify_educational_entity(node.name)
        insights['entity_types'][entity_type] = insights['entity_types'].get(entity_type, 0) + 1
    
    # Analyze relationships
    for edge in search_results.edges:
        rel_type = classify_educational_relationship(edge.name)
        insights['relationship_types'][rel_type] = insights['relationship_types'].get(rel_type, 0) + 1
    
    # Extract learning patterns
    learning_edges = [e for e in search_results.edges if 'learn' in e.name.lower()]
    for edge in learning_edges:
        insights['learning_patterns'].append({
            'from': edge.source_node_name,
            'to': edge.target_node_name,
            'type': edge.name
        })
    
    return insights

def classify_educational_entity(name: str) -> str:
    """Classify entity into educational categories"""
    name_lower = name.lower()
    if any(word in name_lower for word in ['student', 'learner']):
        return 'Student'
    elif any(word in name_lower for word in ['concept', 'topic', 'skill']):
        return 'Concept'
    elif any(word in name_lower for word in ['assessment', 'quiz', 'test']):
        return 'Assessment'
    elif any(word in name_lower for word in ['instructor', 'teacher', 'professor']):
        return 'Instructor'
    else:
        return 'Other'
```

## ✅ Understanding Check (Socratic Method)

### Essential Questions
1. **Why** does hybrid search outperform single-modality search?
2. **When** would you use semantic vs. keyword search in education?
3. **How** do reranking strategies change search relevance?
4. **What** educational insights emerge from relationship-focused searches?

### Critical Thinking
1. **If** search results are too broad, how do you increase precision?
2. **What if** semantic search misses important exact terminology?
3. **How might** search strategies differ for different learning domains?

### Educational Applications
1. Design search for a student recommendation system
2. Create searches for instructor dashboard analytics
3. Plan search strategies for adaptive learning systems

## 🎯 Next Steps

You now master the art of finding exactly what you need in complex knowledge graphs! You've learned:

✅ **Hybrid search strategies** for educational content  
✅ **Advanced filtering and reranking** techniques  
✅ **Educational search recipes** for common scenarios  
✅ **Search analytics** for learning insights  

**Ready for the next step?** Continue to **[07_crud_operations](../07_crud_operations/)** to learn direct manipulation of nodes and edges for precise knowledge graph management.

## 📝 Key Takeaways

1. **Hybrid search is powerful** - Combines semantic, keyword, and graph-based retrieval
2. **Scope matters** - Nodes, edges, or both reveal different insights  
3. **Reranking optimizes relevance** - Cross-encoder and MMR serve different needs
4. **Filters add precision** - Entity types, communities, and namespaces focus results
5. **Educational recipes solve common needs** - Prerequisites, difficulties, success patterns

---

**Master's Tip**: Search is not just about finding information—it's about discovering insights. Different search strategies reveal different aspects of the learning process. Master all approaches to unlock the full potential of your educational knowledge graph! 🔍

*"The right search strategy turns data into actionable educational insights."* - Learning Analytics Principles