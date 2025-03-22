# As Tool

https://openai.github.io/openai-agents-python/ref/agent/#agents.agent.Agent.as_tool

Interestingly, you can turn other agents into tools. This allows one agent to call another for assistance without fully handing off control. The orchestrator agent uses the other agents as a tool, depending on the user’s request, while retaining oversight.

The `as_tool` method in OpenAI's Agents SDK allows you to transform an `Agent` instance into a callable tool that other agents can utilize. This feature facilitates the creation of modular and interactive AI systems where agents can delegate tasks among themselves.

This is different from handoffs in two ways: 
1. In handoffs, the new agent receives the conversation history. In this tool, the new agent receives generated input. 
2. In handoffs, the new agent takes over the conversation. In this tool, the new agent is called as a tool, and the conversation is continued by the original agent.

**Key Concepts:**

- **Agents:** Autonomous entities equipped with instructions and tools to perform specific tasks.

- **Tools:** Functions or capabilities that agents can invoke to accomplish tasks.

- **Handoffs:** Mechanisms enabling agents to delegate tasks to other agents.

**Using the `as_tool` Method:**

To utilize the `as_tool` method, you can follow these steps:

1. **Define Individual Agents:**

   Create agents with specific roles and instructions.

   ```python
   from agents import Agent, Runner

   # Define a shopping assistant agent
   shopping_agent = Agent(
       name="Shopping Assistant",
       instructions="You assist users in finding products and making purchase decisions."
   )

   # Define a support agent
   support_agent = Agent(
       name="Support Agent",
       instructions="You help users with post-purchase support and returns."
   )
   ```


2. **Convert Agents into Tools:**

   Use the `as_tool` method to make each agent callable by other agents.

   ```python
   # Convert agents into tools
   shopping_tool = shopping_agent.as_tool()
   support_tool = support_agent.as_tool()
   ```


3. **Create a Triage Agent:**

   Develop an agent responsible for routing user queries to the appropriate agent tool.

   ```python
   # Define a triage agent that delegates tasks
   triage_agent = Agent(
       name="Triage Agent",
       instructions="You route user queries to the appropriate department.",
       tools=[shopping_tool, support_tool]
   )
   ```


4. **Run the Triage Agent:**

   Execute the triage agent with a user query to see it in action.

   ```python
   # Run the triage agent with a sample input
   result = Runner.run_sync(triage_agent, "I need help with a recent purchase.")
   print(result.final_output)
   ```


**Complete Example:**

Combining the steps above, here's a full example:

```python
from agents import Agent, Runner

# Define individual agents
shopping_agent = Agent(
    name="Shopping Assistant",
    instructions="You assist users in finding products and making purchase decisions."
)

support_agent = Agent(
    name="Support Agent",
    instructions="You help users with post-purchase support and returns."
)

# Convert agents into tools
shopping_tool = shopping_agent.as_tool()
support_tool = support_agent.as_tool()

# Define a triage agent that delegates tasks
triage_agent = Agent(
    name="Triage Agent",
    instructions="You route user queries to the appropriate department.",
    tools=[shopping_tool, support_tool]
)

# Run the triage agent with a sample input
result = Runner.run_sync(triage_agent, "I need help with a recent purchase.")
print(result.final_output)
```


In this setup, the triage agent evaluates the user's input and delegates the task to the appropriate agent (either the shopping assistant or the support agent) using the tools created by the `as_tool` method.

**Benefits of Using `as_tool`:**

- **Modularity:** Encourages a modular design where agents have distinct responsibilities, enhancing code maintainability.

- **Scalability:** Simplifies the process of adding new capabilities by introducing new agents without altering existing structures.

- **Interoperability:** Facilitates seamless interaction between agents, enabling complex workflows and task delegation.



By leveraging the `as_tool` method, you can build sophisticated AI systems where agents collaborate effectively to handle diverse tasks.


## Handoff vs As Tool

The key difference here revolves around *what context* is passed to the new agent and *how control of the conversation flows* between agents. Let’s break down each point:

---

### 1. Context Passed to the New Agent

- **Handoffs:**  
  When an agent uses a handoff, the new (receiving) agent is given the entire conversation history. This means that it gets every message—user input, previous responses, tool calls, and any context that has been built up so far. This comprehensive context allows the new agent to fully understand the background, nuances, and prior decisions of the conversation. It’s as if the conversation “moves” entirely over to the new agent, which can then generate responses based on all of the earlier dialogue.

- **Tool-based Calls (using `as_tool`):**  
  In contrast, when an agent is invoked as a tool (using the `as_tool` method), it does not receive the whole conversation history. Instead, it gets a piece of generated input from the original agent—often a specific string or a data payload that was produced during the conversation. The new agent (now acting as a tool) only processes this discrete input. This design is useful when the new agent’s functionality is meant to handle a specific task or computation without needing the full background, thereby keeping the interface simpler and more focused.

---

### 2. Flow of Conversation Control

- **Handoffs:**  
  In a handoff, the new agent “takes over” the conversation. Because it receives the full history, it continues the interaction as if it were the main agent, making decisions, asking follow-up questions, or generating responses based solely on the transferred dialogue. Essentially, the conversational control is completely passed to the new agent, which now becomes responsible for driving the dialogue forward.

- **Tool-based Calls (using `as_tool`):**  
  When an agent is used as a tool, it is invoked by the original agent to perform a specific function (for example, processing data or executing a sub-task). After the tool (the new agent) completes its job and returns its output, the original agent resumes the conversation. The original agent integrates the tool’s result into the ongoing dialogue, which means it maintains overall control of the conversation flow. This approach allows for modularity—different agents can be “plugged in” to perform functions without completely transferring the conversational context or control.

---

### Why This Distinction Matters

- **Modularity and Reusability:**  
  Using the tool method (via `as_tool`) is ideal for building systems where you want to keep the conversation centralized. The original agent can call upon various specialized sub-agents (tools) for tasks like calculations, look-ups, or processing requests, then stitch their outputs back into a coherent conversation. This leads to a highly modular design where each agent can be developed and maintained independently while still contributing to a unified interaction.

- **Context-Rich Delegation:**  
  Handoffs, on the other hand, are best suited for scenarios where the new agent must have a complete understanding of the conversation to address complex or nuanced issues. This might be important in customer support or when the conversation’s history carries essential details that affect subsequent responses.

---

### An Analogy

Imagine you’re at a restaurant:
- **Handoff:** If you ask the host to call the chef over because your dish needs a complete rework, the chef comes over with full knowledge of everything that’s happened (the conversation history, complaints, previous interactions) and takes over your service.
- **Tool Call:** Instead, if you ask the waiter to bring a side dish, the waiter simply takes your specific request (the generated input) and returns with the dish. You, as the diner, still engage directly with the waiter, who integrates that dish into your meal.

---

### In Summary

- **Handoffs** involve a full transfer of context and control to the new agent, making it responsible for the conversation from that point onward.
- **Tool-based calls** (using `as_tool`) provide a more granular approach where the new agent receives only a specific piece of generated input, performs its function, and then hands control (along with its output) back to the original agent to continue the dialogue.

This separation allows developers to choose between complete delegation of conversation and modular function calls, offering flexibility in building multi-agent systems that suit different application needs.

For more technical details, you can refer to the [OpenAI Agents SDK documentation](citeturn0search1) which outlines the implementation and intended usage of the `as_tool` method compared to handoffs.