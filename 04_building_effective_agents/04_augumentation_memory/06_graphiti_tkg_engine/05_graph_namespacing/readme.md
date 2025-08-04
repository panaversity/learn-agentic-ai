# [Core Concept 04: Graph Namespacing](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) - Multi-Tenant Educational Systems

Welcome to Step 05! This step applies **Socratic Method** and **evidence-based learning** to master graph namespacing with `group_id`.

## 🎯 Learning Objectives

By the end of this step, you will:
- Understand multi-tenancy in educational knowledge graphs
- Implement isolated learning environments with `group_id`
- Design scalable multi-institution systems
- Handle cross-namespace queries and analytics
- Apply namespacing to TutorsGPT scenarios

## 📚 Core Concepts (Building on Communities)

### What is Graph Namespacing?

**Graph Namespacing** creates isolated "worlds" within a single Graphiti instance using `group_id` parameters. Think of it as creating separate classroom environments where each group's knowledge remains private and organized.

**Educational Use Cases:**
- **Multi-Institution Platform**: Different schools using the same TutorsGPT system
- **Course Isolation**: Separate CS101 from MATH201 knowledge graphs
- **Semester Separation**: Fall 2024 vs Spring 2025 student cohorts
- **Privacy Boundaries**: Student data isolation for FERPA compliance
- **Research Studies**: Controlled learning environment experiments

### How Namespacing Works

Every node and edge in Graphiti can have a `group_id`:
```python
await client.add_episode(
    name="student_progress",
    episode_body="Alice completed her Python assignment...",
    source=EpisodeType.text,
    group_id="university_a_cs101_fall2024"  # Isolated namespace
)
```

**Isolation Benefits:**
- **Data Privacy**: Student information stays within their institution
- **Query Scope**: Searches limited to relevant educational context
- **Analytics Precision**: Metrics specific to course/cohort/institution
- **Scalability**: Single system serves multiple educational entities

## 🚀 Worked Examples (Schaum's Method)

### Example 1: Multi-Institution TutorsGPT System

