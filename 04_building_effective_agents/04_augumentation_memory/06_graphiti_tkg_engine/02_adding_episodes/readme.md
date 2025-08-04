# [Core Concept 01: Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes) - Different Types of Data

Now that you've seen Graphiti work with simple text, let's explore the three types of episodes and when to use each one. Episodes are how you feed information into Graphiti.

## 🎯 What You'll Learn

By the end of this step, you will:
- Understand the three episode types: text, message, and JSON
- Know when to use each episode type
- See how different data creates different knowledge structures
- Build a complete learning progression using episodes
- Handle bulk episode loading for large datasets

## 📚 Core Concepts

### What are Episodes?

**Episodes** are Graphiti's fundamental input unit - they represent discrete pieces of information that occurred at a specific time. Think of them as "data events" that Graphiti processes to build your temporal knowledge graph.

**Key Properties:**
- `name`: Unique identifier for the episode
- `episode_body`: The actual content (text, conversation, or JSON)
- `source`: Type of episode (`EpisodeType.text`, `EpisodeType.message`, `EpisodeType.json`)
- `source_description`: Context about where this data came from
- `reference_time`: When this episode occurred
- `group_id`: (Optional) For multi-tenant isolation

So **Episodes** are the input format for Graphiti. Think of them as "events" or "pieces of information" that happened at a specific time. Graphiti processes episodes to extract entities and relationships.

### Entities (Nodes)
**Entities** are the "things" in your knowledge graph - people, places, concepts, objects. Graphiti automatically identifies these from your episode content.

### Relationships (Edges) 
**Relationships** connect entities and show how they're related. These are also automatically extracted and can evolve over time.

### The Three Episode Types

**Text Episodes** - For narrative content:
```python
episode_body = "Sarah completed her Python assignment and got an A grade."
source = EpisodeType.text
```

**Message Episodes** - For conversations:
```python
episode_body = (
    "Student: I don't understand loops\n"
    "Tutor: Let's break them down step by step\n"
    "Student: That helps, thank you!"
)
source = EpisodeType.message
```

**JSON Episodes** - For structured data:
```python
episode_body = {
    "student": "Sarah",
    "assignment": "Python Basics",
    "score": 95,
    "completed_date": "2024-01-15"
}
source = EpisodeType.json
```

**When to Use Each:**
- **Text**: Stories, descriptions, reports, articles
- **Message**: Conversations, chats, dialogues, interviews  
- **JSON**: Database records, API responses, structured forms

## 🚀 Worked Examples (Schaum's Method)

### Example 1: Text Episodes - Educational Content

Let's build a student learning scenario step by step:

