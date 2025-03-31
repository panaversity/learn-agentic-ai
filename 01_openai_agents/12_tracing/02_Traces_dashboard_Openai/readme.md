[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DtqniWGb7XLFctKZ114nt1C-qB4EFlQr?usp=sharing)


# OpenAI Traces Dashboard

This folder contains examples demonstrating the use of OpenAI's Traces Dashboard for monitoring and analyzing LLM applications.

## Official Resources
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/tracing/)
- [OpenAI Traces Dashboard](https://platform.openai.com/traces)

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