```python
# multi_institution_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def multi_institution_tutorsgpt():
    """Schaum's Worked Example: Multi-institution educational platform"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("🏫 SCHAUM'S EXAMPLE: Multi-Institution TutorsGPT")
        print("=" * 60)
        
        await client.build_indices_and_constraints()
        
        # Define institutional namespaces
        institutions = {
            "stanford_cs": "stanford_university_computer_science",
            "mit_eecs": "mit_electrical_engineering_computer_science", 
            "berkeley_cs": "uc_berkeley_computer_science"
        }
        
        # Phase 1: Create isolated institutional knowledge
        print("\n🏛️ Phase 1: Creating isolated institutional environments...")
        
        # Stanford CS101 Course
        print("\n📚 Stanford CS101 Knowledge Base...")
        stanford_episodes = [
            {
                "name": "stanford_cs101_intro",
                "body": "Stanford CS101 emphasizes theoretical foundations with practical Python applications. The course uses problem-based learning and covers algorithmic thinking, data structures, and software engineering principles.",
                "group_id": institutions["stanford_cs"] + "_cs101"
            },
            {
                "name": "stanford_student_alice",
                "body": "Alice Johnson at Stanford is a sophomore majoring in Computer Science. She excels in mathematical reasoning and prefers structured learning approaches. Alice is working on machine learning applications.",
                "group_id": institutions["stanford_cs"] + "_cs101"
            },
            {
                "name": "stanford_professor_smith",
                "body": "Professor David Smith teaches CS101 at Stanford. He has 15 years of experience and specializes in algorithms and computational complexity. His teaching style emphasizes rigorous mathematical proofs.",
                "group_id": institutions["stanford_cs"] + "_cs101"
            }
        ]
        
        # MIT EECS Course
        print("🔬 MIT EECS Knowledge Base...")
        mit_episodes = [
            {
                "name": "mit_6001_intro",
                "body": "MIT 6.001 Structure and Interpretation of Computer Programs focuses on programming paradigms and computational thinking. The course emphasizes functional programming, recursion, and program design methodologies.",
                "group_id": institutions["mit_eecs"] + "_6001"
            },
            {
                "name": "mit_student_bob",
                "body": "Bob Chen at MIT is a first-year student in EECS. He has strong programming background but struggles with theoretical concepts. Bob prefers hands-on experimentation and collaborative learning.",
                "group_id": institutions["mit_eecs"] + "_6001"
            },
            {
                "name": "mit_professor_garcia",
                "body": "Professor Maria Garcia teaches 6.001 at MIT. She has expertise in programming languages and software systems. Her teaching approach combines theoretical depth with practical programming projects.",
                "group_id": institutions["mit_eecs"] + "_6001"
            }
        ]
        
        # UC Berkeley CS Course
        print("🐻 UC Berkeley CS Knowledge Base...")
        berkeley_episodes = [
            {
                "name": "berkeley_cs61a_intro",
                "body": "UC Berkeley CS61A teaches programming paradigms through Python, Scheme, and SQL. The course emphasizes abstraction, recursion, and higher-order functions with a project-based approach.",
                "group_id": institutions["berkeley_cs"] + "_cs61a"
            },
            {
                "name": "berkeley_student_carol",
                "body": "Carol Martinez at UC Berkeley is studying CS61A. She has diverse academic interests and excels in creative problem-solving. Carol benefits from visual learning aids and peer collaboration.",
                "group_id": institutions["berkeley_cs"] + "_cs61a"
            },
            {
                "name": "berkeley_ta_wilson",
                "body": "Teaching Assistant James Wilson supports CS61A at Berkeley. He's a graduate student specializing in educational technology. James focuses on helping students with debugging and conceptual understanding.",
                "group_id": institutions["berkeley_cs"] + "_cs61a"
            }
        ]
        
        # Add all episodes with appropriate namespacing
        all_episodes = stanford_episodes + mit_episodes + berkeley_episodes
        
        for episode in all_episodes:
            await client.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description="Multi-institution knowledge base",
                reference_time=datetime.now() - timedelta(days=30),
                group_id=episode["group_id"]
            )
            institution = episode["group_id"].split("_")[0]
            print(f"   ✅ {institution.upper()}: {episode['name']}")
        
        print(f"\n⏳ Processing {len(all_episodes)} namespaced episodes...")
        await asyncio.sleep(5)
        
        # Phase 2: Demonstrate namespace isolation
        print("\n🔒 Phase 2: Demonstrating namespace isolation...")
        
        # Search within Stanford namespace only
        stanford_search = await client.search(
            query="computer science programming student professor course",
            group_id=institutions["stanford_cs"] + "_cs101",
            limit=10
        )
        
        print(f"\n🏛️ Stanford CS101 Namespace Search:")
        print(f"   Entities found: {len(stanford_search.nodes)}")
        print(f"   Relationships: {len(stanford_search.edges)}")
        print(f"   Stanford-specific entities:")
        for node in stanford_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Search within MIT namespace only
        mit_search = await client.search(
            query="computer science programming student professor course",
            group_id=institutions["mit_eecs"] + "_6001",
            limit=10
        )
        
        print(f"\n🔬 MIT EECS Namespace Search:")
        print(f"   Entities found: {len(mit_search.nodes)}")
        print(f"   Relationships: {len(mit_search.edges)}")
        print(f"   MIT-specific entities:")
        for node in mit_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Search within Berkeley namespace only
        berkeley_search = await client.search(
            query="computer science programming student professor course",
            group_id=institutions["berkeley_cs"] + "_cs61a",
            limit=10
        )
        
        print(f"\n🐻 UC Berkeley CS61A Namespace Search:")
        print(f"   Entities found: {len(berkeley_search.nodes)}")
        print(f"   Relationships: {len(berkeley_search.edges)}")
        print(f"   Berkeley-specific entities:")
        for node in berkeley_search.nodes[:4]:
            print(f"     • {node.name}")
        
        # Phase 3: Cross-namespace analytics (when appropriate)
        print("\n📊 Phase 3: Cross-namespace analytics...")
        
        # Global search across all namespaces (for platform-level insights)
        global_search = await client.search(
            query="teaching methodology programming education approaches",
            limit=15  # No group_id = search all namespaces
        )
        
        print(f"\n🌍 Cross-Institution Analysis:")
        print(f"   Total entities: {len(global_search.nodes)}")
        print(f"   Total relationships: {len(global_search.edges)}")
        print(f"   Teaching methodology entities found:")
        teaching_entities = [n for n in global_search.nodes if 'teach' in n.name.lower() or 'professor' in n.name.lower()]
        for entity in teaching_entities[:4]:
            print(f"     • {entity.name}")
        
        # Phase 4: Namespace-specific communities
        print("\n🏘️ Phase 4: Namespace-specific community analysis...")
        
        # Build communities within Stanford namespace
        stanford_communities = await client.build_communities(
            group_id=institutions["stanford_cs"] + "_cs101"
        )
        
        print(f"\n🏛️ Stanford CS101 Communities:")
        print(f"   Communities detected: {len(stanford_communities)}")
        if stanford_communities:
            print(f"   Sample community: {stanford_communities[0].summary[:150]}...")
        
        # Socratic Questions for Deep Learning
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • Why is data isolation crucial in educational platforms?")
        print(f"   • How does namespacing enable personalized learning at scale?")
        print(f"   • When would you want cross-namespace vs. isolated queries?")
        print(f"   • What privacy and compliance benefits does namespacing provide?")
        print(f"   • How might namespace design affect system performance?")
        
        print(f"\n💡 NAMESPACING INSIGHTS:")
        print(f"   • Institutional knowledge remains properly isolated")
        print(f"   • Each namespace develops its own knowledge communities")
        print(f"   • Cross-namespace analysis reveals educational patterns")
        print(f"   • Privacy compliance achieved through data separation")
        print(f"   • Scalable architecture supports unlimited institutions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting namespacing:")
        print("   1. Verify group_id parameters are correctly specified")
        print("   2. Check that searches include appropriate group_id constraints")
        print("   3. Ensure namespace naming follows consistent conventions")
        
    finally:
        await client.close()
        print("\n🔒 Multi-institution demo completed")

if __name__ == "__main__":
    asyncio.run(multi_institution_tutorsgpt())
```