```python
# text_episodes_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def educational_text_episodes():
    """Schaum's Worked Example: Text episodes for education"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("📚 SCHAUM'S EXAMPLE 1: Text Episodes")
        print("=" * 50)
        
        await client.build_indices_and_constraints()
        
        # Step 1: Course Creation (30 days ago)
        print("\n🎓 Step 1: Creating course context...")
        await client.add_episode(
            name="course_python_intro",
            episode_body=(
                "Course PY101 'Introduction to Python Programming' was established. "
                "This beginner-friendly course teaches programming fundamentals through Python. "
                "Topics include variables, loops, functions, and data structures. "
                "The course is designed for students with no prior programming experience "
                "and emphasizes hands-on coding practice."
            ),
            source=EpisodeType.text,
            source_description="Course catalog entry",
            reference_time=datetime.now() - timedelta(days=30),
        )
        
        # Step 2: Student Enrollment (25 days ago)
        print("👤 Step 2: Student enrollment...")
        await client.add_episode(
            name="student_alice_enrollment",
            episode_body=(
                "Alice Chen, age 22, enrolled in PY101. She is a biology major "
                "interested in bioinformatics applications. Alice has strong analytical "
                "skills but no programming background. Her learning goals include "
                "understanding basic programming concepts and applying Python to "
                "biological data analysis."
            ),
            source=EpisodeType.text,
            source_description="Student enrollment system",
            reference_time=datetime.now() - timedelta(days=25),
        )
        
        # Step 3: Learning Progress (15 days ago)
        print("📈 Step 3: First assignment progress...")
        await client.add_episode(
            name="alice_first_assignment",
            episode_body=(
                "Alice completed her first Python assignment on variables and data types. "
                "She successfully created a program to calculate DNA sequence statistics. "
                "The instructor noted her excellent attention to detail and logical thinking. "
                "Alice struggled initially with string indexing but mastered it with practice. "
                "She shows promise for advanced topics."
            ),
            source=EpisodeType.text,
            source_description="Assignment evaluation",
            reference_time=datetime.now() - timedelta(days=15),
        )
        
        # Step 4: Advanced Progress (5 days ago)
        print("🚀 Step 4: Advanced topic engagement...")
        await client.add_episode(
            name="alice_loops_mastery",
            episode_body=(
                "Alice demonstrated exceptional understanding of loops in Python. "
                "She built a sophisticated DNA pattern matching algorithm using nested loops. "
                "Her code was not only functional but elegant and well-commented. "
                "Alice is now ready for advanced topics like file handling and data analysis libraries. "
                "She has become a peer mentor, helping other students with loop concepts."
            ),
            source=EpisodeType.text,
            source_description="Instructor progress notes",
            reference_time=datetime.now() - timedelta(days=5),
        )
        
        print("\n⏳ Processing episodes (LLM entity extraction)...")
        await asyncio.sleep(3)
        
        # Analyze the temporal knowledge graph
        print("\n🔍 ANALYSIS: How knowledge evolved over time")
        results = await client.search(
            query="Alice Chen Python programming learning journey",
            limit=20
        )
        
        print(f"\n📊 Knowledge Graph Results:")
        print(f"   Entities extracted: {len(results.nodes)}")
        print(f"   Relationships found: {len(results.edges)}")
        
        print(f"\n🧠 Key Learning Entities:")
        for i, node in enumerate(results.nodes[:8], 1):
            print(f"   {i}. {node.name}")
        
        print(f"\n🔗 Learning Relationships:")
        for i, edge in enumerate(results.edges[:6], 1):
            print(f"   {i}. {edge.source_node_name} → {edge.target_node_name}")
            print(f"      Type: {edge.name}")
        
        # Socratic Question: What patterns do you notice?
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • How does Alice's journey show temporal progression?")
        print(f"   • What entities represent learning concepts vs. personal attributes?")
        print(f"   • How might this knowledge help personalize future learning?")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(educational_text_episodes())
```

### Example 2: Message Episodes - Tutoring Conversations

