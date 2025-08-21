# AI Agent Guardrails: 

## What Are Guardrails? 🛡️

Think of guardrails like the safety barriers on a mountain highway. Just as physical guardrails prevent cars from going off dangerous cliffs, **AI guardrails prevent your agents from doing things they shouldn't do** or producing outputs that could be harmful, inappropriate, or costly.

### Real-World Analogy: The Restaurant Bouncer 🚪

Imagine you're running a fancy restaurant with an expensive chef (your AI agent). You don't want just anyone walking in and wasting the chef's time with inappropriate requests. So you hire two bouncers:

- **Input Bouncer (Input Guardrail)**: Checks customers at the door before they enter
- **Output Bouncer (Output Guardrail)**: Reviews what the chef sends out before it reaches the customer

If either bouncer spots a problem, they can immediately stop the process and handle the situation appropriately.

## Why Do We Need Guardrails? 💰

### The Cost Problem
Modern AI agents often use expensive, powerful models. Without guardrails:
- Malicious users could waste your resources
- Inappropriate requests could trigger costly operations
- Your agent might generate harmful or off-brand content

### The Safety Problem
AI agents can sometimes:
- Generate inappropriate content
- Leak sensitive information
- Provide harmful instructions
- Go off-topic from their intended purpose

## Types of Guardrails

### 1. Input Guardrails (The Front Door Security) 🚨

**What they do**: Check user input BEFORE your main agent processes it

**When they run**: Only when the agent is the first agent in your pipeline

**Example scenarios**:
- Blocking offensive language
- Detecting attempts to make the agent do homework
- Preventing requests outside the agent's intended scope
- Filtering out potential security threats

### 2. Output Guardrails (The Quality Control Inspector) ✅

**What they do**: Check the agent's response BEFORE sending it to the user

**When they run**: Only when the agent is the last agent in your pipeline

**Example scenarios**:
- Ensuring responses don't contain sensitive information
- Checking for appropriate tone and content
- Validating that outputs meet quality standards
- Preventing mathematical errors in non-math contexts

## How Guardrails Work: The Three-Step Process

### Input Guardrails Process:
1. **Receive**: Gets the same input that would go to your main agent
2. **Analyze**: Guardrail function evaluates the input and returns a result
3. **Decide**: If `tripwire_triggered` is `True`, raises an exception and stops execution

### Output Guardrails Process:
1. **Receive**: Gets the output produced by your main agent
2. **Analyze**: Guardrail function evaluates the output and returns a result
3. **Decide**: If `tripwire_triggered` is `True`, raises an exception and prevents delivery

## Practical Example 1: Math Homework Detection (Input Guardrail)

### The Scenario
You have a customer support agent that uses an expensive AI model. You don't want students using it to cheat on homework.

### The Solution
```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

# Define what our guardrail should output
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

# Create a simple, fast agent to do the checking
guardrail_agent = Agent( 
    name="Homework Police",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

# Create our guardrail function
@input_guardrail
async def math_guardrail( 
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    # Run our checking agent
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    
    # Return the result with tripwire status
    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_math_homework,  # Trigger if homework detected
    )

# Main agent with guardrail attached
customer_support_agent = Agent(  
    name="Customer Support Specialist",
    instructions="You are a helpful customer support agent for our software company.",
    input_guardrails=[math_guardrail],  # Attach our guardrail
)

# Testing the guardrail
async def test_homework_detection():
    try:
        # This should trigger the guardrail
        await Runner.run(customer_support_agent, "Can you solve 2x + 3 = 11 for x?")
        print("❌ Guardrail failed - homework request got through!")
    
    except InputGuardrailTripwireTriggered:
        print("✅ Success! Homework request was blocked.")
        # Handle appropriately - maybe send a polite rejection message
```

### What Happens Here:
1. User asks: "Can you solve 2x + 3 = 11 for x?"
2. Input guardrail intercepts this request
3. Fast guardrail agent analyzes: "This is math homework"
4. `tripwire_triggered` becomes `True`
5. Exception is raised, expensive main agent never runs
6. You save money and maintain appropriate usage

## Practical Example 2: Sensitive Information Detection (Output Guardrail)

### The Scenario
Your customer support agent sometimes accidentally includes internal information or personal data in responses.

