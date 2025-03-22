# Context Management

Context management in the OpenAI Agents SDK refers to handling additional data that your code can use during an agent’s execution. This “context” comes in two main forms:

[Learning Reference](https://openai.github.io/openai-agents-python/context/)

### 1. Local Context

**What It Is:**  
Local context is any data or dependencies you pass to your agent's run that your code (tools, lifecycle hooks, etc.) can use. It’s entirely internal and never sent to the LLM.

**How It Works:**  
- **Creating Context:**  
  You create a Python object—often using a dataclass or a Pydantic model—to encapsulate data like a username, user ID, logger, or helper functions.
  
- **Passing Context:**  
  You pass this object to the run method (e.g., `Runner.run(..., context=your_context)`). The SDK wraps your object in a `RunContextWrapper`, making it available to every tool function, lifecycle hook, or callback during that run via `wrapper.context`.

- **Key Point:**  
  All parts of a single agent run must share the same type of context, ensuring consistency.

**Example Use Cases:**  
- Storing user details (e.g., a username or ID) that your tools might need.
- Injecting dependencies such as loggers or data fetchers.
- Providing helper functions accessible throughout the run.

*Note:* This local context is not exposed to the LLM. It’s solely for your backend logic and operations.

---

### 2. Agent/LLM Context

**What It Is:**  
Agent/LLM context refers to the information the LLM sees when it generates responses. This is essentially the conversation history or messages (like system prompts, instructions, and user inputs) that guide its output.

**How to Use It:**  
- **Embedding in Instructions:**  
  Include important context (like the user’s name, current date, or specific guidelines) directly in the agent’s instructions or system prompts.
  
- **Passing in Inputs:**  
  You can also add context to the input message when calling `Runner.run()`, ensuring that this data is part of the conversation that the LLM processes.
  
- **Function Tools:**  
  The LLM may also invoke function tools to fetch on-demand data that wasn’t initially part of its conversation history.
  
- **Retrieval/Web Search:**  
  Use specialized tools to pull in relevant external data, thereby grounding the LLM’s responses in up-to-date or detailed information.

**Key Difference:**  
While the local context is internal and never sent to the LLM, the agent/LLM context is deliberately exposed as part of the conversation to influence and guide the LLM’s response generation.

---

### Code Example Breakdown

Consider the following simplified example that demonstrates local context management:

```python
import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool

# Define a simple context using a dataclass
@dataclass
class UserInfo:  
    name: str
    uid: int

# A tool function that accesses local context via the wrapper
@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:  
    return f"User {wrapper.context.name} is 47 years old"

async def main():
    # Create your context object
    user_info = UserInfo(name="John", uid=123)  

    # Define an agent that will use the tool above
    agent = Agent[UserInfo](  
        name="Assistant",
        tools=[fetch_user_age],
    )

    # Run the agent, passing in the local context
    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
    )

    print(result.final_output)  # Expected output: The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())
```

**Explanation of the Example:**

1. **Creating Local Context:**  
   A `UserInfo` dataclass is defined to hold user-specific data.

2. **Passing Context:**  
   An instance of `UserInfo` is created and passed as the context when running the agent.

3. **Accessing Context in a Tool:**  
   The `fetch_user_age` function uses the `RunContextWrapper` to access the `UserInfo` data and generate a response based on that context.

4. **Local vs. LLM Context:**  
   - **Local Context:** Here, the `UserInfo` object is used by the tool function; it’s internal and not shown to the LLM.
   - **Agent/LLM Context:** If you wanted the LLM to consider additional details (e.g., instructions including the user’s name), you’d incorporate that information into the agent’s instructions or conversation history.