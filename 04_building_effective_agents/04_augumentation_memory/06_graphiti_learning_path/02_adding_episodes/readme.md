# Step 02: Adding Episodes - The Three Data Types

Now that you've created your first Graphiti program, let's master episodes - the foundation of how Graphiti ingests and processes information.

## 📚 Official Documentation

- [Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes) - Complete guide to episode types
- [Episode Types](https://help.getzep.com/graphiti/core-concepts/episodes) - Detailed episode concepts
- [Temporal Data](https://help.getzep.com/graphiti/core-concepts/temporal-data) - Time-aware knowledge graphs

## 🎯 What You'll Learn

By the end of this step, you will:
- Master the three episode types: `text`, `message`, and `json`
- Understand exactly when to use each type for different educational scenarios
- Handle bulk episode loading for performance
- See how episodes become searchable knowledge through LLM processing

## 📋 Prerequisites

- Completed Step 01 (Hello World)
- Graphiti client working with basic search
- Understanding of async Python programming

## 📚 What are Episodes?

### The Core Concept

**Episodes** are the primary way Graphiti ingests information. Think of an episode as a single "event" or "piece of information" that happened at a specific time.

**Key Properties:**
- **Episodes are nodes themselves** - they become part of your knowledge graph
- **Temporal tracking** - every episode has a `reference_time` 
- **Provenance** - you can trace where any extracted knowledge came from
- **LLM processing** - episodes are analyzed to extract entities and relationships

### How Episodes Work

1. **You add an episode** → Raw information goes into Graphiti
2. **LLM processes the episode** → Extracts entities (people, concepts, things) and relationships
3. **Knowledge graph grows** → New nodes and edges are created
4. **Everything stays connected** → Extracted entities link back to the original episode via `MENTIONS` edges

### The Three Episode Types

Graphiti supports three episode types, each optimized for different data structures:

## 📝 **Text Episodes** - For Narrative Content

**Use for:** Stories, descriptions, reports, articles, learning content, student reflections

**Best for:** Unstructured narrative content that needs entity extraction

```python
await graphiti.add_episode(
    name="student_background",
    episode_body=(
        "Alice Chen is a 22-year-old biology student who enrolled in Python 101. "
        "She has excellent analytical skills from her science background but has "
        "never programmed before. Alice wants to learn Python to analyze DNA "
        "sequences and biological data for her research."
    ),
    source=EpisodeType.text,
    source_description="Student enrollment system",
    reference_time=datetime.now()
)
```

**What Graphiti extracts:**
- Entities: `Alice Chen`, `Python 101`, `biology`, `DNA sequences`
- Relationships: `Alice ENROLLED_IN Python 101`, `Alice STUDIES biology`
- Temporal context: When this information was recorded

## 💬 **Message Episodes** - For Conversations

**Use for:** Dialogues, chats, tutoring sessions, interviews, Q&A sessions

**Format requirement:** Use `Speaker: Message` pattern - this is crucial!

```python
await graphiti.add_episode(
    name="tutoring_session",
    episode_body=(
        "Student: I don't understand Python loops\n"
        "Tutor: Let's start with a simple example. What do you want to repeat?\n"
        "Student: I want to count DNA bases in a sequence\n"
        "Tutor: Perfect! A for loop is ideal for that task\n"
        "Student: Can you show me the syntax?\n"
        "Tutor: Sure! for base in dna_sequence:"
    ),
    source=EpisodeType.message,
    source_description="Online tutoring platform",
    reference_time=datetime.now()
)
```

**What Graphiti extracts:**
- Participants: `Student`, `Tutor` 
- Topics discussed: `Python loops`, `DNA bases`, `for loop syntax`
- Learning progression: Student confusion → tutor guidance → understanding
- Conversation flow and educational interactions

## 📊 **JSON Episodes** - For Structured Data

**Use for:** Database records, API responses, assessment results, structured system data

**Best for:** When you already have structured data and want precise control

```python
assessment_data = {
    "student_id": "alice_chen_001",
    "student_name": "Alice Chen",
    "course": "Python 101",
    "assessment_type": "loops_quiz",
    "date": "2024-01-15",
    "score": 88,
    "max_score": 100,
    "time_spent_minutes": 35,
    "questions_correct": 7,
    "questions_total": 8,
    "topics_tested": ["for_loops", "while_loops", "nested_loops"],
    "strengths": ["basic_loop_syntax", "iteration_logic"],
    "needs_improvement": ["nested_loop_complexity"],
    "instructor_notes": "Great progress! Ready for functions next."
}

await graphiti.add_episode(
    name="alice_loops_assessment",
    episode_body=assessment_data,
    source=EpisodeType.json,
    source_description="Learning management system",
    reference_time=datetime.now()
)
```

**What Graphiti extracts:**
- Structured relationships: `Alice SCORED 88 ON loops_quiz`
- Performance metrics: scores, timing, topic mastery
- Learning insights: strengths and improvement areas
- Temporal progression: assessment timeline

## 🚀 Complete Working Example

Let's build a comprehensive educational scenario using all three episode types:

### episodes_demo.py

[The existing episodes_demo.py file content remains the same - it's already well-structured]

## ▶️ Running the Example

1. **Save the code** as `episodes_demo.py`
2. **Make sure your environment** from Step 01 is working
3. **Run the program**:

```bash
uv run python episodes_demo.py
```

## 📊 Expected Output

```
🚀 Starting Episode Types Demo...

📝 Adding text episode (student background)...
💬 Adding message episode (tutoring session)...
📊 Adding JSON episode (assessment data)...
✅ All episodes added successfully!

🔍 Searching across all episode types...
📊 Found 8 results:
  1. Alice Chen enrolled in Python 101 course
  2. Alice Chen is biology student with analytical skills
  3. Student struggled with for loop syntax errors
  4. Tutor helped student fix missing colon syntax
  5. Alice scored 88% on loops assessment quiz
  6. Alice shows strength in basic loop syntax
  7. Alice needs improvement with nested loops
  8. Instructor notes Alice ready for functions

🎯 Searching for tutoring interactions...
Tutoring insights: 4 results
  • Student asked about for loop confusion
  • Tutor provided syntax guidance and examples
  • Student learned missing colon was the issue
  • Educational dialogue shows learning progression

🎓 Episode types demo completed!
```

## 🧪 Try It Yourself

### Exercise 1: Add More Episode Types

Create episodes for different educational scenarios:

```python
# Research project discussion (text episode)
await graphiti.add_episode(
    name="research_project_discussion",
    episode_body=(
        "The Advanced Biology Research Project requires students to analyze "
        "real genomic data using Python. Teams of 2-3 students will choose "
        "from datasets on cancer genetics, evolutionary biology, or "
        "microbial genomics. The project spans 8 weeks and includes "
        "data preprocessing, statistical analysis, and visualization."
    ),
    source=EpisodeType.text,
    reference_time=datetime.now()
)

# Study group conversation (message episode)
await graphiti.add_episode(
    name="study_group_session",
    episode_body=(
        "Alice: I'm working on the genomic analysis project\n"
        "Bob: Which dataset did you choose?\n"
        "Alice: Cancer genetics - it's challenging but fascinating\n"
        "Carol: I can help with the statistical analysis part\n"
        "Alice: That would be amazing! I'm struggling with p-values\n"
        "Bob: Let's meet tomorrow to work through it together"
    ),
    source=EpisodeType.message,
    reference_time=datetime.now()
)

# Assignment submission data (JSON episode)
submission_data = {
    "assignment_id": "genomic_analysis_001",
    "student_id": "alice_chen_001",
    "submission_date": "2024-02-15",
    "files_submitted": ["analysis.py", "visualization.ipynb", "report.pdf"],
    "dataset_used": "cancer_genetics_tcga",
    "code_quality_score": 92,
    "analysis_accuracy": 87,
    "collaboration_partners": ["bob_martinez", "carol_zhang"],
    "instructor_feedback": "Excellent statistical approach, visualization needs improvement"
}

await graphiti.add_episode(
    name="alice_project_submission",
    episode_body=submission_data,
    source=EpisodeType.json,
    reference_time=datetime.now()
)
```

### Exercise 2: Understanding Episode Processing

Add episodes and then search to see what was extracted:

```python
# Add an episode
await graphiti.add_episode(
    name="debugging_session",
    episode_body="Alice spent 45 minutes debugging a Python function that calculates GC content in DNA sequences. The issue was an off-by-one error in the loop indexing.",
    source=EpisodeType.text,
    reference_time=datetime.now()
)

# Search to see what was extracted
results = await graphiti.search("Alice debugging Python DNA GC content")
for result in results:
    print(f"Extracted: {result.fact}")
```

## ⚡ Bulk Episode Loading

For efficiency with large datasets, use bulk loading:

### bulk_loading_demo.py

```python
from graphiti_core.nodes import RawEpisode
import json

async def bulk_loading_demo():
    """Efficiently load multiple episodes"""
    
    # Same Graphiti setup as main demo
    graphiti = Graphiti(...)  # Your configuration here
    
    try:
        print("⚡ Starting Bulk Loading Demo...")
        
        # Prepare multiple episodes efficiently
        episodes = []
        
        # Simulate importing student assessment data
        for student_id in range(1, 11):  # 10 students
            for week in range(1, 5):  # 4 weeks of assessments
                assessment = {
                    "student_id": f"student_{student_id:03d}",
                    "week": week,
                    "topic": f"Python Week {week}",
                    "quiz_score": 70 + (student_id * 2) + (week * 3),  # Varied scores
                    "assignment_score": 75 + (student_id * 1.5) + (week * 2),
                    "participation": "High" if student_id % 2 == 0 else "Medium",
                    "submission_date": f"2024-01-{week*7:02d}"
                }
                
                episodes.append(RawEpisode(
                    name=f"assessment_s{student_id:03d}_w{week}",
                    content=json.dumps(assessment),
                    source=EpisodeType.json,
                    source_description="Bulk assessment import",
                    reference_time=datetime.now() - timedelta(weeks=4-week)
                ))
        
        # Bulk load all episodes (much faster than individual calls)
        print(f"📦 Bulk loading {len(episodes)} assessment episodes...")
        await graphiti.add_episode_bulk(episodes)
        
        print(f"✅ Successfully imported {len(episodes)} episodes")
        
        # Verify the bulk import worked
        print("\n🔍 Searching bulk imported data...")
        search_results = await graphiti.search(
            query="student assessment quiz scores participation week",
            num_results=15
        )
        
        print(f"Found {len(search_results)} results from bulk import:")
        for i, result in enumerate(search_results[:8], 1):
            print(f"  {i}. {result.fact}")
            
    finally:
        await graphiti.close()

if __name__ == "__main__":
    asyncio.run(bulk_loading_demo())
```

## 🎯 Decision Guide: When to Use Each Episode Type

| Your Data | Episode Type | Why | Example |
|-----------|--------------|-----|---------|
| Student essay, reflection, or narrative description | `text` | Rich context needs entity extraction | "Alice reflected on her learning journey..." |
| Tutoring conversation, class discussion, Q&A | `message` | Preserves speaker relationships and dialogue flow | "Student: I'm confused\nTutor: Let me help" |
| Grade records, assessment results, structured logs | `json` | Precise data structure, no ambiguity needed | `{"student": "Alice", "score": 95}` |
| Mixed content (narrative + data) | `text` | Convert structured parts to narrative | "Alice scored 95% and felt confident about..." |
| Email or forum posts | `text` or `message` | Depends on format - if speaker:message format, use `message` | Choose based on structure |

## 🔍 **How Episodes Become Knowledge**

### The Processing Pipeline

1. **Episode Creation** → You add raw information
2. **LLM Analysis** → Graphiti's LLM extracts entities and relationships  
3. **Knowledge Graph Update** → New nodes and edges are created
4. **Searchable Knowledge** → Information becomes queryable and discoverable

### Example: Text Episode Processing

**Input episode:**
```
"Alice Chen scored 92% on her Python loops quiz and is ready to move on to functions."
```

**What Graphiti extracts:**
- **Entities**: `Alice Chen`, `Python loops quiz`, `functions`, `92%`
- **Relationships**: `Alice SCORED 92% ON Python loops quiz`, `Alice READY_FOR functions`
- **Temporal context**: When this achievement occurred
- **Provenance**: Links back to the original episode

### Search Power

After processing, you can search for:
- `"Alice performance"` → Finds her quiz results
- `"students ready for functions"` → Identifies students at that level
- `"Python loops assessments"` → Shows all loop-related evaluations
- `"92 percent scores"` → Finds high-performing students

## ✅ Verification Checklist

- [ ] All three episode types added successfully
- [ ] Search returns results from different episode types
- [ ] Message episodes preserve speaker relationships
- [ ] JSON episodes capture structured data precisely
- [ ] Temporal progression visible in search results
- [ ] Bulk loading working for multiple episodes

## 🤔 Common Questions

**Q: Can I mix episode types for the same event?**
A: Yes! You might have a text episode describing a tutoring session and a JSON episode with the structured assessment data from that session.

**Q: What if my conversation doesn't follow "Speaker: Message" format?**
A: Convert it to that format for message episodes, or use a text episode and describe the conversation narratively.

**Q: How do I know if my JSON is too complex?**
A: If you get context window errors, break large JSON objects into smaller, focused episodes representing specific aspects.

**Q: Should I use text or JSON for grades?**
A: Use JSON for pure data (scores, dates, IDs) and text when you want to capture context ("Alice improved dramatically after struggling initially").

## 📝 What You Learned

✅ **Episode Fundamentals**: Episodes are nodes that become part of your knowledge graph
✅ **Three Episode Types**: Text (narrative), Message (conversations), JSON (structured data)  
✅ **LLM Processing**: How episodes are analyzed to extract entities and relationships
✅ **Temporal Tracking**: Every episode has a time context for historical analysis
✅ **Search Integration**: How different episode types contribute to searchable knowledge
✅ **Bulk Loading**: Efficient techniques for importing large datasets
✅ **Decision Framework**: Clear rules for choosing the right episode type

## 🎯 Next Steps

**Excellent work!** You now understand how to feed different types of data into Graphiti and how that data becomes searchable knowledge.

**Ready for more precision?** Continue to **[03_custom_types](../03_custom_types/)** where you'll learn to define custom entities and relationships like `Student`, `Course`, and `ENROLLED_IN` instead of generic nodes and edges.

**What's Coming**: Transform your knowledge graphs from generic entities to domain-specific, meaningful structures that understand your educational context!

---

**Key Takeaway**: Episodes are the foundation of your knowledge graph. Choose the right episode type based on data structure, not content domain. A math conversation is still a `message` episode, and a math test result is still `json`! 🎯

*"The right episode type makes your knowledge graph more accurate and searchable - think structure, not content!"*