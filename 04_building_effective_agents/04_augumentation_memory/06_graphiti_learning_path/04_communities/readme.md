# Step 04: Communities - Discovering Hidden Patterns Automatically

Now that you have custom types creating precise knowledge graphs, let's see how Graphiti automatically discovers groups of related information called "communities".

## 📚 Official Documentation

- [Communities](https://help.getzep.com/graphiti/core-concepts/communities) - Complete guide to community detection

## 🎯 What You'll Learn

By the end of this step, you will:
- Understand what communities are and how they form automatically
- Use `build_communities()` to discover hidden patterns in your data
- See how communities group related students, topics, and concepts
- Update communities dynamically as new episodes are added
- Apply community insights to educational scenarios

## 📋 Prerequisites

- Completed Steps 01-03
- Understanding of episodes and custom types
- Knowledge graph with interconnected data

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
- Periodic rebuilding is still recommended for optimal grouping

### Why Communities Matter

- **Pattern Discovery**: Find hidden relationships you didn't know existed
- **Auto-Organization**: Content groups itself meaningfully through algorithmic analysis
- **Better Search**: Focus queries within relevant communities for more targeted results
- **Learning Insights**: Understand how knowledge naturally clusters in your domain
- **High-Level Synthesis**: Get summarized information about what your graph contains

## 🚀 Complete Working Example

Let's see communities discover patterns in educational data:

### communities_demo.py

```python
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Gemini setup (same as previous steps)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """See how communities automatically discover learning patterns"""
    
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
        print("🏘️ Starting Communities Discovery Demo...")
        
        # Add episodes that will create natural clusters
        learning_episodes = [
            # Python Programming Cluster
            {
                "name": "alice_python_basics",
                "body": "Alice Chen started learning Python programming. She's working on variables, loops, and basic syntax. Alice finds Python syntax intuitive coming from her biology background.",
                "days_ago": 20
            },
            {
                "name": "bob_python_struggles",
                "body": "Bob Martinez is struggling with Python functions and scope. He understands loops but gets confused with function parameters and return values.",
                "days_ago": 18
            },
            {
                "name": "alice_helps_bob",
                "body": "Alice helped Bob understand Python functions by explaining them using biological processes as analogies. Bob now grasps function parameters better.",
                "days_ago": 15
            },
            
            # Web Development Cluster
            {
                "name": "charlie_html_css",
                "body": "Charlie Kim is learning web development, focusing on HTML structure and CSS styling. He's building a portfolio website to showcase his projects.",
                "days_ago": 19
            },
            {
                "name": "diana_javascript",
                "body": "Diana Rodriguez is mastering JavaScript for interactive web features. She's working on DOM manipulation and event handling for dynamic websites.",
                "days_ago": 17
            },
            {
                "name": "charlie_diana_collaboration",
                "body": "Charlie and Diana are collaborating on a web project. Charlie handles the HTML/CSS structure while Diana adds JavaScript interactivity.",
                "days_ago": 12
            },
            
            # Data Science Cluster
            {
                "name": "eve_data_analysis",
                "body": "Eve Thompson is learning data analysis with Python. She's using pandas for data manipulation and matplotlib for visualization.",
                "days_ago": 16
            },
            {
                "name": "frank_machine_learning",
                "body": "Frank Wilson is studying machine learning algorithms. He's implementing linear regression and decision trees using scikit-learn.",
                "days_ago": 14
            },
            {
                "name": "eve_frank_data_project",
                "body": "Eve and Frank are working together on a data science project, combining Eve's data analysis skills with Frank's machine learning knowledge.",
                "days_ago": 10
            },
            
            # Cross-cluster connections
            {
                "name": "alice_web_backend",
                "body": "Alice is helping Charlie add Python backend functionality to his website using Flask. This connects her Python skills to web development.",
                "days_ago": 8
            },
            {
                "name": "diana_data_visualization",
                "body": "Diana is learning to create interactive data visualizations using JavaScript and D3.js, connecting web development with data science.",
                "days_ago": 6
            }
        ]
        
        # Add all episodes
        print("\n📝 Adding learning episodes to create knowledge graph...")
        for episode in learning_episodes:
            await graphiti.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description="Student learning activity",
                reference_time=datetime.now() - timedelta(days=episode["days_ago"])
            )
        
        print("✅ All episodes added!")
        
        # Build communities to discover patterns
        print("\n🔍 Building communities to discover learning patterns...")
        await graphiti.build_communities()
        print("✅ Communities built successfully!")
        
        # Search to see what communities were discovered
        print("\n📊 Exploring discovered communities...")
        
        # General search to see all entities
        all_results = await graphiti.search(
            query="students learning programming web development data science",
            num_results=20
        )
        
        print(f"\n🧑‍🎓 Total entities in knowledge graph: {len(all_results)}")
        
        # Look for Python programming community
        print("\n🐍 Searching for Python Programming Community...")
        python_results = await graphiti.search(
            query="Alice Bob Python programming functions loops syntax",
            num_results=10
        )
        
        print(f"Python community insights ({len(python_results)} results):")
        for i, result in enumerate(python_results[:4], 1):
            print(f"  {i}. {result.fact}")
        
        # Look for web development community
        print("\n🌐 Searching for Web Development Community...")
        web_results = await graphiti.search(
            query="Charlie Diana HTML CSS JavaScript web development",
            num_results=10
        )
        
        print(f"Web development community insights ({len(web_results)} results):")
        for i, result in enumerate(web_results[:4], 1):
            print(f"  {i}. {result.fact}")
        
        # Look for data science community
        print("\n📈 Searching for Data Science Community...")
        data_results = await graphiti.search(
            query="Eve Frank data analysis machine learning pandas scikit-learn",
            num_results=10
        )
        
        print(f"Data science community insights ({len(data_results)} results):")
        for i, result in enumerate(data_results[:4], 1):
            print(f"  {i}. {result.fact}")
        
        # Look for cross-community connections
        print("\n🔗 Searching for Cross-Community Connections...")
        bridge_results = await graphiti.search(
            query="Alice helping Charlie Python web backend Diana visualization",
            num_results=8
        )
        
        print(f"Bridge connections ({len(bridge_results)} results):")
        for i, result in enumerate(bridge_results[:3], 1):
            print(f"  {i}. {result.fact}")
        
        # Demonstrate dynamic community updates
        print("\n⚡ Demonstrating dynamic community updates...")
        
        # Add a new episode and update communities
        await graphiti.add_episode(
            name="new_student_joins",
            episode_body=(
                "Grace Lee just joined the study group. She has experience in both Python "
                "and web development, and she's interested in learning data visualization. "
                "Grace immediately connected with Alice, Charlie, and Diana."
            ),
            source=EpisodeType.text,
            source_description="New student integration",
            reference_time=datetime.now(),
            update_communities=True  # This updates communities dynamically
        )
        
        print("✅ New episode added with community update!")
        
        # Search for the new connections
        grace_results = await graphiti.search(
            query="Grace Lee Python web development data visualization connections",
            num_results=6
        )
        
        print(f"\nNew community connections with Grace ({len(grace_results)} results):")
        for i, result in enumerate(grace_results[:3], 1):
            print(f"  {i}. {result.fact}")
        
        print("\n🎓 Communities demo completed successfully!")
                
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

1. **Save the code** as `communities_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python communities_demo.py
```

## 📊 Expected Output

```
🏘️ Starting Communities Discovery Demo...

📝 Adding learning episodes to create knowledge graph...
✅ All episodes added!

🔍 Building communities to discover learning patterns...
✅ Communities built successfully!

📊 Exploring discovered communities...

🧑‍🎓 Total entities in knowledge graph: 15

🐍 Searching for Python Programming Community...
Python community insights (6 results):
  1. Alice Chen started learning Python programming with variables and loops
  2. Bob Martinez struggles with Python functions and scope
  3. Alice helped Bob understand Python functions using biological analogies
  4. Alice finds Python syntax intuitive from her biology background

🌐 Searching for Web Development Community...
Web development community insights (5 results):
  1. Charlie Kim is learning HTML structure and CSS styling
  2. Diana Rodriguez is mastering JavaScript for interactive features
  3. Charlie and Diana are collaborating on a web project
  4. Charlie handles HTML/CSS while Diana adds JavaScript interactivity

📈 Searching for Data Science Community...
Data science community insights (4 results):
  1. Eve Thompson is learning data analysis with Python and pandas
  2. Frank Wilson is studying machine learning with scikit-learn
  3. Eve and Frank are working on a data science project together
  4. Eve handles data analysis while Frank provides machine learning expertise

🔗 Searching for Cross-Community Connections...
Bridge connections (3 results):
  1. Alice is helping Charlie add Python backend to his website
  2. Diana is learning interactive data visualization with D3.js
  3. Alice connects Python skills to web development through Flask

⚡ Demonstrating dynamic community updates...
✅ New episode added with community update!

New community connections with Grace (3 results):
  1. Grace Lee joined the study group with Python and web experience
  2. Grace is interested in learning data visualization
  3. Grace connected with Alice, Charlie, and Diana immediately

🎓 Communities demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Add Your Own Learning Cluster

Create a new learning community:

```python
# Add episodes about a mobile development cluster
mobile_episodes = [
    "Hannah is learning iOS development with Swift and Xcode",
    "Ivan is building Android apps with Kotlin and Android Studio", 
    "Hannah and Ivan are sharing mobile development best practices",
    "Hannah is helping Ivan understand iOS design patterns"
]

for i, episode in enumerate(mobile_episodes):
    await graphiti.add_episode(
        name=f"mobile_episode_{i}",
        episode_body=episode,
        source=EpisodeType.text,
        reference_time=datetime.now() - timedelta(days=i)
    )

# Rebuild communities to include the new cluster
await graphiti.build_communities()
```

### Exercise 2: Analyze Community Evolution

Track how communities change over time:

```python
# Before adding new data
initial_results = await graphiti.search("learning communities", num_results=20)
print(f"Initial entities: {len(initial_results)}")

# Add new learning experiences
await graphiti.add_episode(
    name="cross_training",
    episode_body="Students are now cross-training in multiple areas",
    source=EpisodeType.text,
    update_communities=True  # Dynamic update
)

# After adding new data
updated_results = await graphiti.search("learning communities", num_results=20)
print(f"Updated entities: {len(updated_results)}")
```

### Exercise 3: Find Bridge Students

Identify students who connect multiple communities:

```python
# Search for students who appear in multiple learning areas
bridge_results = await graphiti.search(
    query="students helping across different programming areas",
    num_results=15
)

print("Bridge students found:")
for result in bridge_results:
    if "helping" in result.fact or "connected" in result.fact:
        print(f"  • {result.fact}")
```

## 🎯 Key Concepts Explained

### Community Detection Process

1. **Episode Addition** → Creates entities and relationships
2. **Connection Analysis** → Identifies strongly connected entities
3. **Leiden Algorithm** → Groups entities into communities
4. **Summary Generation** → Creates descriptions of each community

### Dynamic Community Updates

```python
# Option 1: Rebuild all communities (recommended periodically)
await graphiti.build_communities()

# Option 2: Update existing communities (for new episodes)
await graphiti.add_episode(
    episode_body="New learning content...",
    update_communities=True  # Dynamically updates communities
)
```

### Community-Based Insights

Communities reveal:
- **Learning Patterns**: Which topics students study together
- **Skill Clusters**: Which skills naturally group together
- **Social Learning**: Which students collaborate frequently
- **Knowledge Bridges**: Which concepts connect different areas

## ✅ Verification Checklist

- [ ] Communities built successfully with `build_communities()`
- [ ] Multiple learning clusters discovered (Python, Web, Data Science)
- [ ] Cross-community connections identified
- [ ] Dynamic community updates working with new episodes
- [ ] Search results show community-based patterns

## 🤔 Common Questions

**Q: How many communities should I expect?**
A: It depends on your data, but typically 3-7 meaningful communities emerge from educational content.

**Q: Can entities belong to multiple communities?**
A: The Leiden algorithm typically assigns each entity to one primary community, but entities can have connections across communities.

**Q: How often should I rebuild communities?**
A: Use `update_communities=True` for ongoing additions, but rebuild periodically (weekly/monthly) for optimal grouping.

**Q: What if communities don't make sense educationally?**
A: This usually means you need more interconnected episodes or better episode quality to create meaningful relationships.

## 📝 What You Learned

✅ **Community Detection**: Used `build_communities()` to discover hidden patterns
✅ **Learning Clusters**: Saw how students and topics naturally group together  
✅ **Dynamic Updates**: Updated communities as new learning episodes are added
✅ **Pattern Recognition**: Identified bridge connections between different learning areas
✅ **Educational Insights**: Understood how knowledge naturally organizes itself

## 🎯 Next Steps

**Fantastic work!** You now understand how knowledge naturally clusters and can leverage these patterns for educational insights.

**Ready to isolate different educational contexts?** Continue to **[05_graph_namespacing](../05_graph_namespacing/)** where you'll learn how to create separate graph spaces for different schools, classes, or organizations.

**What's Coming**: Instead of one big knowledge graph, you'll create isolated environments where different educational contexts don't interfere with each other - perfect for multi-tenant educational systems!

---

**Key Takeaway**: Communities emerge automatically from your data and reveal the natural structure of learning. They're like "knowledge neighborhoods" that help you understand how concepts and students naturally cluster together! 🏘️

*"Knowledge that connects together, stays together. Communities reveal the hidden structure of learning."*