```python
# message_episodes_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def tutoring_message_episodes():
    """Schaum's Worked Example: Message episodes for conversations"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("💬 SCHAUM'S EXAMPLE 2: Message Episodes")
        print("=" * 50)
        
        await client.build_indices_and_constraints()
        
        # Episode 1: First tutoring session (struggling with loops)
        print("\n🆘 Session 1: Student struggling with concepts...")
        await client.add_episode(
            name="alice_tutoring_session_1",
            episode_body=(
                "Tutor: Hi Alice! I see you're working on the loops assignment. What's challenging you?\n"
                "Alice: I understand what loops do conceptually, but I keep getting syntax errors.\n"
                "Tutor: That's completely normal! Let's look at your code. What type of loop are you using?\n"
                "Alice: I'm trying to use a for loop to go through DNA sequences, but it's not working.\n"
                "Tutor: Show me the exact code. The devil is in the details with Python syntax.\n"
                "Alice: for base in dna_sequence print(base) - I think I'm missing something.\n"
                "Tutor: Ah! You need a colon after the for statement. Try: for base in dna_sequence:\n"
                "Alice: Oh wow, that fixed it! Such a small thing but so important.\n"
                "Tutor: Exactly! Python is very particular about colons and indentation."
            ),
            source=EpisodeType.message,
            source_description="Online tutoring session",
            reference_time=datetime.now() - timedelta(days=10),
        )
        
        # Episode 2: Follow-up session (building confidence)
        print("📈 Session 2: Building on success...")
        await client.add_episode(
            name="alice_tutoring_session_2",
            episode_body=(
                "Alice: Hi! I got the basic loop working, but now I want to count specific DNA bases.\n"
                "Tutor: Excellent! You're thinking like a programmer now. What's your approach?\n"
                "Alice: I want to count how many times 'A', 'T', 'G', and 'C' appear in a sequence.\n"
                "Tutor: Perfect biological application! You'll need a counter for each base. Any ideas how?\n"
                "Alice: Maybe I could use variables like a_count = 0, t_count = 0?\n"
                "Tutor: Great start! Or even better, you could use a dictionary to store all counts.\n"
                "Alice: A dictionary? Like {'A': 0, 'T': 0, 'G': 0, 'C': 0}?\n"
                "Tutor: Exactly! Then you can increment the count as you loop through the sequence.\n"
                "Alice: This is so cool! I'm starting to see how programming can help with biology."
            ),
            source=EpisodeType.message,
            source_description="Follow-up tutoring session",
            reference_time=datetime.now() - timedelta(days=5),
        )
        
        # Episode 3: Advanced session (teaching others)
        print("🎓 Session 3: From learner to teacher...")
        await client.add_episode(
            name="alice_tutoring_session_3",
            episode_body=(
                "Tutor: Alice, I have a new student struggling with loops. Would you help?\n"
                "Alice: Me? But I just learned this myself!\n"
                "Tutor: That's exactly why you'd be perfect. You remember what it's like to struggle.\n"
                "Bob: Hi Alice, I heard you're really good with loops now.\n"
                "Alice: Hi Bob! I was just like you a week ago. What's confusing you?\n"
                "Bob: I don't understand why we need the colon after the for statement.\n"
                "Alice: Oh, I made that exact mistake! The colon tells Python 'here comes the loop body'.\n"
                "Bob: That makes sense! And what about indentation?\n"
                "Alice: Everything inside the loop needs to be indented. It shows what's part of the loop.\n"
                "Tutor: Alice, you're explaining this beautifully!"
            ),
            source=EpisodeType.message,
            source_description="Peer tutoring session",
            reference_time=datetime.now() - timedelta(days=2),
        )
        
        print("\n⏳ Processing conversation episodes...")
        await asyncio.sleep(3)
        
        # Analyze conversation patterns
        print("\n🎯 ANALYSIS: Tutoring conversation insights")
        conversation_results = await client.search(
            query="Alice tutoring learning progression from struggling to teaching",
            limit=15
        )
        
        print(f"\n📞 Conversation Analysis:")
        print(f"   Entities from conversations: {len(conversation_results.nodes)}")
        print(f"   Interaction patterns: {len(conversation_results.edges)}")
        
        print(f"\n👥 Conversation Entities:")
        for i, node in enumerate(conversation_results.nodes[:8], 1):
            print(f"   {i}. {node.name}")
        
        print(f"\n💡 Learning Progression Relationships:")
        for i, edge in enumerate(conversation_results.edges[:6], 1):
            print(f"   {i}. {edge.source_node_name} ↔ {edge.target_node_name}")
            print(f"      Interaction: {edge.name}")
        
        # Socratic Question: Conversation vs. Text episodes
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • How do message episodes capture different information than text?")
        print(f"   • What social learning patterns emerge from the conversations?")
        print(f"   • How could this inform AI tutoring system design?")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(tutoring_message_episodes())
```

### Example 3: JSON Episodes - Structured Assessment Data

