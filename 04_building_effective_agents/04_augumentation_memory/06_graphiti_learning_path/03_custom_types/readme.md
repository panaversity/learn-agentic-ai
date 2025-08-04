# Step 03: Custom Entity & Edge Types - Making Knowledge Graphs Domain-Specific

Now that you understand episodes, let's make your knowledge graphs much more precise by defining custom types for your educational domain.

## 📚 Official Documentation

- [Custom Entity and Edge Types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types) - Complete guide to custom types

## 🎯 What You'll Learn

By the end of this step, you will:
- Define custom entity types (like `Student`, `Course`, `Instructor`)
- Create custom edge types (like `ENROLLED_IN`, `TEACHES`, `COMPLETED`)
- Use Pydantic models to add rich attributes and validation
- Apply custom types to episodes for precise knowledge extraction
- Search with type filters for targeted results

## 📋 Prerequisites

- Completed Steps 01 and 02
- Understanding of episodes and basic Graphiti operations
- Basic knowledge of Python classes and type hints

## 📚 Why Custom Types Matter

### The Problem with Generic Types

**Without Custom Types:**
```
Generic entities: "person", "thing", "concept", "event"
Generic relationships: "relates_to", "connected_to", "associated_with"
```

**Result:** Vague, hard-to-query knowledge graphs with unclear semantics

### The Power of Custom Types

**With Custom Types:**
```
Educational entities: Student, Course, Instructor, Assignment, Skill
Educational relationships: ENROLLED_IN, TEACHES, COMPLETED, MASTERED, STRUGGLES_WITH
```

**Result:** Precise, queryable, domain-specific knowledge that understands your educational context

### Key Benefits

- **Semantic Precision**: Know exactly what each entity represents
- **Rich Attributes**: Store domain-specific data (GPA, course credits, skill levels)
- **Better Queries**: Search for specific types of information  
- **Guided LLM**: Help AI extract the right types of information from episodes
- **Type Safety**: Validate data structure and catch errors early

## 🏗️ **Understanding Custom Types Architecture**

### Entity Types vs Edge Types

**Entity Types** define "things" in your domain:
- `Student` - a learner with attributes like GPA, major, learning style
- `Course` - a class with credits, difficulty, prerequisites
- `Instructor` - a teacher with experience, specialization, department
- `Skill` - a competency with difficulty level, category

**Edge Types** define "relationships" between things:
- `Enrollment` - student ↔ course relationship with grade, semester, status
- `TeachingAssignment` - instructor ↔ course relationship with schedule, section
- `SkillDevelopment` - student ↔ skill relationship with proficiency, evidence
- `PrerequisiteRelationship` - course ↔ course dependency with strength

### Using Pydantic for Type Definition

Graphiti uses **Pydantic BaseModel** for custom types. This provides:
- **Type validation** - ensures data integrity
- **Rich attributes** - structured fields with descriptions
- **Documentation** - built-in schema generation
- **IDE support** - autocomplete and type checking

## 🚀 Complete Working Example

Let's build comprehensive educational types:

### custom_types_demo.py

