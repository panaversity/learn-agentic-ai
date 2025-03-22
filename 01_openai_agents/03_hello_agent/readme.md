🚀 **[Open in Google Colab](https://colab.research.google.com/drive/1T3JPcpC7B7_ASDFLifLwwDH0Ikgc68Am?usp=sharing)**
# OpenAI Agents using Google Gemini Model

https://openai.github.io/openai-agents-python/

https://openai.github.io/openai-agents-python/models/

https://ai.google.dev/gemini-api/docs/openai


Create a .env file with your gemini key
    
    
    uv init hello_agent

    cd hello_agent

    uv add openai-agents python-dotenv

    uv run main.py

## How to configure LLM Providers (Other than OpenAI) at different levels (Global, Run and Agent)?

Agents SDK is setup to use OpenAI as default providers. When using other providers you can setup at different levels:

### 1. AGENT LEVEL

```python
import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

gemini_api_key = ""

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

async def main():
    # This agent will use the custom LLM provider
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    )

    result = await Runner.run(
        agent,
        "Tell me about recursion in programming.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. RUN LEVEL

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

gemini_api_key = ""

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

agent: Agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Hello, how are you.", run_config=config)

print(result.final_output)
```

### GLOBAL

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents import set_default_openai_client

gemini_api_key = ""

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(external_client)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

agent: Agent = Agent(name="Assistant", instructions="You are a helpful assistant", model=model)

result = Runner.run_sync(agent, "Hello, how are you.")

print(result.final_output)
```