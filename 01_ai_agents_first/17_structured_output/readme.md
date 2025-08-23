# 📊 Structured Output: Making Agents Return Perfect Data

## 🎯 What is Structured Output?

Think of **Structured Output** like **ordering from a restaurant with a specific form**. Instead of saying "give me some food" and getting random items, you fill out a precise order form that guarantees you get exactly what you want in the right format.

### 🧒 Simple Analogy: The Order Form

**Without Structured Output (Messy)**:
- You: "Tell me about the weather"
- Agent: "It's pretty nice today, maybe around 75 degrees and sunny in New York"
- You: 😕 "How do I extract the temperature? What city? Is it Fahrenheit or Celsius?"

**With Structured Output (Perfect)**:
- You: "Tell me about the weather"
- Agent: `{"location": "New York", "temperature_c": 24, "summary": "sunny"}`
- You: 😎 "Perfect! I can use this data directly in my app!"

---

## 📊 The Core Concept

**Regular Output (Unpredictable)**:
```python
# Agent returns free-form text
result = Runner.run_sync(agent, "What's the weather in Karachi?")
print(result.final_output)
# "The weather in Karachi is quite warm today, around 30 degrees Celsius with clear skies."
# Problem: How do you extract the temperature? The format changes every time!
```

**Structured Output (Predictable)**:
```python
# Agent returns structured data
class WeatherAnswer(BaseModel):
    location: str
    temperature_c: float
    summary: str

agent = Agent(output_type=WeatherAnswer)
result = Runner.run_sync(agent, "What's the weather in Karachi?")

# Perfect! Now you get structured data:
print(result.final_output.location)      # "Karachi"
print(result.final_output.temperature_c) # 30.0
print(result.final_output.summary)       # "clear skies"
```

---

## 🔧 How Structured Output Works

### **The Magic Behind the Scenes**

When you use structured output, the agent:

1. **Understands the Schema**: Knows exactly what fields to fill
2. **Validates the Data**: Ensures all required fields are present
3. **Formats Correctly**: Returns data in the exact structure you specified
4. **Type Checks**: Guarantees temperature is a number, not text

```python
# What happens automatically:
class PersonInfo(BaseModel):
    name: str          # Must be text
    age: int           # Must be a whole number
    email: str         # Must be text
    is_student: bool   # Must be True/False

# Agent MUST return data in this exact format
# If it tries to return invalid data, it gets corrected automatically!
```

### **Pydantic Models - Your Data Blueprint**

| Component | What It Does | Example |
|-----------|-------------|---------|
| **Class Definition** | Creates the data structure | `class WeatherInfo(BaseModel):` |
| **Field Types** | Specifies what kind of data | `temperature: float` |
| **Required Fields** | Must be included | All fields are required by default |
| **Optional Fields** | Can be missing | `rainfall: Optional[float] = None` |

---

## 🎯 Baby Steps Examples

### 1. **Your First Structured Output**

```python
from pydantic import BaseModel
from agents import Agent, Runner

# Define your data structure
class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

# Create agent with structured output
agent = Agent(
    name="InfoCollector",
    instructions="Extract person information from the user's message.",
    output_type=PersonInfo  # This is the magic!
)

# Test it
result = Runner.run_sync(
    agent, 
    "Hi, I'm Alice, I'm 25 years old and I work as a teacher."
)

# Now you get perfect structured data!
print("Type:", type(result.final_output))        # <class 'PersonInfo'>
print("Name:", result.final_output.name)         # "Alice"
print("Age:", result.final_output.age)           # 25
print("Job:", result.final_output.occupation)    # "teacher"
```

### 2. **Different Data Types**

