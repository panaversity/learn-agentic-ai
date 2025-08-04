# Step 05: Graph Namespacing - Multi-Tenant Educational Systems

Now that you understand communities, let's learn how to create isolated educational environments using `group_id` for multi-tenant systems.

## 📚 Official Documentation

- [Graph Namespacing](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) - Complete guide to using group_ids

## 🎯 What You'll Learn

By the end of this step, you will:
- Understand multi-tenancy in educational knowledge graphs using `group_id`
- Create isolated learning environments for different schools/courses
- Query within specific namespaces for targeted results
- Apply namespacing to real TutorsGPT scenarios
- Handle cross-namespace analytics when appropriate

## 📋 Prerequisites

- Completed Steps 01-04
- Understanding of communities and search
- Knowledge of multi-tenant system concepts

## 📚 What is Graph Namespacing?

### The Concept

**Graph namespacing** in Graphiti uses `group_id` parameters to create isolated graph environments within the same Graphiti instance. This enables multiple distinct knowledge graphs to coexist without interference.

**Educational Use Cases:**
- **Multi-Institution Platform**: Different schools using the same TutorsGPT system
- **Course Isolation**: Separate CS101 from MATH201 knowledge graphs
- **Semester Separation**: Fall 2024 vs Spring 2025 student cohorts
- **Privacy Boundaries**: Student data isolation for FERPA compliance
- **Testing Environments**: Separate development, testing, and production graphs

### How Namespacing Works

In Graphiti, every node and edge can be associated with a `group_id`. When you specify a `group_id`, you're effectively creating a namespace for that data. Nodes and edges with the same `group_id` form a cohesive, isolated graph that can be queried and manipulated independently.

### Key Benefits

- **Data Isolation**: Prevent data leakage between different namespaces
- **Simplified Management**: Organize and manage related data together
- **Performance Optimization**: Improve query performance by limiting search space
- **Flexible Architecture**: Support multiple use cases within a single Graphiti instance

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

## 🚀 Complete Working Example

Let's create a multi-institution TutorsGPT system with proper namespace isolation:

