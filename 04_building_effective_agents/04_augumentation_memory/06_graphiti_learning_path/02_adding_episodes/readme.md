# Step 02: [Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes) - The Three Data Types

Now that you've created your first Graphiti program, let's master episodes - the foundation of how Graphiti ingests and processes information.

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

**Use for:** Dialogues, chats, tutoring sessions, interviews, Q&A sessions. Using the EpisodeType.message type supports passing in multi-turn conversations in the episode_body. The text should be structured in {role/name}: {message} pairs.

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

### main.py

```python
import asyncio
import os
import json

from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Gemini setup (same as Step 01)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())


async def main():
    """Complete example using all three episode types"""

    # Initialize Graphiti (same setup as Step 01)
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
        print("🚀 Starting Episode Types Demo...")

        # 3. JSON EPISODE - Assessment results
        print("📊 Adding JSON episode (assessment data)...")
        assessment_result = {
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
            "strengths": ["basic loop syntax", "iteration logic"],
            "needs_improvement": ["nested loop complexity"],
            "instructor_notes": "Great progress! Ready for functions next."
        }

        await graphiti.add_episode(
            name="alice_loops_assessment",
            episode_body=json.dumps(assessment_result),
            source=EpisodeType.json,
            source_description="Assessment system results",
            reference_time=datetime.now() - timedelta(days=1),
        )

        print("✅ All episodes added successfully!")

        # Specific searches by type
        print("\n🎯 Searching for alice tutoring interactions...")
        tutoring_results = await graphiti.search(
            query="What is alice confusion",
            num_results=5,
        )

        print(f"Tutoring insights: {len(tutoring_results)} results")
        for result in tutoring_results[:3]:
            print(f"  • {result.fact}")

        print("\n🎓 Episode types demo completed!")

    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())


```

## ▶️ Running the Example

1. **Save the code** as `main.py`
2. **Make sure your environment** from Step 01 is working
3. **Run the program**:

```bash
uv run python main.py
```

## 📊 Expected Output

```
🚀 Starting Episode Types Demo...
📊 Adding JSON episode (assessment data)...
✅ All episodes added successfully!

🎯 Searching for alice tutoring interactions...
Tutoring insights: 5 results
  • student_id: alice_chen_001
  • questions_total: 8
  • questions_correct: 7

🎓 Episode types demo completed!
Connection closed.
```

## 🧪 Try It Yourself

### Exercise 1: Add More Episode Types

Create episodes for different educational scenarios:

### Exercise 2: Understanding Episode Processing

Add episodes and then search to see what was extracted.

## ⚡ Bulk Episode Loading

For efficiency with large datasets, use bulk loading.

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

#### Example: Text Episode Processing

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

## 🤔 Common Questions

**Q: Can I mix episode types for the same event?**
A: Yes! You might have a text episode describing a tutoring session and a JSON episode with the structured assessment data from that session.

**Q: What if my conversation doesn't follow "Speaker: Message" format?**
A: Convert it to that format for message episodes, or use a text episode and describe the conversation narratively.

**Q: How do I know if my JSON is too complex?**
A: If you get context window errors, break large JSON objects into smaller, focused episodes representing specific aspects.

**Q: Should I use text or JSON for grades?**
A: Use JSON for pure data (scores, dates, IDs) and text when you want to capture context ("Alice improved dramatically after struggling initially").

## 🎯 Next Steps

Continue to **[03_custom_types](../03_custom_types/)** where you'll learn to define custom entities and relationships like `Student`, `Course`, and `ENROLLED_IN` instead of generic nodes and edges.