```python
# json_episodes_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def assessment_json_episodes():
    """Schaum's Worked Example: JSON episodes for structured data"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("📊 SCHAUM'S EXAMPLE 3: JSON Episodes")
        print("=" * 50)
        
        await client.build_indices_and_constraints()
        
        # Episode 1: Initial assessment
        print("\n📝 Assessment 1: Baseline evaluation...")
        initial_assessment = {
            "assessment_id": "PY101_001",
            "student": {
                "id": "alice_chen_001",
                "name": "Alice Chen",
                "course": "PY101"
            },
            "assessment_type": "diagnostic",
            "date": "2024-01-15",
            "topics_tested": ["variables", "basic_syntax", "print_statements"],
            "questions": [
                {
                    "question_id": 1,
                    "topic": "variables",
                    "question_text": "What is a variable in Python?",
                    "student_answer": "A container that stores data values",
                    "correct": True,
                    "points": 10,
                    "time_spent_seconds": 45
                },
                {
                    "question_id": 2,
                    "topic": "basic_syntax",
                    "question_text": "How do you print 'Hello World' in Python?",
                    "student_answer": "print('Hello World')",
                    "correct": True,
                    "points": 10,
                    "time_spent_seconds": 30
                }
            ],
            "overall_score": 20,
            "max_possible_score": 20,
            "percentage": 100,
            "strengths": ["clear understanding of basic concepts", "good syntax knowledge"],
            "areas_for_improvement": ["needs exposure to more advanced topics"],
            "instructor_notes": "Strong foundation, ready for loops and functions"
        }
        
        await client.add_episode(
            name="alice_initial_assessment",
            episode_body=initial_assessment,
            source=EpisodeType.json,
            source_description="Diagnostic assessment system",
            reference_time=datetime.now() - timedelta(days=20),
        )
        
        # Episode 2: Mid-course assessment  
        print("📈 Assessment 2: Mid-course evaluation...")
        mid_assessment = {
            "assessment_id": "PY101_002",
            "student": {
                "id": "alice_chen_001", 
                "name": "Alice Chen",
                "course": "PY101"
            },
            "assessment_type": "formative",
            "date": "2024-02-01",
            "topics_tested": ["loops", "conditionals", "functions"],
            "questions": [
                {
                    "question_id": 3,
                    "topic": "loops",
                    "question_text": "Write a for loop to count DNA bases",
                    "student_answer": "for base in sequence:\n    if base == 'A':\n        count += 1",
                    "correct": True,
                    "points": 15,
                    "time_spent_seconds": 180,
                    "code_quality": "excellent"
                },
                {
                    "question_id": 4,
                    "topic": "functions",
                    "question_text": "Create a function to calculate GC content",
                    "student_answer": "def gc_content(dna):\n    gc = dna.count('G') + dna.count('C')\n    return gc / len(dna) * 100",
                    "correct": True,
                    "points": 20,
                    "time_spent_seconds": 300,
                    "code_quality": "exceptional",
                    "creativity_bonus": 5
                }
            ],
            "overall_score": 40,
            "max_possible_score": 35,
            "percentage": 114,  # Including bonus points
            "strengths": ["excellent loop mastery", "creative problem solving", "clean code"],
            "areas_for_improvement": ["could explore more advanced data structures"],
            "instructor_notes": "Exceptional progress, ready for advanced topics",
            "peer_tutoring_recommendation": True
        }
        
        await client.add_episode(
            name="alice_mid_assessment",
            episode_body=mid_assessment,
            source=EpisodeType.json,
            source_description="Formative assessment system",
            reference_time=datetime.now() - timedelta(days=10),
        )
        
        # Episode 3: Final project assessment
        print("🎓 Assessment 3: Final project evaluation...")
        final_project = {
            "project_id": "PY101_FINAL_001",
            "student": {
                "id": "alice_chen_001",
                "name": "Alice Chen", 
                "course": "PY101"
            },
            "project_type": "capstone",
            "title": "DNA Sequence Analysis Tool",
            "date": "2024-02-15",
            "requirements_met": {
                "file_handling": True,
                "data_structures": True,
                "functions": True,
                "error_handling": True,
                "documentation": True,
                "user_interface": True
            },
            "features_implemented": [
                "FASTA file parsing",
                "Multiple sequence analysis",
                "GC content calculation",
                "Open reading frame detection",
                "Results export to CSV"
            ],
            "code_metrics": {
                "lines_of_code": 245,
                "functions_created": 8,
                "test_coverage": 95,
                "documentation_percentage": 100
            },
            "evaluation_criteria": {
                "functionality": {"score": 95, "max": 100},
                "code_quality": {"score": 98, "max": 100},
                "creativity": {"score": 92, "max": 100},
                "documentation": {"score": 100, "max": 100},
                "presentation": {"score": 88, "max": 100}
            },
            "overall_grade": "A+",
            "instructor_feedback": "Exceptional work demonstrating mastery of all course concepts and creative application to biology",
            "future_recommendations": ["Advanced Python programming", "Bioinformatics specialization", "Research opportunities"]
        }
        
        await client.add_episode(
            name="alice_final_project",
            episode_body=final_project,
            source=EpisodeType.json,
            source_description="Final project evaluation system",
            reference_time=datetime.now() - timedelta(days=2),
        )
        
        print("\n⏳ Processing structured assessment data...")
        await asyncio.sleep(4)  # JSON episodes may take longer to process
        
        # Analyze assessment progression
        print("\n📊 ANALYSIS: Assessment data insights")
        assessment_results = await client.search(
            query="Alice Chen assessment scores progression learning mastery",
            limit=20
        )
        
        print(f"\n📈 Assessment Analysis:")
        print(f"   Assessment entities: {len(assessment_results.nodes)}")
        print(f"   Performance relationships: {len(assessment_results.edges)}")
        
        print(f"\n🎯 Performance Entities:")
        for i, node in enumerate(assessment_results.nodes[:10], 1):
            print(f"   {i}. {node.name}")
        
        print(f"\n📊 Assessment Relationships:")
        for i, edge in enumerate(assessment_results.edges[:8], 1):
            print(f"   {i}. {edge.source_node_name} → {edge.target_node_name}")
            print(f"      Assessment aspect: {edge.name}")
        
        # Socratic Question: Structured vs. Unstructured data
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • How does JSON capture different insights than text/messages?")
        print(f"   • What quantitative patterns emerge from structured assessments?")
        print(f"   • How could this data drive adaptive learning algorithms?")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(assessment_json_episodes())
```

