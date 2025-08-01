from agents import Agent,OpenAIChatCompletionsModel,Runner,function_tool
from openai import AsyncOpenAI
from dotenv import get_key,find_dotenv
import requests

gemini_api_key=get_key(find_dotenv(),"GEMINI_API_KEY")


client=AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=gemini_api_key

)

@function_tool
def get_weather(city:str)->str:
    """
    Get the current weather for a given city.
    """
    result=requests.get(f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}")
    data=result.json()
    return f"The current weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."


model=OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client,
)

agent:Agent=Agent(
    name="Weather Agent",
    instructions="You are a weather agent. You can provide weather information and forecasts.",
    model=model,
    tools=[get_weather]
)

result= Runner.run_sync(agent, "What's the weather like in Islamabad?")
print(result.final_output)