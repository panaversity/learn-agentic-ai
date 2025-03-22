# LifeCycle

In general terms, a lifecycle refers to the complete sequence of stages that an object, process, or entity goes through from its creation to its termination. 

In the context of the OpenAI Agents SDK, it specifically describes the stages an agent experiences—from when it’s initialized (or activated) until it completes its task and produces an output. 

## Lifecycle events (hooks)
Sometimes, you want to observe the lifecycle of an agent. For example, you may want to log events, or pre-fetch data when certain events occur. You can hook into the agent lifecycle with the hooks property. Subclass the AgentHooks class, and override the methods you're interested in.

In the OpenAI Agents SDK, lifecycle management is provided at two levels:

1. **Run-Level Lifecycle (RunHooks):**  
   This manages global events that span the entire execution or "run" of one or more agents. It allows you to monitor and control overarching events such as the start and end of an agent's execution, tool invocations, and handoffs between agents.

2. **Agent-Level Lifecycle (AgentHooks):**  
   This focuses on the individual agent. It lets you inject custom logic right into the agent's specific workflow—tracking events such as when an agent starts processing, when it completes its task, and when it interacts with external tools.

These two layers allow for both a broad view of the system's execution (through RunHooks) and a detailed, fine-grained control of each agent's behavior (via AgentHooks). 


## Run LifeCycle in the OpenAI Agents SDK

In the SDK, the **run lifecycle** is managed through **RunHooks**. These hooks allow you to observe and control events that occur across the entire run of one or more agents. They include callbacks for when an agent starts or ends, when a tool is about to run, and when control is handed off between agents. You can add callbacks on these (lifecycle events)[https://openai.github.io/openai-agents-python/ref/lifecycle/#agents.lifecycle.RunHooks] in an agent run:

1. **on_agent_start async:** Called before the agent is invoked. Called each time the current agent changes.
2. **on_agent_end async:** Called when the agent produces a final output.
3. **on_handoff async:** Called when a handoff occurs.
4. **on_tool_start async:** Called before a tool is invoked.
5. **on_tool_end async:** Called after a tool is invoked.

### Basic Example

```python
# Imports
import asyncio
import random
from typing import Any
from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, Usage, AsyncOpenAI OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled

gemini_api_key = "..."

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

set_default_openai_client(external_client)
set_tracing_disabled(True)

class TestHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0
        self.name = "TestHooks"

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"### {self.name} {self.event_counter}: Agent {agent.name} started. Usage: {context.usage}")

start_hook = TestHooks()

start_agent = Agent(
    name="Content Moderator Agent",
    instructions="You are content moderation agent. Watch social media content received and flag queries that need help or answer. We will answer anything about AI?",
    model=model
)

async def main():
  result = await Runner.run(
      start_agent,
      hooks=start_hook,
      input=f"<tweet>Will Agentic AI Die at end of 2025?.</tweet>"
  )

  print(result.final_output)

asyncio.run(main())
```

#### Learning References
- https://openai.github.io/openai-agents-python/agents/#lifecycle-events-hooks
- https://openai.github.io/openai-agents-python/ref/run/#agents.run.Runner
- https://openai.github.io/openai-agents-python/ref/lifecycle/#agents.lifecycle.RunHooks
- https://openai.github.io/openai-agents-python/ref/lifecycle/#agents.lifecycle.AgentHooks