### namespacing_demo.py

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
    """Multi-institution educational platform with namespace isolation"""
    
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
        print("🏫 Starting Multi-Institution Namespacing Demo...")
        
        # Define institutional namespaces
        institutions = {
            "stanford_cs": "stanford_university_computer_science",
            "mit_eecs": "mit_electrical_engineering_computer_science", 
            "berkeley_cs": "uc_berkeley_computer_science"
        }
        
        # Create isolated institutional knowledge
        print("\n🏛️ Creating isolated institutional environments...")
        
        # Stanford CS101 Episodes
        stanford_episodes = [
            {
                "name": "stanford_cs101_intro",
                "body": "Stanford CS101 emphasizes theoretical foundations with practical Python applications. The course uses problem-based learning and covers algorithmic thinking, data structures, and software engineering principles.",
                "namespace": institutions["stanford_cs"] + "_cs101"
            },
            {
                "name": "stanford_student_alice",
                "body": "Alice Johnson at Stanford is a sophomore majoring in Computer Science. She excels in mathematical reasoning and prefers structured learning approaches. Alice is working on machine learning applications.",
                "namespace": institutions["stanford_cs"] + "_cs101"
            },
            {
                "name": "stanford_professor_smith",
                "body": "Professor David Smith teaches CS101 at Stanford. He has 15 years of experience and specializes in algorithms and computational complexity. His teaching emphasizes rigorous mathematical proofs.",
                "namespace": institutions["stanford_cs"] + "_cs101"
            }
        ]
        
        # MIT EECS Episodes
        mit_episodes = [
            {
                "name": "mit_6001_intro",
                "body": "MIT 6.001 Structure and Interpretation of Computer Programs focuses on programming paradigms and computational thinking. The course emphasizes functional programming, recursion, and program design methodologies.",
                "namespace": institutions["mit_eecs"] + "_6001"
            },
            {
                "name": "mit_student_bob",
                "body": "Bob Chen at MIT is a first-year student in EECS. He has strong programming background but struggles with theoretical concepts. Bob prefers hands-on experimentation and collaborative learning.",
                "namespace": institutions["mit_eecs"] + "_6001"
            },
            {
                "name": "mit_professor_garcia",
                "body": "Professor Maria Garcia teaches 6.001 at MIT. She has expertise in programming languages and software systems. Her teaching combines theoretical depth with practical programming projects.",
                "namespace": institutions["mit_eecs"] + "_6001"
            }
        ]
        
        # UC Berkeley CS Episodes
        berkeley_episodes = [
            {
                "name": "berkeley_cs61a_intro",
                "body": "UC Berkeley CS61A teaches programming paradigms through Python, Scheme, and SQL. The course emphasizes abstraction, recursion, and higher-order functions with a project-based approach.",
                "namespace": institutions["berkeley_cs"] + "_cs61a"
            },
            {
                "name": "berkeley_student_carol",
                "body": "Carol Martinez at UC Berkeley is studying CS61A. She has diverse academic interests and excels in creative problem-solving. Carol benefits from visual learning aids and peer collaboration.",
                "namespace": institutions["berkeley_cs"] + "_cs61a"
            },
            {
                "name": "berkeley_ta_wilson",
                "body": "Teaching Assistant James Wilson supports CS61A at Berkeley. He's a graduate student specializing in educational technology. James focuses on helping students with debugging and conceptual understanding.",
                "namespace": institutions["berkeley_cs"] + "_cs61a"
            }
        ]
        
        # Add all episodes with appropriate namespacing
        all_episodes = stanford_episodes + mit_episodes + berkeley_episodes
        
        for episode in all_episodes:
            await graphiti.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description="Multi-institution knowledge base",
                reference_time=datetime.now() - timedelta(days=30),
                group_id=episode["namespace"]
            )
            institution = episode["namespace"].split("_")[0]
            print(f"   ✅ {institution.upper()}: {episode['name']}")
        
        print(f"\n⏳ Processing {len(all_episodes)} namespaced episodes...")
        
        # Demonstrate namespace isolation
        print("\n🔒 Demonstrating namespace isolation...")
        
        # Search within Stanford namespace only
        stanford_search = await graphiti.search(
            query="computer science programming student professor course",
            group_id=institutions["stanford_cs"] + "_cs101",
            num_results=10
        )
        
        print(f"\n🏛️ Stanford CS101 Namespace Search:")
        print(f"   Entities found: {len(stanford_search)}")
        print(f"   Stanford-specific results:")
        for i, result in enumerate(stanford_search[:3], 1):
            print(f"     {i}. {result.fact}")
        
        # Search within MIT namespace only
        mit_search = await graphiti.search(
            query="computer science programming student professor course",
            group_id=institutions["mit_eecs"] + "_6001",
            num_results=10
        )
        
        print(f"\n🔬 MIT EECS Namespace Search:")
        print(f"   Entities found: {len(mit_search)}")
        print(f"   MIT-specific results:")
        for i, result in enumerate(mit_search[:3], 1):
            print(f"     {i}. {result.fact}")
        
        # Search within Berkeley namespace only
        berkeley_search = await graphiti.search(
            query="computer science programming student professor course",
            group_id=institutions["berkeley_cs"] + "_cs61a",
            num_results=10
        )
        
        print(f"\n🐻 UC Berkeley CS61A Namespace Search:")
        print(f"   Entities found: {len(berkeley_search)}")
        print(f"   Berkeley-specific results:")
        for i, result in enumerate(berkeley_search[:3], 1):
            print(f"     {i}. {result.fact}")
        
        # Cross-namespace analytics (when appropriate)
        print("\n📊 Cross-namespace analytics...")
        
        # Global search across all namespaces (for platform-level insights)
        global_search = await graphiti.search(
            query="teaching methodology programming education approaches",
            num_results=15  # No group_id = search all namespaces
        )
        
        print(f"\n🌍 Cross-Institution Analysis:")
        print(f"   Total results: {len(global_search)}")
        print(f"   Teaching methodology insights:")
        for i, result in enumerate(global_search[:4], 1):
            print(f"     {i}. {result.fact}")
        
        # Multi-tenant application example
        print("\n🏢 Multi-tenant application pattern...")
        
        async def add_customer_data(tenant_id, customer_data):
            """Add customer data to tenant-specific namespace"""
            namespace = f"tenant_{tenant_id}"
            
            await graphiti.add_episode(
                name=f"customer_data_{customer_data['id']}",
                episode_body=customer_data,
                source=EpisodeType.json,
                source_description="Customer profile update",
                reference_time=datetime.now(),
                group_id=namespace  # Namespace by tenant
            )
        
        async def search_tenant_data(tenant_id, query):
            """Search within tenant's namespace"""
            namespace = f"tenant_{tenant_id}"
            
            return await graphiti.search(
                query=query,
                group_id=namespace
            )
        
        # Example tenant data
        tenant_data = {"id": "001", "name": "Student Progress", "course": "CS101"}
        await add_customer_data("university_a", tenant_data)
        
        tenant_results = await search_tenant_data("university_a", "student progress course")
        print(f"   Tenant-specific results: {len(tenant_results)}")
        
        print("\n🎓 Namespacing demo completed successfully!")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

