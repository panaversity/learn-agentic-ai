import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, GuardrailFunctionOutput, input_guardrail, InputGuardrailTripwireTriggered, RunContextWrapper, output_guardrail, OutputGuardrailTripwireTriggered
from typing import Any
from pydantic import BaseModel

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

class WeatherSanitizer(BaseModel):
    weather_related: bool
    reason: str | None = None

weather_sanitizer = Agent(
    name="WeatherSanitizer",
    instructions="Check if this is a weather related query",
    model=llm_model,
    output_type=WeatherSanitizer
)

@input_guardrail
async def weather_input_checker(ctx: RunContextWrapper, agent: Agent, input):
    res = await Runner.run(weather_sanitizer, input)
    print("\n[WEATHER SANITIZER RESPONSE]", res.final_output)
    return GuardrailFunctionOutput(
        output_info="passed",
        tripwire_triggered=res.final_output.weather_related is False
        )

@output_guardrail
def weather_response_checker(ctx: RunContextWrapper, agent: Agent, output: Any):    
    # CODE REGREX PATTERN......
    # AGENT Call -> Special guardrail agent
    return GuardrailFunctionOutput(
        output_info="passed",
        tripwire_triggered=False
        )

base_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are a helpful assistant.",
    model=llm_model,
    input_guardrails=[weather_input_checker],
    output_guardrails=[weather_response_checker]
)

try:
    res = Runner.run_sync(base_agent, [{"role": "user", "content": "What's the weather like in SF?"}])
    print("[OUTPUT]" , res.to_input_list())
except InputGuardrailTripwireTriggered as e:
    print("Alert: Guardrail input tripwire was triggered!")
except OutputGuardrailTripwireTriggered as e:
    print("Alert: Guardrail output tripwire was triggered!")