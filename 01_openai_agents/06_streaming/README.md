
🚀 **[Open in Google Colab](https://colab.research.google.com/drive/1gmj2g515XHCKMhXRc58vBU6Rc9x5xykd?usp=sharing)**<br>
🚀 **[Open in Colab - gemini](https://colab.research.google.com/drive/13qluzlzZ4Vko2F5ZGKt1lEIEvQjzlTjQ?usp=sharing)** 
# Streamed Agent Output Examples

This README demonstrates how to implement and interpret streamed output from agents using Python's asynchronous features and the hypothetical `agents` library.

## Example 1: Streamed Agent with Tool Calls

This example shows how an agent utilizes asynchronous tools to perform tasks dynamically.

### Code Overview
- **Agent**: Defined with specific instructions and tools.
- **Tool**: `how_many_jokes`, returns a random integer determining the number of jokes.
- **Runner**: Executes agent actions asynchronously and streams events.

## Usage
```python
import asyncio
import random
from agents import Runner, ItemHelpers

async def main():
    agent = Agent(
        instructions="You are a helpful assistant. First, determine how many jokes to tell, then provide jokes.",
        tools=[how_many_jokes],
    )

    result = Runner.run_streamed(agent, input="Hello")

    async for event in result.stream_events():
        if event.item.type == "tool_call_output_item":
            print(f"Tool output: {event.item.output}")
        elif event.item.type == "message_output_item":
            print(ItemHelpers.text_message_output(event.item))

asyncio.run(main())
```

## Expected Output Example
```
=== Run starting ===
-- Tool output: 4
-- Message output:
 Sure, here are four jokes for you:

1. **Why don't skeletons fight each other?**
   They don't have the guts!

2. **What do you call fake spaghetti?**
   An impasta!

3. **Why did the scarecrow win an award?**
   Because he was outstanding in his field!

4. **Why can't you give Elsa a balloon?**
   Because she will let it go!

```

# Explanation of Events
- **tool_call_output_item**: Shows the tool's returned data.
- **message_output_item**: Contains the generated messages by the agent.

## Example 2: Raw Response Event Handling

```python
from agents import Agent, Runner
import asyncio

async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")

    async for event in result.stream_events():
        if event.item.type == "message_output_item":
            print(ItemHelpers.text_message_output(event.item))

asyncio.run(main())
```

## Key Concepts
- **Streaming Output**: Real-time responses from asynchronous agent executions.
- **Event Handling**: Filtering and processing streamed events for specific outputs.
- **Agent Tools**: Modular functions called by agents during tasks.

## Best Practices
- Clearly separate logic for handling different event types.
- Ensure asynchronous methods (`async`/`await`) are used properly.
- Provide user-friendly outputs by ignoring non-relevant event types (e.g., raw event deltas).

This guide will help developers efficiently implement and interpret asynchronous, streaming AI agents for various applications.