## 🧪 Practice Exercises

### Exercise 1: Choose the Right Episode Type

For each scenario, pick the best episode type and explain why:

1. **Student course enrollment form** → `?`
2. **Live tutoring session transcript** → `?`  
3. **Quiz results from LMS API** → `?`
4. **Student reflection essay** → `?`
5. **Chatbot conversation log** → `?`

**Answers:**
1. **JSON** - Structured form data with specific fields
2. **Message** - Back-and-forth conversation format
3. **JSON** - Structured data from an API  
4. **Text** - Narrative writing, personal reflection
5. **Message** - Dialogue between user and bot

### Exercise 2: Build a Learning Story

Create 3 episodes showing a student's progress over time:

```python
# Week 1 - Starting out (Text episode)
await client.add_episode(
    name="alice_week1",
    episode_body="Alice enrolled in Python 101. She has no programming experience but is eager to learn.",
    source=EpisodeType.text,
    reference_time=datetime.now() - timedelta(days=14)
)

# Week 2 - Getting help (Message episode)  
await client.add_episode(
    name="alice_week2",
    episode_body=(
        "Alice: I'm confused about variables\n"
        "Tutor: Think of variables as labeled boxes that store information\n"
        "Alice: Oh, that makes sense! Like a box labeled 'age' contains the number 25"
    ),
    source=EpisodeType.message,
    reference_time=datetime.now() - timedelta(days=7)
)

# Week 3 - Assessment results (JSON episode)
await client.add_episode(
    name="alice_week3",
    episode_body={
        "student": "Alice",
        "assessment": "Python Basics Quiz",
        "score": 85,
        "topics": ["variables", "loops", "functions"],
        "time_spent_minutes": 45
    },
    source=EpisodeType.json,
    reference_time=datetime.now()
)
```

### Problem 2: Temporal Progression Design
**Challenge**: Design a series of episodes showing a student's journey from beginner to expert in "Python Functions."

**Your Task**: Create 4 episodes spanning 3 weeks showing progression:
1. Initial confusion episode (text)
2. Tutoring breakthrough (message)  
3. First successful implementation (json assessment)
4. Teaching others (message)

### Problem 3: Bulk Episode Loading
**Scenario**: You have 1,000 student assessment records to load.

```python
# Your task: Complete this bulk loading implementation
async def load_assessment_data():
    assessments = load_from_database()  # Returns 1000 records
    
    # TODO: Convert to RawEpisode objects
    # TODO: Use add_episode_bulk for efficient loading
    # TODO: Include proper error handling
    
    pass
```

## 🔧 Advanced Techniques

### Bulk Episode Loading for Performance

When loading large datasets, use `add_episode_bulk`:

