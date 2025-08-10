import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, ModelSettings, function_tool

# 🌿 Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
llm_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)


from agents import Agent, Runner, handoff
import asyncio

# 1) Two specialists that will OWN the conversation after transfer
billing_agent = Agent(
    name="Billing Agent",
    instructions="Resolve billing problems end-to-end. Ask for any details you need."
)

refunds_agent = Agent(
    name="Refunds Agent",
    instructions="Handle refunds end-to-end. Ask for order ID and explain next steps."
)

# 2) Triage agent that decides WHO should take over
triage = Agent(
    name="Triage Agent",
    instructions=(
        "Greet the user and decide where to send them:\n"
        "- If the user asks about a double charge, invoice, payment, etc., hand off to Billing Agent.\n"
        "- If the user asks about refund status or returning an item, hand off to Refunds Agent.\n"
        "Once handed off, the specialist should continue the conversation."
    ),
    # You can list the agents directly or wrap with handoff(...) for later customization
    handoffs=[billing_agent, handoff(refunds_agent)],
)

async def main():
    # Example A: A refund-style question → should hand off to Refunds Agent
    r1 = await Runner.run(triage, "Hi, I returned my headset last week. What's my refund status?")
    print("A) Final reply (from REFUNDS specialist):", r1.final_output, "\n")

    # Example B: A billing-style question → should hand off to Billing Agent
    r2 = await Runner.run(triage, "My card was charged twice for the same order.")
    print("B) Final reply (from BILLING specialist):", r2.final_output)


if __name__ == "__main__":
    asyncio.run(main())
