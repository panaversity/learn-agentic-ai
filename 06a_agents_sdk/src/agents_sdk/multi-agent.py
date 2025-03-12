# Import necessary classes from agents module and asyncio for async operations
from agents import Agent, Runner
import asyncio

# Create an agent specialized in Pakistan-related questions
pakistan_agent = Agent(
    name="Pakistan Agent",
    handoff_description="Specialist agent for Pakistan-related questions",  # Description used when referring to this agent
    instructions="You are a helpful assistant that can answer questions about Pakistan.",
)

# Create an agent specialized in India-related questions
india_agent = Agent(
    name="India Agent",
    handoff_description="Specialist agent for india-related questions",  # Description used when referring to this agent
    instructions="You are a helpful assistant that can answer questions about India.",
)

# Create an agent specialized in USA-related questions
usa_agent = Agent(
    name="USA Agent",
    handoff_description="Specialist agent for USA-related questions",  # Description used when referring to this agent
    instructions="You are a helpful assistant that can answer questions about USA.",
)

# Create a triage agent that will direct questions to the appropriate specialist agent
trainge_agent = Agent(
    name="Trainge Agent",
    instructions="You determine which agent to use based on the user's country question",
    handoffs=[
        pakistan_agent,
        india_agent,
        usa_agent,
    ],  # List of specialist agents this agent can refer to
)


# Define the main async function that will run our agent
async def main():
    # Run the triage agent with a specific question and await its response
    result = await Runner.run(trainge_agent, "What is the Capital of Pakistan?")
    # Print the final response from the agent
    print(result.final_output)


# Standard Python idiom to run the main function only if this file is run directly
if __name__ == "__main__":
    # Run the async main function using asyncio
    asyncio.run(main())
