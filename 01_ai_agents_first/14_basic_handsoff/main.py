import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, handoff, set_tracing_disabled, ModelSettings, function_tool

# 🌿 Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
llm_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# Fitness Coach 
fitness_coach = Agent(
    name="Fitness Coach",
    instructions=(
        "You're a running coach. Ask 1-2 quick questions, then give a week plan. "
        "Keep it simple and encouraging. No medical advice."
    ),
)

# Study Coach
study_coach = Agent(
    name="Study Coach",
    instructions=(
        "You're a study planner. Ask for current routine, then give a 1-week schedule. "
        "Keep steps small and doable."
    ),
)

# Router that decides who should OWN the conversation
router = Agent(
    name="Coach Router",
    instructions=(
        "Route the user:\n"
        "- If message is about running, workout, stamina → handoff to Fitness Coach.\n"
        "- If it's about exams, study plan, focus, notes → handoff to Study Coach.\n"
        "After handoff, the specialist should continue the conversation."
    ),
    handoffs=[study_coach, handoff(fitness_coach)],
)

async def main():
    # ---- Turn 1: user asks about running → should handoff to Fitness Coach
    r1 = await Runner.run(router, "I want to run a 5Km in 8 weeks. Can you help?")
    print("\nTurn 1 (specialist reply):\n", r1.final_output)

    # Grab the specialist that actually replied (Fitness Coach)
    specialist = r1.last_agent

    # ---- Turn 2: user answers the coach's follow-up; continue with SAME specialist
    t2_input = r1.to_input_list() + [
        {"role": "user", "content": "Right now I can jog about 2 km, 3 days per week."}
    ]
    r2 = await Runner.run(specialist, t2_input)
    print("\nTurn 2 (specialist reply):\n", r2.final_output)

    # ---- Turn 3: another follow-up; still same specialist
    t3_input = r2.to_input_list() + [
        {"role": "user", "content": "Nice. What should I eat on training days?"}
    ]
    r3 = await Runner.run(specialist, t3_input)
    print("\nTurn 3 (specialist reply):\n", r3.final_output)


if __name__ == "__main__":
    asyncio.run(main())