### Example 2: Semester-Based Learning Analytics

```python
# semester_analytics_demo.py
import asyncio
from datetime import datetime, timedelta

async def semester_learning_analytics():
    """Advanced example: Semester-based learning analytics with namespacing"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("📊 SEMESTER-BASED LEARNING ANALYTICS")
        print("=" * 50)
        
        # Define semester namespaces
        semesters = [
            "university_cs101_fall2023",
            "university_cs101_spring2024", 
            "university_cs101_fall2024"
        ]
        
        # Simulate semester progression data
        for semester in semesters:
            print(f"\n📅 Analyzing {semester}...")
            
            # Search within semester namespace
            semester_data = await client.search(
                query="student learning outcomes performance assessment",
                group_id=semester,
                limit=20
            )
            
            print(f"   Students: {len([n for n in semester_data.nodes if 'student' in n.name.lower()])}")
            print(f"   Assessments: {len([n for n in semester_data.nodes if 'assessment' in n.name.lower() or 'quiz' in n.name.lower()])}")
            print(f"   Learning relationships: {len(semester_data.edges)}")
            
            # Analyze learning progression within semester
            progression_relationships = [
                e for e in semester_data.edges 
                if 'progress' in e.name.lower() or 'improve' in e.name.lower()
            ]
            print(f"   Learning progressions: {len(progression_relationships)}")
        
        # Cross-semester comparison (aggregated analytics)
        print(f"\n📈 Cross-Semester Trends:")
        
        all_semesters_data = await client.search(
            query="learning outcomes trends semester comparison",
            limit=50  # No group_id = cross-namespace search
        )
        
        print(f"   Total learning entities: {len(all_semesters_data.nodes)}")
        print(f"   Total learning relationships: {len(all_semesters_data.edges)}")
        
        # Identify semester-specific vs. universal learning patterns
        semester_specific = []
        universal_patterns = []
        
        for node in all_semesters_data.nodes:
            # This would require additional metadata to determine namespace membership
            # In practice, you'd track which nodes appear across multiple semesters
            pass
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(semester_learning_analytics())
```

## 📚 Practice Problems (Zone of Proximal Development)

### Problem 1: Namespace Design Strategy
**Scenario**: You're designing a TutorsGPT system for a university consortium.

**Your Task**: Design namespace hierarchies for:
1. 5 universities, each with multiple departments
2. Department-level courses with semester isolation
3. Research projects that span institutions
4. Student privacy while enabling collaborative learning

### Problem 2: Migration Between Namespaces
**Challenge**: A student transfers from one institution to another.

**Your Task**:
1. Design a strategy to migrate student learning history
2. Consider what knowledge should transfer vs. remain isolated
3. Plan privacy implications and consent requirements

### Problem 3: Cross-Namespace Analytics
**Scenario**: Researchers want to study learning patterns across institutions.

**Your Task**:
1. Design an analytics framework that preserves privacy
2. Plan aggregation strategies that prevent individual identification
3. Consider what insights can be shared vs. kept isolated

## 🔧 Advanced Techniques