```python
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_filters import SearchFilters

# Gemini setup (same as previous steps)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

# === CUSTOM ENTITY TYPES ===

class Student(BaseModel):
    """A learner in our educational system"""
    age: Optional[int] = Field(None, description="Student's age")
    major: Optional[str] = Field(None, description="Academic major or field of study")
    learning_style: Optional[str] = Field(None, description="Visual, auditory, kinesthetic, etc.")
    enrollment_year: Optional[int] = Field(None, description="Year student first enrolled")
    gpa: Optional[float] = Field(None, description="Current GPA (0.0-4.0)")
    academic_level: Optional[str] = Field(None, description="Freshman, Sophomore, Junior, Senior")

class Course(BaseModel):
    """An academic course or class"""
    course_code: Optional[str] = Field(None, description="Course identifier (e.g., CS101)")
    credit_hours: Optional[int] = Field(None, description="Number of credit hours")
    difficulty_level: Optional[str] = Field(None, description="Beginner, intermediate, advanced")
    department: Optional[str] = Field(None, description="Academic department")
    max_enrollment: Optional[int] = Field(None, description="Maximum number of students")

class Instructor(BaseModel):
    """A teacher or professor"""
    department: Optional[str] = Field(None, description="Academic department")
    years_experience: Optional[int] = Field(None, description="Years of teaching experience")
    specialization: Optional[str] = Field(None, description="Primary area of expertise")
    title: Optional[str] = Field(None, description="Professor, Associate Professor, etc.")
    office_location: Optional[str] = Field(None, description="Office building and room number")

class Skill(BaseModel):
    """A learnable skill or competency"""
    skill_category: Optional[str] = Field(None, description="Programming, math, communication, etc.")
    difficulty_level: Optional[str] = Field(None, description="Basic, intermediate, advanced")
    measurable: Optional[bool] = Field(None, description="Whether skill can be quantitatively assessed")
    prerequisite_skills: Optional[List[str]] = Field(None, description="Skills needed before learning this")

class Assignment(BaseModel):
    """A homework, project, or assessment"""
    assignment_type: Optional[str] = Field(None, description="Homework, project, quiz, exam")
    max_points: Optional[float] = Field(None, description="Maximum possible score")
    due_date: Optional[str] = Field(None, description="Assignment due date")
    difficulty_rating: Optional[int] = Field(None, description="Difficulty from 1-10")

# === CUSTOM EDGE TYPES ===

class Enrollment(BaseModel):
    """Student enrolled in course relationship"""
    enrollment_date: Optional[str] = Field(None, description="Date of enrollment")
    status: Optional[str] = Field(None, description="Active, completed, withdrawn, audit")
    final_grade: Optional[str] = Field(None, description="A, B, C, D, F, or Pass/Fail")
    semester: Optional[str] = Field(None, description="Fall 2024, Spring 2025, etc.")
    midterm_grade: Optional[str] = Field(None, description="Midterm performance indicator")

class TeachingAssignment(BaseModel):
    """Instructor teaches course relationship"""
    semester: Optional[str] = Field(None, description="Fall 2024, Spring 2025, etc.")
    section_number: Optional[str] = Field(None, description="Section identifier")
    class_size: Optional[int] = Field(None, description="Number of enrolled students")
    schedule: Optional[str] = Field(None, description="Class meeting times")

class SkillDevelopment(BaseModel):
    """Student develops skill relationship"""
    proficiency_level: Optional[str] = Field(None, description="Novice, developing, proficient, expert")
    assessment_date: Optional[str] = Field(None, description="When proficiency was assessed")
    evidence_source: Optional[str] = Field(None, description="Assignment, project, observation, etc.")
    confidence_score: Optional[float] = Field(None, description="Confidence in assessment (0.0-1.0)")

class AssignmentSubmission(BaseModel):
    """Student submission of assignment"""
    submission_date: Optional[str] = Field(None, description="When submitted")
    score_achieved: Optional[float] = Field(None, description="Points earned")
    time_spent_hours: Optional[float] = Field(None, description="Time spent on assignment")
    attempt_number: Optional[int] = Field(None, description="Which attempt (if retakes allowed)")
    feedback_received: Optional[str] = Field(None, description="Instructor feedback summary")

async def main():
    """Complete example using custom educational types"""
    
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
        print("🎓 Starting Custom Types Demo...")
        
        # Define our custom type mappings
        entity_types = {
            "Student": Student,
            "Course": Course, 
            "Instructor": Instructor,
            "Skill": Skill,
            "Assignment": Assignment
        }
        
        edge_types = {
            "Enrollment": Enrollment,
            "TeachingAssignment": TeachingAssignment,
            "SkillDevelopment": SkillDevelopment,
            "AssignmentSubmission": AssignmentSubmission
        }
        
        # Define which edge types can exist between entity types
        edge_type_map = {
            ("Student", "Course"): ["Enrollment"],
            ("Instructor", "Course"): ["TeachingAssignment"],
            ("Student", "Skill"): ["SkillDevelopment"],
            ("Student", "Assignment"): ["AssignmentSubmission"],
            ("Entity", "Entity"): ["RELATES_TO"]  # Fallback for unexpected relationships
        }
        
        # 1. ENROLLMENT EPISODE with custom types
        print("\n📝 Adding enrollment episode with custom types...")
        await graphiti.add_episode(
            name="alice_cs101_enrollment",
            episode_body=(
                "Alice Chen, a 20-year-old computer science sophomore with a visual learning style, "
                "enrolled in CS101 'Introduction to Programming' on August 28, 2024. "
                "This is a 3-credit beginner course in the Computer Science department with "
                "maximum enrollment of 50 students. The course is taught by Dr. Sarah Williams, "
                "a Computer Science professor with 8 years of teaching experience, "
                "specializing in programming education. Dr. Williams has her office in "
                "Engineering Building room 301."
            ),
            source=EpisodeType.text,
            source_description="Student enrollment with custom types",
            reference_time=datetime.now() - timedelta(days=30),
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map
        )
        
        # 2. SKILL DEVELOPMENT EPISODE
        print("📊 Adding skill development episode...")
        await graphiti.add_episode(
            name="alice_python_skill_progress",
            episode_body=(
                "Alice developed her Python programming skills from novice to proficient level "
                "between September and October 2024. Her proficiency in Python syntax moved from "
                "developing to proficient based on her midterm project submission evidence. "
                "She also demonstrated proficient level in problem-solving methodology, "
                "with high confidence scores from multiple coding assignments. "
                "Her prerequisite skills in logical thinking and mathematics provided "
                "a strong foundation for programming concepts."
            ),
            source=EpisodeType.text,
            source_description="Skill development tracking",
            reference_time=datetime.now() - timedelta(days=15),
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map
        )
        
        # 3. ASSIGNMENT SUBMISSION EPISODE
        print("📝 Adding assignment submission episode...")
        assignment_data = {
            "student_name": "Alice Chen",
            "assignment_name": "Python Loops Project",
            "assignment_type": "Project",
            "max_points": 100,
            "score_achieved": 94,
            "submission_date": "2024-09-20",
            "time_spent_hours": 12.5,
            "attempt_number": 1,
            "difficulty_rating": 6,
            "instructor_feedback": "Excellent work on loop implementation and code documentation"
        }
        
        await graphiti.add_episode(
            name="alice_loops_project_submission",
            episode_body=assignment_data,
            source=EpisodeType.json,
            source_description="Assignment submission system",
            reference_time=datetime.now() - timedelta(days=10),
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map
        )
        
        print("✅ All episodes with custom types added!")
        
        # SEARCH WITH TYPE FILTERS
        print("\n🔍 Searching with custom type filters...")
        
        # Search for only Student and Course entities
        try:
            student_course_filter = SearchFilters(
                node_labels=["Student", "Course"]
            )
            
            student_results = await graphiti.search(
                query="Alice Chen CS101 programming enrollment computer science",
                search_filter=student_course_filter,
                num_results=10
            )
            
            print(f"\n👨‍🎓 Student & Course Results: {len(student_results)} found")
            for i, result in enumerate(student_results[:4], 1):
                print(f"  {i}. {result.fact}")
                
        except Exception as e:
            print(f"   Note: Type filtering requires compatible search configuration: {e}")
        
        # Search for enrollment and skill development patterns
        enrollment_search = await graphiti.search(
            query="Alice enrollment CS101 programming course semester",
            num_results=8
        )
        
        print(f"\n📚 Enrollment Patterns: {len(enrollment_search)} found")
        for i, result in enumerate(enrollment_search[:4], 1):
            print(f"  {i}. {result.fact}")
        
        # Search for skill development and assignments
        skill_search = await graphiti.search(
            query="Alice Python skill development proficient programming assignments",
            num_results=8
        )
        
        print(f"\n🚀 Skill Development: {len(skill_search)} found")
        for i, result in enumerate(skill_search[:4], 1):
            print(f"  {i}. {result.fact}")
        
        # General search to see all custom type results
        print("\n📊 General search across all custom types...")
        all_results = await graphiti.search(
            query="Alice Chen computer science programming course instructor assignments",
            num_results=15
        )
        
        print(f"\n🎯 All Custom Type Results: {len(all_results)} found")
        for i, result in enumerate(all_results[:6], 1):
            print(f"  {i}. {result.fact}")
        
        print("\n🎓 Custom types demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting custom types:")
        print("   1. Verify Pydantic models are properly defined")
        print("   2. Check that entity_types and edge_types dictionaries are correct")
        print("   3. Ensure edge_type_map covers your expected relationships")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
```