1. **Save the code** as `namespacing_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python namespacing_demo.py
```

## 📊 Expected Output

```
🏫 Starting Multi-Institution Namespacing Demo...

🏛️ Creating isolated institutional environments...
   ✅ STANFORD: stanford_cs101_intro
   ✅ STANFORD: stanford_student_alice
   ✅ STANFORD: stanford_professor_smith
   ✅ MIT: mit_6001_intro
   ✅ MIT: mit_student_bob
   ✅ MIT: mit_professor_garcia
   ✅ BERKELEY: berkeley_cs61a_intro
   ✅ BERKELEY: berkeley_student_carol
   ✅ BERKELEY: berkeley_ta_wilson

🔒 Demonstrating namespace isolation...

🏛️ Stanford CS101 Namespace Search:
   Entities found: 5
   Stanford-specific results:
     1. Stanford CS101 emphasizes theoretical foundations with Python
     2. Alice Johnson at Stanford excels in mathematical reasoning
     3. Professor David Smith specializes in algorithms and complexity

🔬 MIT EECS Namespace Search:
   Entities found: 4
   MIT-specific results:
     1. MIT 6.001 focuses on programming paradigms and computational thinking
     2. Bob Chen at MIT prefers hands-on experimentation
     3. Professor Maria Garcia combines theoretical depth with practical projects

🐻 UC Berkeley CS61A Namespace Search:
   Entities found: 4
   Berkeley-specific results:
     1. UC Berkeley CS61A teaches programming through Python, Scheme, and SQL
     2. Carol Martinez excels in creative problem-solving
     3. James Wilson focuses on helping with debugging and concepts

📊 Cross-namespace analytics...

🌍 Cross-Institution Analysis:
   Total results: 12
   Teaching methodology insights:
     1. Problem-based learning approaches across institutions
     2. Theoretical foundations combined with practical applications
     3. Different programming paradigms and methodologies
     4. Various teaching styles and student support approaches

🎓 Namespacing demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Add More Institutions

Create additional educational namespaces:

```python
# Add more institutions
new_institutions = {
    "harvard_cs": "harvard_university_computer_science",
    "caltech_cs": "caltech_computer_science"
}

# Create episodes for each new institution
harvard_episodes = [
    {
        "name": "harvard_cs50_intro",
        "body": "Harvard CS50 Introduction to Computer Science...",
        "namespace": new_institutions["harvard_cs"] + "_cs50"
    }
]
```

### Exercise 2: Hierarchical Namespacing

Create nested namespace structures:

```python
class NamespaceManager:
    """Manage hierarchical namespace structures"""
    
    def __init__(self, institution: str, department: str, course: str, semester: str):
        self.institution = institution
        self.department = department
        self.course = course
        self.semester = semester
    
    @property
    def full_namespace(self) -> str:
        return f"{self.institution}_{self.department}_{self.course}_{self.semester}"
    
    @property
    def course_namespace(self) -> str:
        return f"{self.institution}_{self.department}_{self.course}"

