# Import needed tools and libraries
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

# Define what the homework check response should look like
class HomeworkOutput(BaseModel):
    is_homework: bool      # True/False if it's homework
    reasoning: str        # Why it was classified as homework or not

# Create an agent that checks if questions are homework-related
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,  # Use our homework check format
)

# Create a math specialist agent
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

# Create a history specialist agent
history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

# Function that checks if input is homework-related
async def homework_guardrail(ctx, agent, input_data):
    # Ask the guardrail agent to check the input
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    # Convert the result to our homework check format
    final_output = result.final_output_as(HomeworkOutput)
    # Return whether it's homework and if we should block the request
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,  # Block if it's not homework
    )

# Create main agent that directs questions to specialists
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],  # List of specialist agents
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),  # Add homework check
    ],
)

# Main function to run our program
async def main():
    # Test the system with a math question
    result = await Runner.run(triage_agent, "what is 10 + 10")
    # Show the result
    print(result.final_output)

# Run the program if this file is run directly
if __name__ == "__main__":
    asyncio.run(main())