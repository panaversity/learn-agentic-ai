# [Core Concept 02: Custom Entity and Edge Types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types) - Making Knowledge Graphs Domain-Specific

Instead of generic "entities" and "relationships", you can define specific types for your domain. This makes your knowledge graphs much more precise and useful.

## 🎯 What You'll Learn

By the end of this step, you will:
- Define custom entity types (like `Student`, `Course`, `Instructor`)
- Create custom relationship types (like `ENROLLED_IN`, `TEACHES`, `COMPLETED`)
- Use Pydantic models to add attributes to your types
- Apply custom types to episodes for better knowledge extraction
- Design a complete educational domain ontology

## 📚 Core Concepts (Building on Episodes)

### Why Use Custom Types?

**Without Custom Types:**
```
Generic entities: "person", "thing", "concept"
Generic relationships: "relates_to", "connected_to"
```

**With Custom Types:**
```
Specific entities: Student, Course, Instructor, Assignment
Specific relationships: ENROLLED_IN, TEACHES, COMPLETED, STRUGGLES_WITH
```

**Benefits:**
- **More precise knowledge** - Know exactly what each entity represents
- **Better queries** - Search for specific types of information
- **Rich attributes** - Store domain-specific data on entities and relationships
- **Improved LLM extraction** - Guide the AI to find the right types of information

### How to Define Custom Types

Use Pydantic models to define your custom types:

**Custom Entity Example:**
```python
from graphiti_core.nodes import EntityNode
from pydantic import Field
from datetime import datetime

class Student(EntityNode):
    """A student in our educational system"""
    age: int = Field(..., description="Student's age")
    major: str = Field(..., description="Academic major")
    gpa: float = Field(..., description="Current GPA")
    enrollment_year: int = Field(..., description="Year enrolled")
```

**Custom Edge Example:**
```python
from graphiti_core.nodes import EntityEdge

class Enrollment(EntityEdge):
    """Relationship between student and course"""
    semester: str = Field(..., description="Fall 2024, Spring 2025, etc.")
    grade: str = Field(..., description="A, B, C, D, F")
    credits: int = Field(..., description="Credit hours")
```

**Key Points:**
- Inherit from `EntityNode` for entities, `EntityEdge` for relationships
- Use `Field()` to add descriptions and validation
- Add any attributes that make sense for your domain

## 🚀 Worked Examples (Schaum's Method)

### Example 1: Educational Domain Types

Let's build a comprehensive educational ontology:

```python
# educational_types.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from graphiti_core.nodes import EntityNode, EntityEdge

# === ENTITY TYPES ===

class Student(EntityNode):
    """Represents a learner in the educational system"""
    student_id: str = Field(..., description="Unique student identifier")
    age: int = Field(..., description="Student's age")
    major: str = Field(..., description="Academic major or field of study")
    learning_style: str = Field(..., description="Visual, auditory, kinesthetic, etc.")
    enrollment_year: int = Field(..., description="Year student first enrolled")
    gpa: Optional[float] = Field(None, description="Current GPA")
    
class Course(EntityNode):
    """Represents an academic course"""
    course_code: str = Field(..., description="Course identifier (e.g., CS101)")
    credit_hours: int = Field(..., description="Number of credit hours")
    difficulty_level: str = Field(..., description="Beginner, intermediate, advanced")
    prerequisites: List[str] = Field(default=[], description="Required prior courses")
    
class Instructor(EntityNode):
    """Represents a teacher or professor"""
    employee_id: str = Field(..., description="Unique instructor identifier") 
    department: str = Field(..., description="Academic department")
    years_experience: int = Field(..., description="Years of teaching experience")
    specialization: List[str] = Field(..., description="Areas of expertise")

class Skill(EntityNode):
    """Represents a learnable skill or competency"""
    skill_category: str = Field(..., description="Programming, math, communication, etc.")
    difficulty_level: str = Field(..., description="Basic, intermediate, advanced")
    measurable: bool = Field(..., description="Whether skill can be quantitatively assessed")

class Assessment(EntityNode):
    """Represents any form of evaluation"""
    assessment_type: str = Field(..., description="Quiz, exam, project, homework")
    max_points: float = Field(..., description="Maximum possible score")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit if applicable")
    
# === EDGE TYPES ===

class Enrollment(EntityEdge):
    """Student enrolled in course relationship"""
    enrollment_date: datetime = Field(..., description="Date of enrollment")
    status: str = Field(..., description="Active, completed, withdrawn, audit")
    final_grade: Optional[str] = Field(None, description="A, B, C, D, F, or Pass/Fail")

class TeachingAssignment(EntityEdge):
    """Instructor teaches course relationship"""
    semester: str = Field(..., description="Fall 2024, Spring 2025, etc.")
    section_number: str = Field(..., description="Section identifier")
    class_size: int = Field(..., description="Number of enrolled students")

class SkillDevelopment(EntityEdge):
    """Student develops skill relationship"""
    proficiency_level: str = Field(..., description="Novice, developing, proficient, expert")
    assessment_date: datetime = Field(..., description="When proficiency was assessed")
    evidence_source: str = Field(..., description="Assignment, project, observation, etc.")

class Prerequisite(EntityEdge):
    """Course prerequisite relationship"""
    requirement_type: str = Field(..., description="Required, recommended, corequisite")
    can_waive: bool = Field(default=False, description="Whether prerequisite can be waived")

class Assessment_Performance(EntityEdge):
    """Student performance on assessment"""
    score_achieved: float = Field(..., description="Points earned")
    completion_time_minutes: Optional[int] = Field(None, description="Time taken")
    attempt_number: int = Field(default=1, description="Which attempt (if retakes allowed)")
    submission_date: datetime = Field(..., description="When assessment was submitted")
```

