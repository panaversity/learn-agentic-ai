# Import the Agent and Runner classes from the agents module
from agents import Agent, Runner

# Create a new AI agent with a name and instructions 
agent = Agent(
    name="Assistant",  # Set the name of the agent
    instructions="You are a helpful assistant that can answer questions and help with tasks.",  # Define how the agent should behave
)

# Run the agent synchronously with a specific question
result = Runner.run_sync(agent, "What is the capital of pakistan?")

# Print the agent's response
print(result.final_output)