## ▶️ Running the Example

1. **Save the code** as `custom_types_demo.py`
2. **Use the same environment** from previous steps
3. **Run the program**:

```bash
uv run python custom_types_demo.py
```

## 📊 Expected Output

```
🎓 Starting Custom Types Demo...

📝 Adding enrollment episode with custom types...
📊 Adding skill development episode...
📝 Adding assignment submission episode...
✅ All episodes with custom types added!

🔍 Searching with custom type filters...

👨‍🎓 Student & Course Results: 6 found
  1. Alice Chen enrolled in CS101 Introduction to Programming
  2. CS101 is 3-credit beginner course in Computer Science department
  3. Alice Chen is computer science sophomore with visual learning style
  4. Dr. Sarah Williams teaches CS101 programming course

📚 Enrollment Patterns: 5 found
  1. Alice Chen enrolled in CS101 on August 28, 2024
  2. CS101 has maximum enrollment of 50 students
  3. Course taught by Dr. Sarah Williams with 8 years experience
  4. Alice Chen is computer science sophomore student

🚀 Skill Development: 7 found
  1. Alice developed Python programming skills from novice to proficient
  2. Alice's Python syntax proficiency moved from developing to proficient
  3. Alice demonstrated proficient problem-solving methodology
  4. Alice scored 94 points on Python Loops Project assignment

📊 General search across all custom types...

🎯 All Custom Type Results: 12 found
  1. Alice Chen enrolled in CS101 Introduction to Programming
  2. Alice developed Python programming skills to proficient level
  3. Alice scored 94 on Python Loops Project with excellent feedback
  4. Dr. Sarah Williams specializes in programming education
  5. CS101 is beginner-level course with 3 credit hours
  6. Alice spent 12.5 hours on Python Loops Project

🎓 Custom types demo completed successfully!
```