### Example 2: Using Custom Types in Episodes

```python
# custom_types_demo.py
import asyncio
import os
from datetime import datetime, timedelta
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from educational_types import Student, Course, Instructor, Enrollment, SkillDevelopment

async def educational_custom_types_demo():
    """Schaum's Worked Example: Custom types in educational episodes"""
    
    client = Graphiti(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print("🎓 SCHAUM'S EXAMPLE: Custom Educational Types")
        print("=" * 60)
        
        await client.build_indices_and_constraints()
        
        # Define our custom types for this session
        entity_types = {
            "Student": Student,
            "Course": Course, 
            "Instructor": Instructor
        }
        
        edge_types = {
            "Enrollment": Enrollment,
            "SkillDevelopment": SkillDevelopment
        }
        
        # Episode 1: Student enrollment with custom types
        print("\n📝 Step 1: Student enrollment with custom entity extraction...")
        await client.add_episode(
            name="alice_enrollment_custom",
            episode_body=(
                "Alice Chen, a 20-year-old biology major, enrolled in CS101 'Introduction to Programming' "
                "on August 28, 2024. She has a visual learning style and is in her second year. "
                "The course is taught by Dr. Sarah Williams, a computer science professor with 8 years "
                "of teaching experience specializing in programming education and software engineering. "
                "CS101 is a 3-credit beginner course with no prerequisites."
            ),
            source=EpisodeType.text,
            source_description="Enrollment system with custom types",
            reference_time=datetime.now() - timedelta(days=60),
            entity_types=entity_types,
            edge_types=edge_types
        )
        print("   ✅ Episode processed with custom entity/edge guidance")
        
        # Episode 2: Assessment performance with custom types
        print("\n📊 Step 2: Assessment with structured custom relationships...")
        await client.add_episode(
            name="alice_first_quiz_custom",
            episode_body=(
                "Alice completed Quiz 1 in CS101 on September 15, 2024. The quiz tested basic programming "
                "concepts and was worth 50 points maximum. Alice scored 47 points, completing it in "
                "32 minutes. This assessment demonstrated her developing proficiency in variables and "
                "basic syntax skills. Dr. Williams noted Alice's careful attention to detail."
            ),
            source=EpisodeType.text,
            source_description="Assessment system with performance tracking",
            reference_time=datetime.now() - timedelta(days=45),
            entity_types=entity_types,
            edge_types=edge_types
        )
        print("   ✅ Assessment performance captured with custom types")
        
        # Episode 3: Skill development progression
        print("\n🚀 Step 3: Skill development with temporal progression...")
        await client.add_episode(
            name="alice_programming_skills_custom",
            episode_body=(
                "By October 10, 2024, Alice had progressed from novice to proficient level in "
                "programming fundamentals. Her skill development in 'Python syntax' moved from "
                "developing to proficient based on her midterm project submission. She also "
                "demonstrated proficient level in 'problem-solving methodology' and 'debugging techniques'. "
                "Evidence sources include her project code, peer code reviews, and instructor observations."
            ),
            source=EpisodeType.text,
            source_description="Skill assessment and development tracking",
            reference_time=datetime.now() - timedelta(days=30),
            entity_types=entity_types,
            edge_types=edge_types
        )
        print("   ✅ Skill progression documented with custom relationship types")
        
        print("\n⏳ Processing episodes with custom type guidance...")
        await asyncio.sleep(4)
        
        # Search for custom type entities
        print("\n🔍 ANALYSIS: Custom type extraction results")
        custom_results = await client.search(
            query="Alice Chen CS101 programming enrollment assessment skills",
            limit=25
        )
        
        print(f"\n📊 Custom Type Analysis:")
        print(f"   Total entities: {len(custom_results.nodes)}")
        print(f"   Total relationships: {len(custom_results.edges)}")
        
        # Analyze by entity types
        entity_types_found = {}
        for node in custom_results.nodes:
            # This would require access to node type information
            # In practice, you'd use the node's type classification
            entity_types_found[type(node).__name__] = entity_types_found.get(type(node).__name__, 0) + 1
        
        print(f"\n🎯 Entity Types Discovered:")
        print(f"   Students: {len([n for n in custom_results.nodes if 'alice' in n.name.lower() or 'student' in n.name.lower()])}")
        print(f"   Courses: {len([n for n in custom_results.nodes if 'cs101' in n.name.lower() or 'programming' in n.name.lower()])}")
        print(f"   Instructors: {len([n for n in custom_results.nodes if 'williams' in n.name.lower() or 'professor' in n.name.lower()])}")
        print(f"   Skills: {len([n for n in custom_results.nodes if 'skill' in n.name.lower() or 'python' in n.name.lower()])}")
        
        print(f"\n🔗 Custom Relationship Types:")
        enrollment_edges = [e for e in custom_results.edges if 'enroll' in e.name.lower()]
        skill_edges = [e for e in custom_results.edges if 'skill' in e.name.lower() or 'develop' in e.name.lower()]
        assessment_edges = [e for e in custom_results.edges if 'score' in e.name.lower() or 'perform' in e.name.lower()]
        
        print(f"   Enrollment relationships: {len(enrollment_edges)}")
        print(f"   Skill development relationships: {len(skill_edges)}")
        print(f"   Assessment performance relationships: {len(assessment_edges)}")
        
        # Show sample relationships
        print(f"\n🔍 Sample Custom Relationships:")
        for i, edge in enumerate(custom_results.edges[:6], 1):
            print(f"   {i}. {edge.source_node_name} → {edge.target_node_name}")
            print(f"      Relationship: {edge.name}")
        
        # Socratic Questions
        print(f"\n🤔 SOCRATIC REFLECTION:")
        print(f"   • How do custom types provide more precise semantic meaning?")
        print(f"   • What educational insights emerge from typed relationships?")
        print(f"   • How might custom types improve AI tutoring recommendations?")
        print(f"   • What would be lost with only generic entity/edge types?")
        
        print(f"\n💡 CUSTOM TYPES INSIGHTS:")
        print(f"   • Domain-specific entities capture precise educational concepts")
        print(f"   • Typed relationships enable sophisticated educational queries")
        print(f"   • Custom attributes store domain-relevant metadata")
        print(f"   • LLM extraction becomes more accurate with type guidance")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting custom types:")
        print("   1. Verify Pydantic model definitions are correct")
        print("   2. Check that entity/edge types are properly passed to add_episode")
        print("   3. Ensure custom types inherit from EntityNode/EntityEdge")
        
    finally:
        await client.close()
        print("\n🔒 Custom types demo completed")

if __name__ == "__main__":
    asyncio.run(educational_custom_types_demo())
```

