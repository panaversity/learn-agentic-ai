# Module 08 – Evaluation-Driven Development (EDD)

> **The AI testing discipline: How to systematically test and optimize your AI prompts and models in agentic applications.**

## 🎯 **What EDD Actually Is**

**EDD is the AI-specific testing discipline that works alongside TDD:**

- **TDD**: Tests traditional code (functions, APIs, business logic)
- **EDD**: Tests AI components (prompts, models, agent behavior)

**EDD is NOT:**
- A replacement for TDD
- A single learning path
- A magic solution for all AI problems
- A replacement for good prompt engineering

## 🔄 **TDD vs EDD: Parallel Testing Disciplines**

### **TDD (Test-Driven Development)**
**For:** Traditional code and functions
**Tests:** Code logic, APIs, database operations, business logic
**Focus:** "Does my code work correctly?"

**Example:**
```python
def test_user_creation():
    user = create_user("john@example.com", "password123")
    assert user.email == "john@example.com"
    assert user.is_active == True
```

### **EDD (Evaluation-Driven Development)**
**For:** AI agents and LLM applications
**Tests:** Prompt quality, agent behavior, model performance, reasoning chains
**Focus:** "Does my AI agent work correctly?"

**Example:**
```python
def test_agent_response():
    response = agent.run("Help me book a flight")
    assert response.contains("flight")
    assert response.is_helpful()
    assert response.cost < 0.01
```

## 🤖 **For Agentic Applications, You Need Both**

**TDD for the "plumbing":**
- Database connections
- API integrations
- Business logic
- Error handling
- Authentication

**EDD for the "intelligence":**
- Agent prompts
- Reasoning chains
- Tool selection
- Conversation flow
- Model performance

## 🔄 **How EDD Fits in SDD Workflow**

**SDD → TDD → EDD → PHR**

**1. SDD Design**: Plan your AI agent's capabilities and user interactions
**2. TDD Implementation**: Build the traditional code that supports the agent
**3. EDD Implementation**: Build and test the AI components that make the agent intelligent
**4. PHR Learning**: Capture insights from both TDD and EDD

### **Why EDD Matters for Agentic Applications**

**Agentic applications are complex because:**
- Agents make multiple decisions in sequence
- Each decision depends on previous context
- Agent behavior is emergent and hard to predict
- Prompt quality directly determines agent performance

**EDD helps by:**
- Testing agent prompts systematically
- Comparing models for agent tasks
- Measuring agent performance with data
- Optimizing based on real results

## 🛠️ **How to Actually Do EDD**

### **The Simple Approach**

**1. Choose Your Evaluation Tool**
- PromptFoo (most popular)
- OpenAI Evals
- Custom evaluation scripts
- Manual testing

**2. Define What to Test**
- Core agent prompts
- Tool calling behavior
- Conversation flow
- Safety and boundaries

**3. Set Up Tests**
- Write test cases
- Define success criteria
- Choose models to compare
- Run evaluations

**4. Optimize Based on Results**
- Fix failing tests
- Improve prompts
- Choose better models
- Iterate and improve

### **Example: Testing an AI Tutor Agent**

```yaml
# Basic agent evaluation
prompts:
  - |
    You are an AI tutor. Help the student learn {{topic}}.
    Student: {{student_input}}
    
    Ask one helpful question.

providers:
  - openai:gpt-4.1-mini
  - openai:gpt-4.1

tests:
  - vars:
      topic: "machine learning"
      student_input: "I want to learn ML"
    assert:
      - type: contains
        value: "?"
      - type: llm-rubric
        value: "Asks a helpful learning question"
```

## 📁 **Organizing EDD for Agentic Applications**

### **Simple Directory Structure**

```
your-agent-project/
├── prompts/                 # Your agent prompts
│   ├── system_prompts/     # Main agent instructions
│   ├── tool_prompts/       # Tool calling prompts
│   └── conversation/       # Multi-turn conversation prompts
├── evaluations/            # EDD test files
│   ├── basic_tests.yaml   # Core functionality tests
│   ├── tool_tests.yaml    # Tool usage tests
│   └── safety_tests.yaml  # Safety and boundary tests
└── results/               # Evaluation results and reports
```

### **What to Test in Each Area**

**Core Agent Behavior:**
- Does the agent understand user intent?
- Does it respond appropriately?
- Does it maintain conversation context?

**Tool Integration:**
- Does the agent choose the right tools?
- Does it use tools correctly?
- Does it handle tool errors gracefully?

**Safety and Boundaries:**
- Does the agent refuse harmful requests?
- Does it stay within its defined role?
- Does it handle edge cases safely?

## 🔄 **EDD in Your SDD Workflow**

### **When to Use EDD**

**Use EDD when you have:**
- AI prompts that users interact with
- Multiple AI models to choose from
- Important AI responses that must be reliable
- Time to invest in making AI work better

### **How to Get Started**

**1. Start Simple**
```bash
# Install PromptFoo
npm install -g promptfoo

# Create your first test
cat > test.yaml << 'EOF'
prompts:
  - 'You are a helpful assistant. User: {{query}}'
providers:
  - openai:gpt-4.1-mini
tests:
  - vars:
      query: 'Hello'
    assert:
      - type: contains
        value: 'hello'
EOF

# Run the test
promptfoo eval -c test.yaml
```

**2. Test Your Agent Prompts**
- Test core agent behavior
- Test tool calling
- Test conversation flow
- Test safety and boundaries

**3. Compare Models**
- Test the same prompts across different models
- Compare cost, speed, and quality
- Choose the best model for your use case

**4. Iterate and Improve**
- Fix failing tests
- Improve prompts based on results
- Add more test cases
- Set up automated testing

### **The Key Principle**

**Test your AI prompts like you test your code.**

## 🎯 **Summary**

**EDD is the AI-specific testing discipline that works alongside TDD in agentic applications.**

**Key points:**
- TDD tests traditional code, EDD tests AI components
- Both are essential for reliable agentic applications
- Test your prompts like you test your code
- Compare different models for your use case
- Measure performance with real data
- Optimize based on results, not guesswork

**For agentic applications:**
- Use TDD for the "plumbing" (APIs, databases, business logic)
- Use EDD for the "intelligence" (prompts, models, agent behavior)
- Both disciplines work together in the SDD workflow

**The simple approach:**
1. Choose an evaluation tool (PromptFoo is popular)
2. Write test cases for your prompts
3. Run evaluations and analyze results
4. Fix problems and iterate

**Remember: TDD and EDD are parallel testing disciplines - you need both for agentic applications.**