```python
from typing import Optional, List
from datetime import datetime

class ProductInfo(BaseModel):
    name: str                           # Text
    price: float                        # Decimal number
    in_stock: bool                      # True/False
    categories: List[str]               # List of text items
    discount_percent: Optional[int] = 0 # Optional number, default 0
    reviews_count: int                  # Whole number

# Create product info extractor
agent = Agent(
    name="ProductExtractor",
    instructions="Extract product information from product descriptions.",
    output_type=ProductInfo
)

# Test with product description
result = Runner.run_sync(
    agent,
    "The iPhone 15 Pro costs $999.99, it's available in electronics and smartphones categories, currently in stock with 1,247 reviews."
)

print("Product:", result.final_output.name)         # "iPhone 15 Pro"
print("Price:", result.final_output.price)          # 999.99
print("In Stock:", result.final_output.in_stock)    # True
print("Categories:", result.final_output.categories) # ["electronics", "smartphones"]
print("Reviews:", result.final_output.reviews_count) # 1247
```

## 🏗️ Real-World Applications

### **Meeting Minutes Extractor**

```python
from datetime import datetime
from typing import List, Optional

class ActionItem(BaseModel):
    task: str
    assignee: str
    due_date: Optional[str] = None
    priority: str = "medium"

class Decision(BaseModel):
    topic: str
    decision: str
    rationale: Optional[str] = None

class MeetingMinutes(BaseModel):
    meeting_title: str
    date: str
    attendees: List[str]
    agenda_items: List[str]
    key_decisions: List[Decision]
    action_items: List[ActionItem]
    next_meeting_date: Optional[str] = None
    meeting_duration_minutes: int

# Meeting minutes extractor
agent = Agent(
    name="MeetingSecretary",
    instructions="""Extract structured meeting minutes from meeting transcripts.
    Identify all key decisions, action items, and important details.""",
    output_type=MeetingMinutes
)

meeting_transcript = """
Marketing Strategy Meeting - January 15, 2024
Attendees: Sarah (Marketing Manager), John (Product Manager), Lisa (Designer), Mike (Developer)
Duration: 90 minutes

Agenda:
1. Q1 Campaign Review
2. New Product Launch Strategy  
3. Budget Allocation
4. Social Media Strategy

Key Decisions:
- Approved $50K budget for Q1 digital campaigns based on strong ROI data
- Decided to launch new product in March instead of February for better market timing
- Will focus social media efforts on Instagram and TikTok for younger demographics

Action Items:
- Sarah to create campaign timeline by January 20th (high priority)
- John to finalize product features by January 25th
- Lisa to design landing page mockups by January 22nd
- Mike to review technical requirements by January 30th

Next meeting: January 29, 2024
"""

result = Runner.run_sync(agent, meeting_transcript)

print("=== Meeting Minutes ===")
print(f"Meeting Minutes: {result.final_output}")
```

---

## 🧪 Try It Yourself!

### Exercise 1: Build a Resume Parser

```python
from typing import List, Optional

class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: int
    gpa: Optional[float] = None

class Experience(BaseModel):
    position: str
    company: str
    start_year: int
    end_year: Optional[int] = None  # None if current job
    responsibilities: List[str]

class Resume(BaseModel):
    full_name: str
    email: str
    phone: str
    summary: str
    education: List[Education]
    experience: List[Experience]
    skills: List[str]
    languages: List[str]

# Create resume parser
resume_parser = Agent(
    name="ResumeParser",
    instructions="Extract structured information from resume text.",
    output_type=Resume
)

# Test with sample resume
sample_resume = """
John Smith
Email: john.smith@email.com, Phone: (555) 123-4567

Professional Summary:
Experienced software developer with 5 years in web development and team leadership.

Education:
- Bachelor of Computer Science, MIT, 2018, GPA: 3.8
- Master of Software Engineering, Stanford, 2020

Experience:
- Senior Developer at Google (2020-present): Led team of 5 developers, implemented microservices architecture
- Junior Developer at Startup Inc (2018-2020): Built React applications, maintained CI/CD pipelines

Skills: Python, JavaScript, React, Docker, Kubernetes
Languages: English (native), Spanish (conversational), French (basic)
"""

result = Runner.run_sync(resume_parser, sample_resume)

print("=== Parsed Resume ===")
print(f"Name: {result.final_output.full_name}")
print(f"Email: {result.final_output.email}")
print(f"Phone: {result.final_output.phone}")
print(f"Summary: {result.final_output.summary}")

print("\nEducation:")
for edu in result.final_output.education:
    gpa_str = f", GPA: {edu.gpa}" if edu.gpa else ""
    print(f"  • {edu.degree} from {edu.institution} ({edu.graduation_year}){gpa_str}")

print("\nExperience:")
for exp in result.final_output.experience:
    end_year = exp.end_year if exp.end_year else "present"
    print(f"  • {exp.position} at {exp.company} ({exp.start_year}-{end_year})")
    for resp in exp.responsibilities:
        print(f"    - {resp}")

print(f"\nSkills: {', '.join(result.final_output.skills)}")
print(f"Languages: {', '.join(result.final_output.languages)}")
```

