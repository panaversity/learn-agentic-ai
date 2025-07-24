# Example: OpenAI Agents SDK (official)
# Docs: https://openai.github.io/openai-agents-python/
# Install: uv add openai-agents

import os

from agents import Agent, Runner

# Set your OpenAI API key (use environment variable for security)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-...your-key...")

# Create an agent with instructions
agent = Agent(name="Assistant", instructions="You are a helpful assistant.")

# Run the agent synchronously with a prompt
if __name__ == "__main__":
    prompt = "Write a haiku about recursion in programming."
    result = Runner.run_sync(agent, prompt)
    print(result.final_output)
    # Example output:
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance.