### Hierarchical Namespacing

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
        """Generate full hierarchical namespace"""
        return f"{self.institution}_{self.department}_{self.course}_{self.semester}"
    
    @property
    def course_namespace(self) -> str:
        """Course-level namespace (across semesters)"""
        return f"{self.institution}_{self.department}_{self.course}"
    
    @property
    def department_namespace(self) -> str:
        """Department-level namespace"""
        return f"{self.institution}_{self.department}"
    
    def get_peer_namespaces(self) -> List[str]:
        """Get namespaces for peer courses in same department"""
        # Would query for other courses in same department
        pass

# Usage
stanford_cs101 = NamespaceManager("stanford", "cs", "cs101", "fall2024")
print(stanford_cs101.full_namespace)  # "stanford_cs_cs101_fall2024"
```

### Namespace-Aware Search Strategies

```python
async def intelligent_namespace_search(query: str, user_context: dict):
    """Intelligently search across appropriate namespaces"""
    
    primary_namespace = user_context.get("primary_namespace")
    user_role = user_context.get("role")  # student, instructor, admin
    
    if user_role == "student":
        # Students search within their course namespace
        return await client.search(
            query=query,
            group_id=primary_namespace,
            limit=10
        )
    
    elif user_role == "instructor":
        # Instructors can search across their courses
        course_namespaces = user_context.get("course_namespaces", [])
        all_results = []
        for namespace in course_namespaces:
            results = await client.search(
                query=query,
                group_id=namespace,
                limit=5
            )
            all_results.extend(results.nodes)
        return all_results
    
    elif user_role == "admin":
        # Admins can search across institution
        return await client.search(
            query=query,
            # No group_id restriction for admins
            limit=20
        )
```

### Privacy-Preserving Analytics

```python
async def privacy_preserving_analytics():
    """Perform analytics while preserving namespace privacy"""
    
    # Aggregate statistics without exposing individual data
    namespace_stats = {}
    
    for namespace in get_all_namespaces():
        # Get aggregate metrics without exposing individual records
        namespace_data = await client.search(
            query="learning outcomes assessment performance",
            group_id=namespace,
            limit=100
        )
        
        # Compute aggregated, anonymized statistics
        namespace_stats[namespace] = {
            "total_entities": len(namespace_data.nodes),
            "total_relationships": len(namespace_data.edges),
            "entity_types": count_entity_types(namespace_data.nodes),
            # No individual student data exposed
        }
    
    return namespace_stats
```

## ✅ Understanding Check (Socratic Method)

### Essential Questions
1. **Why** is data isolation crucial in educational technology?
2. **When** would you search within vs. across namespaces?
3. **How** does namespacing enable scalable multi-tenancy?
4. **What** are the privacy implications of namespace design?

### Critical Thinking
1. **If** you need to share insights across institutions, how do you preserve privacy?
2. **What if** a student needs access to resources from multiple courses?
3. **How might** namespace granularity affect system performance and usability?

### Design Challenges
1. Design namespaces for a K-12 school district with multiple schools
2. Plan namespace migration for university mergers
3. Create a research collaboration framework that spans institutions

## 🐛 Common Issues & Solutions

### Issue 1: "Overly granular namespaces"
**Problem**: Too many small namespaces reduce knowledge sharing
**Solution**: Balance isolation needs with knowledge connectivity; use hierarchical namespaces

### Issue 2: "Cross-namespace query complexity"
**Problem**: Managing queries across multiple namespaces becomes complex
**Solution**: Implement namespace-aware search abstractions and user role-based access

### Issue 3: "Namespace migration challenges"
**Problem**: Moving data between namespaces breaks relationships
**Solution**: Plan migration carefully with relationship mapping and data validation

## 🎯 Next Steps

You now understand how to create scalable, privacy-preserving educational systems! You've learned:

✅ **Multi-tenant isolation** with `group_id` namespacing  
✅ **Institutional privacy** and compliance strategies  
✅ **Scalable architecture** for educational platforms  
✅ **Analytics frameworks** that preserve privacy  

**Ready for the next step?** Continue to **[06_searching](../06_searching/)** to master Graphiti's powerful hybrid search capabilities and advanced retrieval techniques.

## 📝 Key Takeaways

1. **Namespaces enable scale** - Single system, multiple isolated environments
2. **Privacy through isolation** - Institutional and student data protection  
3. **Flexible analytics** - Namespace-specific vs. cross-namespace insights
4. **Hierarchical organization** - Institution → Department → Course → Semester
5. **Role-based access** - Different search scopes for different user types

---

**Master's Tip**: Think of namespaces as "institutional boundaries" in your knowledge graph. They enable privacy, scalability, and organization while still allowing controlled cross-institutional insights when appropriate. 🏫

*"In education, privacy and personalization must coexist. Namespacing makes both possible at scale."* - Educational Technology Architecture Principles