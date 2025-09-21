# The Definitive Guide to Evaluation-Driven Development (EDD)

**[Must Read: From TDD to EDD: Why Evaluation-Driven Development Is the Future of AI Engineering](https://medium.com/@nimrodbusany_9074/from-tdd-to-edd-why-evaluation-driven-development-is-the-future-of-ai-engineering-a5e5796b2af4)**

# What we’d recommend for EDD (our stack)

1. **Use [promptfoo](https://www.promptfoo.dev/) for day-to-day EDD gates** (on every PR): run matrix tests across prompts/models, post pass/fail & diffs on PRs.
2. **Add [OpenAI Evals](https://github.com/openai/evals) for deeper, model-graded checks** on golden sets (faithfulness, task success) and optionally call the **Evaluation API** as part of nightly jobs or release candidates.

Here is a detailed, step-by-step tutorial for implementing Evaluation-Driven Development (EDD). This guide is designed to slot directly into your AI-First Engineering Playbook, enhancing it with a robust layer of behavioral quality assurance.


**A tutorial for guaranteeing AI agent quality and preventing behavioral regressions.**

Welcome to the next evolution of your AI engineering practice. You have mastered Test-Driven Development (TDD) to ensure your code is functionally correct—the engine runs, the wheels turn. But in the world of AI agents, that's only half the battle. **Evaluation-Driven Development (EDD) is the driving test.** It puts your agent on a simulated road with real-world challenges to ensure its *behavior* is safe, reliable, and aligned with its purpose.

This tutorial will show you, with many examples, how to weave EDD into your daily workflow.

### The Core Philosophy: Behavior First

The fundamental shift with EDD is this:

  * **TDD asks:** "Does my code execute correctly?" (e.g., Does the `get_runner()` function return a valid agent runner?)
  * **EDD asks:** "Does my agent behave correctly?" (e.g., Does the agent *actually use* the tool to calculate a tip when asked?)

You will now design and test the desired *behavior* first, and then use TDD to implement the code that supports it.

-----

### Part 1: Setting Up Your EDD Environment

First, let's get the tools ready. This is a one-time setup per project. We'll use `promptfoo`, a powerful open-source framework for testing and evaluating LLM outputs.

**Step 1: Install `promptfoo`**
Open your terminal and install it globally. It's a command-line tool that makes running evaluations simple.

```bash
npm install -g promptfoo
```

**Step 2: Initialize in Your Project**
Navigate to the root of your agent repository and run the init command.

```bash
promptfoo init
```

This command will create two essential things:

1.  **`promptfoo.config.yaml`:** The main configuration file. This is where you tell `promptfoo` how to test your agent.
2.  **An `evals/` directory:** A new folder, sitting right next to your `tests/` directory, which will hold all your behavioral test cases.

**Step 3: Configure `promptfoo` to Test Your FastAPI Agent**
Open `promptfoo.config.yaml` and configure it to send prompts to your locally running FastAPI service.

```yaml
# promptfoo.config.yaml

prompts:
  # This tells promptfoo to read prompts from your eval files, not here.
  - file://evals/*.yaml

providers:
  # This defines HOW to test your agent. We'll define one provider: your local API.
  - id: 'api:fastapi-agent'
    config:
      # The command to start your local server. Promptfoo will run this for you!
      command: 'uvicorn app.main:app --port 8000'
      # The URL of your chat endpoint.
      url: 'http://localhost:8000/chat'
      method: 'POST'
      headers:
        Content-Type: 'application/json'
      # Defines how to format the request body. {{prompt}} is the variable for the user's message.
      body: |
        {
          "session_id": "eval-session-{{ N }}",
          "user_message": "{{prompt}}"
        }
      # Defines how to extract the agent's reply from the JSON response.
      response: '{{ output.text }}'

# Default assertion rules can go here, but we'll define them in our eval files.
# tests: []
```

Your environment is now ready.

-----

### Part 2: The EDD Development Loop in Action

Let's build a new feature using the enhanced PDD x EDD x TDD loop.

**Scenario:** We are building a **Travel Agent Bot**. The first feature is to correctly identify when a user wants to book a flight and respond with a confirmation, even though the actual flight booking tool doesn't exist yet.

#### Step 1: RED (Write a Failing Behavioral Eval)

Before writing any code or prompts, define the desired behavior. Create a new file: `evals/flight_booking_intent.yaml`.

```yaml
# evals/flight_booking_intent.yaml

tests:
  - name: "Identifies explicit flight booking request"
    description: "When the user explicitly asks to book a flight, the agent should confirm the intent."
    # The prompt we will send to the agent
    vars:
      prompt: "Hi, I'd like to book a flight from Karachi to Lahore for next Tuesday."
    # The assertions that define "good behavior"
    assert:
      - type: "contains"
        value: "Okay, I can help you with booking a flight."
      - type: "not-contains"
        value: "I cannot book flights." # Make sure it doesn't give a wrong refusal.

  - name: "Ignores requests for hotel bookings"
    description: "When the user asks for a hotel, the agent should state that it's out of scope."
    vars:
      prompt: "Can you help me find a hotel in Islamabad?"
    assert:
      - type: "contains"
        value: "I can only assist with flight bookings at the moment."
```

Now, run the evaluation. Since we haven't taught our agent this logic yet, **it will fail.**

```bash
promptfoo eval

# Expected Output:
# Результаты
# ╔════════════════════════════════════════════╤═══════╗
# ║ ✓ Identifies explicit flight booking request │ FAIL  ║
# ╟────────────────────────────────────────┼───────╢
# ║ ✓ Ignores requests for hotel bookings      │ FAIL  ║
# ╚════════════════════════════════════════════╧═══════╝
```

**You are now in a "RED" state for behavior.**

#### Step 2: GREEN (Write a Prompt to Pass the Eval)

Now, open your agent's instruction file (e.g., `app/agents/customer.py`). Your goal is to write the simplest prompt possible to make the failing evals pass.

**Use Cursor/Your IDE (This is your PDD step):**

> "Update the agent's instructions. The agent is a travel assistant specializing *only* in booking flights. If a user asks to book a flight, confirm that you can help. If they ask for anything else, like hotels or rental cars, politely state that you can only handle flights."

The AI generates the updated instructions:

```python
# app/agents/customer.py

INSTRUCTIONS = """
You are a friendly and helpful travel assistant. Your primary and ONLY capability is to help users book flights.

When a user asks to book a flight, your first step is to confirm their request. For example, say: "Okay, I can help you with booking a flight."

If the user asks for anything other than flights (e.g., hotels, rental cars, tourist attractions), you MUST politely decline and state your specialization. For example, say: "I can only assist with flight bookings at the moment."
"""
```

#### Step 3: VERIFY (Run the Evals Again)

Now that you've updated the agent's core logic (its prompt), run the evaluation again.

```bash
promptfoo eval

# Expected Output:
# Результаты
# ╔════════════════════════════════════════════╤═══════╗
# ║ ✓ Identifies explicit flight booking request │ PASS  ║
# ╟────────────────────────────────────────┼───────╢
# ║ ✓ Ignores requests for hotel bookings      │ PASS  ║
# ╚════════════════════════════════════════════╧═══════╝
```

**Congratulations\! You are now in a "GREEN" state for behavior.** The agent *behaves* correctly, even though the backend tools aren't built yet.

#### Step 4: IMPLEMENT (Use TDD for the Code)

Now that the agent's behavior is locked in by the EDD tests, you can proceed with your familiar TDD loop to build the actual `book_flight` tool and the API logic, confident that the agent knows when and how to use it.

-----

### Part 3: Advanced EDD Techniques (Improving Further)

Basic EDD is powerful, but you can make it even more robust.

#### Technique 1: Using AI to Generate Your Test Cases

Struggling to think of edge cases? Use an AI to help.

**The Prompt (to ChatGPT, Cursor, etc.):**

> "I am building an evaluation set for a travel agent bot. The bot's only capability is booking flights. Generate 15 diverse test prompts for me in YAML format. Include tricky edge cases like ambiguous requests, requests with missing information, and users trying to trick the bot. For each, specify the expected behavior (e.g., 'should ask for clarification' or 'should politely decline')."

This technique helps you build a comprehensive test suite much faster.

#### Technique 2: Semantic Similarity Assertions (Beyond `contains`)

Sometimes, the exact wording doesn't matter, but the *meaning* does.

  * **Problem:** Your eval asserts `contains: "Okay, I can help"`. But what if the agent says, `"Certainly, I can assist with that"`? Your test would fail, even though the behavior is correct.
  * **Solution:** Use a semantic similarity check.

<!-- end list -->

```yaml
# evals/flight_booking_intent.yaml

tests:
  - name: "Identifies explicit flight booking request"
    vars:
      prompt: "Hi, I'd like to book a flight from Karachi to Lahore for next Tuesday."
    assert:
      - type: "similar" # Checks for semantic similarity, not exact words
        value: "Okay, I can help you book a flight"
        threshold: 0.85 # On a scale of 0 to 1, how similar the meaning must be
```

This makes your tests far more resilient to minor, harmless changes in the agent's wording.

#### Technique 3: Scaling Your Evals with Test Providers

If you have hundreds of test cases, putting them all in one YAML file is messy. You can separate your data from your tests.

**Step A:** Create a CSV file with your test data: `evals/flight_scenarios.csv`

```csv
user_prompt,expected_outcome
"Book a flight to Dubai",flight_intent
"Find me a cheap hotel",out_of_scope
"What's the weather like in Hunza?",out_of_scope
"I need a ticket to Islamabad for tomorrow",flight_intent
```

**Step B:** Update your `promptfoo.config.yaml` to use this file as a "provider".

```yaml
# promptfoo.config.yaml

providers:
  # ... (your FastAPI provider)

# NEW SECTION
testProviders:
  - id: 'file:evals/flight_scenarios.csv'

# Define one set of tests that runs against all the data
tests:
  - vars:
      # This variable will be filled by the 'expected_outcome' column in the CSV
      expected: '{{expected_outcome}}'
    assert:
      # A custom script that checks if the agent's response matches the expected outcome
      - type: 'javascript'
        value: 'output.includes(expected)'
```

This is a highly scalable way to manage large sets of behavioral tests.

By embracing EDD, you are adding the most critical layer of quality control for AI systems. You are ensuring that what you build is not just functionally sound, but behaviorally reliable, safe, and trustworthy.