```python
from graphiti_core.nodes import RawEpisode
import json

async def efficient_bulk_loading():
    """Load 100s or 1000s of episodes efficiently"""
    
    # Prepare episodes
    raw_episodes = []
    for assessment in assessment_records:
        raw_episodes.append(RawEpisode(
            name=f"assessment_{assessment['id']}",
            content=json.dumps(assessment),
            source=EpisodeType.json,
            source_description="LMS assessment export",
            reference_time=datetime.fromisoformat(assessment['completed_at'])
        ))
    
    # Bulk load (much faster than individual add_episode calls)
    await client.add_episode_bulk(raw_episodes)
```

**Performance Benefits**:
- 10-100x faster for large datasets
- Optimized LLM batching
- Reduced API calls and database transactions

## ✅ Understanding Check (Socratic Method)

Before proceeding, reflect on these questions:

### Essential Questions
1. **Why** does Graphiti need three different episode types?
2. **When** would you choose JSON over text episodes?
3. **How** does the temporal aspect (`reference_time`) enable learning insights?
4. **What** happens if you put conversation data in a text episode?

### Critical Thinking
1. **If** a student's understanding changes over time, how do episodes capture this evolution?
2. **What if** you have partially structured data (like a form with free-text fields)?
3. **How might** bulk loading affect the temporal ordering of knowledge extraction?

### Application Scenarios
1. Design episodes for a customer support knowledge base
2. Plan episode structure for a research paper analysis system  
3. Create episodes that track project collaboration over time

## 🐛 Common Issues & Solutions

### Issue 1: "Episode too large for LLM context"
**Problem**: Your JSON episode exceeds the LLM's context window
**Solution**: Break large JSON into smaller, focused episodes
```python
# Instead of one massive episode:
huge_assessment = {...}  # 10,000+ characters

# Create focused episodes:
await client.add_episode(name="student_profile", episode_body=assessment["student_info"], ...)
await client.add_episode(name="question_responses", episode_body=assessment["responses"], ...)
await client.add_episode(name="performance_metrics", episode_body=assessment["scores"], ...)
```

### Issue 2: "Message format not recognized"
**Problem**: Conversation episodes not extracting dialogue properly
**Solution**: Use proper `{role}: {message}` format
```python
# Correct format:
episode_body = (
    "Student: I don't understand loops.\n"
    "Tutor: Let's break it down step by step.\n" 
    "Student: That helps, thank you!"
)

# Incorrect format:
episode_body = "Student said they don't understand loops. Tutor explained step by step."
```

### Issue 3: "No entities extracted"
**Problem**: Episodes added but no graph entities created
**Solutions**:
1. **Check LLM configuration**: Verify OpenAI API key
2. **Wait for processing**: Allow time for async entity extraction
3. **Content quality**: Ensure episodes have meaningful, extractable content

## 📝 What You Learned

Congratulations! You now understand how to use different episode types effectively:

### **Key Skills Gained**
✅ **Episode Type Selection**: Choose the right format for your data
✅ **Temporal Knowledge Building**: Use reference_time to show progression over time
✅ **Bulk Loading**: Handle large datasets efficiently with `add_episode_bulk`
✅ **Real-World Application**: Apply episodes to educational scenarios

### **When to Use Each Type**
- **Text Episodes**: For stories, descriptions, reports, and narrative content
- **Message Episodes**: For conversations, dialogues, and interactive content
- **JSON Episodes**: For structured data, API responses, and database records

## 🎯 Next Steps

**Ready to make your knowledge graphs even more powerful?** Continue to **[03_custom_types](../03_custom_types/)** where you'll learn to define custom entities and relationships specific to your domain.

**What's Coming**: Instead of generic "entities" and "relationships", you'll create specific types like `Student`, `Course`, `ENROLLED_IN`, and `COMPLETED` that make your knowledge graphs much more precise and useful.

## 📚 Key Takeaways

1. **Different data needs different episode types** - Choose based on structure
2. **Time matters** - Use reference_time to build temporal knowledge
3. **Episode quality affects graph quality** - Well-structured input creates better knowledge
4. **Bulk operations scale better** - Use `add_episode_bulk` for large datasets
5. **Mix and match** - Combine different episode types for comprehensive knowledge

---

**Practice makes perfect!** Try creating episodes from your own data before moving to the next step. The more you practice, the better you'll understand when to use each type. 🚀

*"The best way to learn episodes is to experiment with your own data and see how different types create different knowledge structures."*