### Exercise 2: Create a Recipe Analyzer

```python
from typing import List, Optional

class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str
    notes: Optional[str] = None

class NutritionInfo(BaseModel):
    calories_per_serving: Optional[int] = None
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty_level: str = Field(..., regex=r'^(easy|medium|hard)$')

class Recipe(BaseModel):
    title: str
    description: str
    servings: int
    ingredients: List[Ingredient]
    instructions: List[str]
    nutrition: NutritionInfo
    cuisine_type: str
    dietary_tags: List[str]  # vegetarian, vegan, gluten-free, etc.

# Create recipe analyzer
recipe_analyzer = Agent(
    name="RecipeAnalyzer",
    instructions="Extract detailed recipe information from recipe text.",
    output_type=Recipe
)

# Test with recipe
recipe_text = """
Spaghetti Carbonara
A classic Italian pasta dish with eggs, cheese, and pancetta.
Serves 4 people. Prep time: 15 minutes, Cook time: 20 minutes. Medium difficulty.

Ingredients:
- 400g spaghetti pasta
- 150g pancetta, diced
- 3 large eggs
- 100g Parmesan cheese, grated
- 2 cloves garlic, minced
- Black pepper to taste
- Salt for pasta water

Instructions:
1. Boil salted water and cook spaghetti according to package directions
2. Fry pancetta in a large pan until crispy
3. Beat eggs with Parmesan cheese in a bowl
4. Drain pasta and add to pancetta pan
5. Remove from heat and quickly mix in egg mixture
6. Serve immediately with extra Parmesan

Cuisine: Italian
Dietary notes: Contains gluten, dairy, and eggs
Approximate calories: 650 per serving
"""

result = Runner.run_sync(recipe_analyzer, recipe_text)

print("=== Recipe Analysis ===")
print(f"Title: {result.final_output.title}")
print(f"Description: {result.final_output.description}")
print(f"Servings: {result.final_output.servings}")
print(f"Cuisine: {result.final_output.cuisine_type}")
print(f"Difficulty: {result.final_output.nutrition.difficulty_level}")
print(f"Total Time: {result.final_output.nutrition.prep_time_minutes + result.final_output.nutrition.cook_time_minutes} minutes")

print("\nIngredients:")
for ing in result.final_output.ingredients:
    notes_str = f" ({ing.notes})" if ing.notes else ""
    print(f"  • {ing.amount} {ing.unit} {ing.name}{notes_str}")

print("\nInstructions:")
for i, step in enumerate(result.final_output.instructions, 1):
    print(f"  {i}. {step}")

print(f"\nDietary Tags: {', '.join(result.final_output.dietary_tags)}")
if result.final_output.nutrition.calories_per_serving:
    print(f"Calories per serving: {result.final_output.nutrition.calories_per_serving}")
```

---

*Remember: Structured output transforms your agent from giving messy text to providing perfect, usable data every time!* 📊✨
