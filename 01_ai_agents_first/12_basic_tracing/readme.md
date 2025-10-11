[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DtqniWGb7XLFctKZ114nt1C-qB4EFlQr?usp=sharing)

# OpenAI Traces Dashboard

This folder contains examples demonstrating the use of OpenAI's Traces Dashboard for monitoring and analyzing LLM applications.

## Official Resources
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/tracing/)
- [OpenAI Traces Dashboard](https://platform.openai.com/traces)

## Part 1: Understanding Observability (Seeing What Your App Does)

### What is Observability?

**Simple Definition:** Observability means being able to see and understand what your AI application is doing when it runs.

Think of it like this: If your AI application were a person doing a job, observability would be like having a security camera that records everything they do. You can go back and watch to see what happened.

### Why Do We Need Observability?

When you ask an AI application a question, many things happen behind the scenes:

- The application receives your question
- It might call an AI model
- It might search through documents
- It might use tools or functions
- Finally, it gives you an answer

Without observability, you're flying blind. You only see the final answer, but not how the application got there.

---

## Step 1: Understanding Basic Building Blocks

### What is a Run?

A **run** is a single action or step your application takes.

**Example:** Imagine making a sandwich:

- Taking out bread = 1 run
- Spreading butter = 1 run
- Adding cheese = 1 run
- Putting bread slices together = 1 run

Each of these individual actions is a "run."

In AI applications:

- Calling an AI model = 1 run
- Searching documents = 1 run
- Formatting a prompt = 1 run

**Key Point:** A run represents the smallest unit of work in your application.

---

### What is a Trace?

A **trace** is the complete story of everything that happened from start to finish.

**Using Our Sandwich Example:**

- The entire process of making the sandwich (all 4 steps together) = 1 trace
- Each individual step = 1 run within that trace

In AI applications:

- User asks a question → Application searches documents → Calls AI model → Returns answer
- This entire sequence = 1 trace
- Each arrow represents a run within that trace

**Key Point:** A trace is a collection of runs that shows the complete journey from input to output.

---

## Part 2: Basic Tracing with OpenAI Platform

## Features
- Real-time monitoring of LLM calls
- Performance analytics
- Cost tracking
- Error analysis
- Request/response visualization

## Setup Requirements
- OpenAI API key
- OpenAI Agents SDK installed
- Python environment with async support

## Example Structure
This folder will contain examples showing:
1. Basic tracing setup
2. Custom trace attributes
3. Performance monitoring
4. Error tracking
5. Cost analysis

## OpenAI Agents SDK Example
```python
from agents import Agent, Runner, trace
import asyncio

from agents import Agent, Runner, trace

async def main():
    agent = Agent(name="Joke generator", instructions="Tell funny jokes.")

    with trace("Joke workflow"): 
        first_result = await Runner.run(agent, "Tell me a joke")
        second_result = await Runner.run(agent, f"Rate this joke: {first_result.final_output}")
        print(f"Joke: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")

asyncio.run(main())
``` 
## Output

```python
Joke: Why don't scientists trust atoms?

Because they make up everything!
Rating: That's a classic! I'd give it a solid 8 out of 10. It's a clever play on words and has that nerdy charm.

```
## Openai Tracing Dashboard
https://platform.openai.com/traces

[](https://github.com/panaversity/learn-agentic-ai/blob/main/01_openai_agents/12_tracing/02_Traces_dashboard_Openai/openai-tracing.gif?raw=true)
<img src="https://github.com/panaversity/learn-agentic-ai/blob/main/01_openai_agents/12_tracing/02_Traces_dashboard_Openai/openai-tracing.gif?raw=true">