## 🧪 Practice Exercises

### Exercise 1: Design Your Domain Types

**Scenario**: You're building a TutorsGPT system for a coding bootcamp.

**Your Task**: Define custom types for this domain:

**Entities needed:**
- `Bootcamp` - represents the program
- `Student` - represents learners
- `Mentor` - represents instructors
- `Project` - represents assignments

**Relationships needed:**
- `ENROLLED_IN` - student enrolled in bootcamp
- `MENTORS` - mentor teaches student  
- `ASSIGNED` - project assigned to student
- `COMPLETED` - student completed project

**Try it yourself:**
```python
class Bootcamp(EntityNode):
    duration_weeks: int = Field(..., description="Length of program")
    technology_focus: str = Field(..., description="Main technology taught")
    # Add more attributes...

class Student(EntityNode):
    # What attributes would be useful for a coding student?
    
class ENROLLED_IN(EntityEdge):
    # What information about enrollment would be useful?
```

### Exercise 2: Test Your Types

Add episodes using your custom types:

```python
# Define your types
entity_types = {
    "Bootcamp": Bootcamp,
    "Student": Student,
    "Mentor": Mentor
}

edge_types = {
    "ENROLLED_IN": ENROLLED_IN,
    "MENTORS": MENTORS
}

# Use them in episodes
await client.add_episode(
    name="bootcamp_enrollment",
    episode_body="Sarah enrolled in the 12-week Python bootcamp taught by mentor Jake.",
    source=EpisodeType.text,
    entity_types=entity_types,
    edge_types=edge_types
)
```

### Problem 2: Type Migration
**Challenge**: You have existing episodes without custom types. How do you add types retroactively?