## 🧪 Try It Yourself

### Exercise 1: Add More Custom Types

Extend the example with additional educational types:

```python
class Department(BaseModel):
    """Academic department"""
    department_name: Optional[str] = Field(None, description="Official department name")
    building_location: Optional[str] = Field(None, description="Main building location")
    faculty_count: Optional[int] = Field(None, description="Number of faculty members")
    research_areas: Optional[List[str]] = Field(None, description="Primary research focuses")

class Textbook(BaseModel):
    """Course textbook or resource"""
    isbn: Optional[str] = Field(None, description="International Standard Book Number")
    author: Optional[str] = Field(None, description="Book author(s)")
    edition: Optional[int] = Field(None, description="Book edition number")
    required: Optional[bool] = Field(None, description="Whether textbook is required")

# Add to your entity_types dictionary
entity_types["Department"] = Department
entity_types["Textbook"] = Textbook
```

### Exercise 2: Advanced Edge Types

Create more complex relationship types:

```python
class PrerequisiteRelationship(BaseModel):
    """Course prerequisite relationship"""
    requirement_type: Optional[str] = Field(None, description="Hard prerequisite, recommended, corequisite")
    minimum_grade: Optional[str] = Field(None, description="Minimum grade required")
    waiver_possible: Optional[bool] = Field(None, description="Can prerequisite be waived")
    established_date: Optional[str] = Field(None, description="When requirement was established")

class MentorshipRelationship(BaseModel):
    """Student-instructor mentorship"""
    mentorship_type: Optional[str] = Field(None, description="Academic, research, career")
    start_date: Optional[str] = Field(None, description="When mentorship began")
    meeting_frequency: Optional[str] = Field(None, description="Weekly, monthly, as-needed")
    focus_areas: Optional[List[str]] = Field(None, description="Areas of mentorship focus")
```

### Exercise 3: Type Validation

Add Pydantic validators for data quality:

```python
from pydantic import validator

class Student(BaseModel):
    age: Optional[int] = Field(None, description="Student's age")
    gpa: Optional[float] = Field(None, description="Current GPA (0.0-4.0)")
    
    @validator('age')
    def age_must_be_reasonable(cls, v):
        if v is not None and (v < 16 or v > 65):
            raise ValueError('Age must be between 16 and 65')
        return v
    
    @validator('gpa')
    def gpa_must_be_valid(cls, v):
        if v is not None and (v < 0.0 or v > 4.0):
            raise ValueError('GPA must be between 0.0 and 4.0')
        return v
```

## 🎯 Key Concepts Explained

### How Custom Types Guide LLM Extraction

**Without Custom Types:**
```
"Alice enrolled in CS101" → Generic entities: "person", "thing"
```

**With Custom Types:**
```
"Alice enrolled in CS101" → Specific entities: Student("Alice"), Course("CS101")
                          → Specific relationship: Enrollment(semester="Fall 2024")
```

### Edge Type Mapping Strategy

The `edge_type_map` tells Graphiti which relationships can exist:

```python
edge_type_map = {
    ("Student", "Course"): ["Enrollment"],           # Students can enroll in courses
    ("Instructor", "Course"): ["TeachingAssignment"], # Instructors can teach courses
    ("Student", "Skill"): ["SkillDevelopment"],      # Students can develop skills
    ("Course", "Course"): ["PrerequisiteRelationship"], # Courses can require other courses
    ("Entity", "Entity"): ["RELATES_TO"]             # Fallback for unexpected relationships
}
```

### Benefits of Rich Attributes

Custom types allow storing detailed, structured information:

```python
# Instead of just knowing "Alice enrolled in CS101"
# You get rich relationship data:
Enrollment(
    enrollment_date="2024-08-28",
    status="Active", 
    semester="Fall 2024",
    midterm_grade="B+",
    final_grade=None  # Still in progress
)
```

### Search Filter Advantages

With custom types, you can search precisely:

```python
# Find only students and courses
SearchFilters(node_labels=["Student", "Course"])

# Find only enrollment relationships  
SearchFilters(edge_types=["Enrollment"])

# Combine both for very targeted searches
SearchFilters(
    node_labels=["Student"], 
    edge_types=["SkillDevelopment"]
)
```

## ✅ Verification Checklist

- [ ] Custom entity types defined with meaningful attributes
- [ ] Custom edge types capture relationship details
- [ ] Edge type mapping covers expected relationships
- [ ] Episodes processed with custom type guidance
- [ ] Search results show domain-specific entities and relationships
- [ ] Type filtering working (where supported)

## 🤔 Common Questions

**Q: What's the difference between episodes and custom types?**
A: Episodes are the raw data you input. Custom types guide how Graphiti extracts and structures that data into precise entities and relationships.

**Q: Can I change custom types after adding episodes?**
A: Yes, but you may need to re-process episodes to get the new type structure. Plan your types carefully upfront.

**Q: How many custom types should I create?**
A: Start with 3-5 core entity types and 2-3 key relationship types. Add more as you discover what you need.

**Q: Do I need to use all the optional fields?**
A: No! Pydantic's Optional fields mean you can use what you have. Empty fields are fine.

## 📝 What You Learned

✅ **Domain-Specific Types**: Defined precise educational entities instead of generic nodes
✅ **Rich Relationships**: Created meaningful edge types with detailed attributes
✅ **Pydantic Models**: Used structured, validated data models for type safety
✅ **LLM Guidance**: Helped Graphiti extract exactly the information you need
✅ **Targeted Search**: Used type filters for precise knowledge retrieval
✅ **Educational Schema**: Built a complete academic domain model

## 🎯 Next Steps

**Excellent progress!** You now have precise, domain-specific knowledge graphs instead of generic entities and relationships.

**Ready to discover patterns automatically?** Continue to **[04_communities](../04_communities/)** where you'll learn how Graphiti automatically finds groups and clusters in your knowledge graph.

**What's Coming**: Instead of manually organizing information, you'll see how Graphiti discovers that certain students struggle with similar topics, or that certain teaching methods work well together - all automatically!

---

**Key Takeaway**: Custom types transform generic knowledge graphs into precise, domain-specific knowledge systems. Start with your most important entities and relationships, then expand as needed! 🚀

*"The best custom types emerge from understanding your domain deeply and starting with the most essential entities and relationships."*