### The Solution
```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

class MessageOutput(BaseModel): 
    response: str

class SensitivityCheck(BaseModel): 
    contains_sensitive_info: bool
    reasoning: str
    confidence_level: int  # 1-10 scale

# Fast guardrail agent for checking outputs
sensitivity_guardrail_agent = Agent(
    name="Privacy Guardian",
    instructions="""
    Check if the response contains:
    - Personal information (SSN, addresses, phone numbers)
    - Internal company information
    - Confidential data
    - Inappropriate personal details
    
    Be thorough but not overly sensitive to normal business information.
    """,
    output_type=SensitivityCheck,
)

@output_guardrail
async def privacy_guardrail(  
    ctx: RunContextWrapper, 
    agent: Agent, 
    output: MessageOutput
) -> GuardrailFunctionOutput:
    # Check the agent's response for sensitive content
    result = await Runner.run(
        sensitivity_guardrail_agent, 
        f"Please analyze this customer service response: {output.response}", 
        context=ctx.context
    )
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_sensitive_info,
    )

# Main customer support agent with output guardrail
support_agent = Agent( 
    name="Customer Support Agent",
    instructions="Help customers with their questions. Be friendly and informative.",
    output_guardrails=[privacy_guardrail],  # Add our privacy check
    output_type=MessageOutput,
)

async def test_privacy_protection():
    try:
        # This might generate a response with sensitive info
        result = await Runner.run(
            support_agent, 
            "What's my account status for john.doe@email.com?"
        )
        print(f"✅ Response approved: {result.final_output.response}")
    
    except OutputGuardrailTripwireTriggered as e:
        print("🛑 Response blocked - contained sensitive information!")
        # Send a generic response instead
        fallback_message = "I apologize, but I need to verify your identity before sharing account details."
```

## Advanced Guardrail Strategies

### 1. Cascading Guardrails
Use multiple guardrails in sequence:
```python
agent = Agent(
    name="Multi-Protected Agent",
    input_guardrails=[
        profanity_filter,      # Check for bad language
        topic_validator,       # Ensure on-topic
        rate_limiter,         # Prevent spam
    ],
    output_guardrails=[
        privacy_checker,       # Remove sensitive info
        quality_validator,     # Ensure good responses
        brand_compliance,      # Match company tone
    ]
)
```

### 2. Context-Aware Guardrails
Make guardrails smarter by considering context:
```python
@input_guardrail
async def context_aware_guardrail(ctx, agent, input):
    # Consider user history, time of day, agent purpose, etc.
    user_context = ctx.context.get('user_history', {})
    
    if user_context.get('suspicious_activity', False):
        # Apply stricter checking for flagged users
        pass
```

## Best Practices for Implementing Guardrails

### 1. Keep Guardrails Fast and Cheap ⚡
- Use smaller, faster models for guardrails
- Cache common guardrail results when possible
- Keep guardrail logic simple and focused

### 2. Design Clear Tripwire Logic 🎯
```python
# Good: Clear, specific conditions
tripwire_triggered = (
    result.confidence > 0.8 and 
    result.contains_math and 
    result.looks_like_homework
)

# Bad: Vague or overly complex conditions
tripwire_triggered = result.maybe_bad_somehow
```

### 3. Handle Exceptions Gracefully 🤝
```python
try:
    result = await Runner.run(agent, user_input)
except InputGuardrailTripwireTriggered:
    # Provide helpful feedback to user
    return "I'm designed to help with customer support. For homework help, try Khan Academy!"
except OutputGuardrailTripwireTriggered:
    # Provide safe fallback response
    return "I apologize, but I need to review my response. Please try rephrasing your question."
```

### 4. Monitor and Iterate 📊
- Log guardrail triggers to understand patterns
- Regularly review false positives and negatives
- Adjust guardrail sensitivity based on real usage

## Common Pitfalls to Avoid ⚠️

### 1. Overly Restrictive Guardrails
- Don't make guardrails so strict they block legitimate use cases
- Test with real user scenarios

### 2. Expensive Guardrails
- Remember: guardrails should be cheaper than your main agent
- Avoid using the same expensive model for both guardrail and main logic

### 3. Ignoring Edge Cases
- Consider unusual inputs and outputs
- Plan for partial matches and ambiguous cases

### 4. Poor Error Handling
- Always provide meaningful feedback when guardrails trigger
- Don't leave users confused about why their request was blocked


## 4. Discussion Questions
- "What could go wrong without guardrails?"
- "When might a guardrail be too restrictive?"
- "How do you balance safety with functionality?"

## Conclusion

Guardrails are essential safety and cost-control mechanisms for AI agents. They act as intelligent filters that protect both your resources and your users by catching problematic inputs and outputs before they cause issues.

Key takeaways:
- **Input guardrails** = Doorman checking who comes in
- **Output guardrails** = Quality inspector checking what goes out
- Keep them fast, focused, and cost-effective
- Handle exceptions gracefully with helpful user feedback
- Monitor and iterate based on real usage patterns

Remember: Good guardrails are invisible to legitimate users but essential for maintaining a safe, cost-effective, and reliable AI system.