**Your Task**: 
1. Design a migration strategy
2. Consider what data might be lost
3. Plan for backward compatibility

### Problem 3: Advanced Educational Ontology
**Scenario**: Design types for a complex educational scenario with:
- Multiple learning pathways
- Prerequisite chains
- Competency-based assessment
- Peer collaboration

## 🔧 Advanced Techniques

### Type Constraints and Validation

```python
from pydantic import validator, root_validator

class Student(EntityNode):
    age: int = Field(..., description="Student age")
    gpa: Optional[float] = Field(None, description="GPA")
    
    @validator('age')
    def age_must_be_reasonable(cls, v):
        if v < 16 or v > 65:
            raise ValueError('Age must be between 16 and 65 for students')
        return v
    
    @validator('gpa')
    def gpa_must_be_valid(cls, v):
        if v is not None and (v < 0.0 or v > 4.0):
            raise ValueError('GPA must be between 0.0 and 4.0')
        return v
```

### Dynamic Type Selection

```python
async def smart_episode_processing(episode_content: str):
    """Dynamically choose types based on content analysis"""
    
    # Analyze content to determine likely domain
    if "student" in episode_content.lower() and "course" in episode_content.lower():
        entity_types = {"Student": Student, "Course": Course}
        edge_types = {"Enrollment": Enrollment}
    elif "assessment" in episode_content.lower():
        entity_types = {"Assessment": Assessment, "Student": Student}
        edge_types = {"Performance": Assessment_Performance}
    else:
        entity_types = {}  # Use default extraction
        edge_types = {}
    
    await client.add_episode(
        name="smart_typed_episode",
        episode_body=episode_content,
        source=EpisodeType.text,
        entity_types=entity_types,
        edge_types=edge_types
    )
```

## ✅ Understanding Check (Socratic Method)

### Essential Questions
1. **Why** are custom types more powerful than generic entity extraction?
2. **When** should you define a new entity type vs. using attributes?
3. **How** do custom edge types change the semantic meaning of relationships?
4. **What** happens to existing data when you introduce new types?

### Critical Thinking
1. **If** you have overlapping entity types (Student vs. Person), how do you handle classification?
2. **What if** your domain evolves and you need to add new attributes to existing types?
3. **How might** custom types affect query performance and storage?

### Design Challenges
1. Design types for a medical education system (patients, procedures, competencies)
2. Create types for a corporate training platform (employees, skills, certifications)
3. Model types for a research collaboration network (researchers, papers, citations)

## 🐛 Common Issues & Solutions

### Issue 1: "Type inheritance conflicts"
**Problem**: Multiple inheritance or conflicting type definitions
**Solution**: Use composition over inheritance and clear type hierarchies

### Issue 2: "Attribute validation errors"
**Problem**: Pydantic validation fails during episode processing
**Solution**: Add proper validators and handle edge cases

### Issue 3: "Migration breaking existing queries"
**Problem**: Adding types changes how existing data is interpreted
**Solution**: Plan migration carefully with backward compatibility

## 📝 What You Learned

Congratulations! You now know how to create domain-specific knowledge graphs:

### **Key Skills Gained**
✅ **Custom Entity Types**: Define specific types like `Student`, `Course`, `Instructor`
✅ **Custom Relationship Types**: Create precise relationships like `ENROLLED_IN`, `TEACHES`
✅ **Pydantic Models**: Add attributes and validation to your types
✅ **Type Application**: Use custom types in episodes for better extraction
✅ **Domain Design**: Think systematically about your knowledge domain

### **Benefits of Custom Types**
- **Precision**: Know exactly what each entity represents
- **Rich Data**: Store domain-specific attributes on entities and relationships
- **Better Queries**: Search for specific types of information
- **Guided Extraction**: Help the LLM find the right information

## 🎯 Next Steps

**Ready to see patterns emerge automatically?** Continue to **[04_communities](../04_communities/)** where you'll learn how Graphiti automatically discovers groups and clusters in your knowledge graphs.

**What's Coming**: Instead of manually organizing information, you'll see how Graphiti finds related entities and groups them into "communities" - like discovering that certain students always struggle with the same topics, or that certain teaching methods work well together.

## 📚 Key Takeaways

1. **Custom types make graphs more useful** - Domain-specific is better than generic
2. **Pydantic provides structure** - Use it to define your entities and relationships
3. **Start simple** - Begin with basic types and add complexity gradually
4. **Types guide extraction** - Help the LLM understand what to look for
5. **Think about your domain** - What entities and relationships matter most?

---

**Design tip**: Start with the most important entities in your domain (like `Student` and `Course` for education) and add more types as you discover what you need. Don't try to model everything at once! 🚀

*"The best custom types emerge from understanding your domain deeply and starting with the most essential entities and relationships."*