# Usage
stanford_cs101 = NamespaceManager("stanford", "cs", "cs101", "fall2024")
print(stanford_cs101.full_namespace)  # "stanford_cs_cs101_fall2024"
```

### Exercise 3: Role-Based Namespace Access

Implement intelligent namespace search based on user roles:

```python
async def intelligent_namespace_search(query: str, user_context: dict):
    """Search across appropriate namespaces based on user role"""
    
    primary_namespace = user_context.get("primary_namespace")
    user_role = user_context.get("role")  # student, instructor, admin
    
    if user_role == "student":
        # Students search within their course namespace
        return await graphiti.search(
            query=query,
            group_id=primary_namespace,
            num_results=10
        )
    elif user_role == "instructor":
        # Instructors can search across their courses
        course_namespaces = user_context.get("course_namespaces", [])
        all_results = []
        for namespace in course_namespaces:
            results = await graphiti.search(
                query=query,
                group_id=namespace,
                num_results=5
            )
            all_results.extend(results)
        return all_results
    elif user_role == "admin":
        # Admins can search across institution
        return await graphiti.search(
            query=query,
            num_results=20  # No group_id restriction
        )
```

## 🎯 Key Concepts Explained

### Best Practices for Graph Namespacing

1. **Consistent Naming**: Use consistent naming conventions for `group_id` values
2. **Documentation**: Maintain documentation of namespace structure and purpose
3. **Granularity**: Choose appropriate level of granularity for namespaces
   - Too many namespaces can lead to fragmented data
   - Too few namespaces may not provide sufficient isolation
4. **Cross-namespace Queries**: When necessary, perform multiple queries across namespaces and combine results in application logic

### Multi-Tenant Application Pattern

The example demonstrates the multi-tenant pattern where:
- Each tenant (institution/course) gets its own namespace
- Data isolation prevents leakage between tenants
- Platform-level analytics can still be performed across namespaces when appropriate
- Role-based access controls which namespaces users can access

## ✅ Verification Checklist

- [ ] Multiple namespaces created with proper `group_id` values
- [ ] Namespace isolation demonstrated through separate searches
- [ ] Cross-namespace analytics working when no `group_id` specified
- [ ] Multi-tenant patterns implemented correctly
- [ ] Role-based namespace access patterns understood

## 🤔 Common Questions

**Q: Can entities exist in multiple namespaces?**
A: No, each entity belongs to one namespace defined by its `group_id`. However, you can create similar entities in different namespaces.

**Q: How do I share knowledge between namespaces?**
A: Use cross-namespace searches (without `group_id`) or implement application-level data sharing patterns.

**Q: What happens if I don't specify a group_id?**
A: The entity/episode will exist in the default namespace and be accessible in global searches.

**Q: Can I change an entity's namespace after creation?**
A: This requires careful migration - typically you'd create new entities in the target namespace and migrate relationships.

## 📝 What You Learned

✅ **Multi-Tenant Isolation**: Used `group_id` to create isolated educational environments
✅ **Namespace-Constrained Search**: Searched within specific institutional contexts
✅ **Cross-Namespace Analytics**: Performed platform-level analysis across institutions
✅ **Hierarchical Organization**: Designed namespace structures for complex educational systems
✅ **Role-Based Access**: Implemented user role-based namespace access patterns

## 🎯 Next Steps

**Excellent work!** You now understand how to create scalable, privacy-preserving educational systems with proper data isolation.

**Ready to master advanced search techniques?** Continue to **[06_searching](../06_searching/)** where you'll learn Graphiti's powerful hybrid search capabilities and result optimization techniques.

**What's Coming**: Instead of basic searches, you'll learn semantic search, keyword search, reranking strategies, and search recipes tailored for educational scenarios!

---

**Key Takeaway**: Namespaces enable privacy, scalability, and organization in multi-tenant educational systems. Think of them as "institutional boundaries" that allow controlled sharing while maintaining data isolation! 🏫

*"In education, privacy and personalization must coexist. Namespacing makes both possible at scale."*