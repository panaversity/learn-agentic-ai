# 🧬 Agent Cloning: Create Agent Variants
# Simple examples to learn agent cloning

import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, ModelSettings, function_tool

# 🌿 Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# 🛠️ Simple tools for learning
@function_tool
def calculate_area(length: float, width: float) -> str:
    """Calculate the area of a rectangle."""
    area = length * width
    return f"Area = {length} × {width} = {area} square units"

@function_tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    return f"The weather in {city} is sunny and 72°F"

def main():
    """Learn Agent Cloning with simple examples."""
    print("🧬 Agent Cloning: Create Agent Variants")
    print("=" * 50)
    
    # 🎯 Example 1: Basic Cloning
    print("\n🎯 Example 1: Basic Cloning")
    print("-" * 40)
    
    # Base agent
    base_agent = Agent(
        name="BaseAssistant",
        instructions="You are a helpful assistant.",
        model_settings=ModelSettings(temperature=0.7),
        model=model
    )
    
    # Simple clone
    friendly_agent = base_agent.clone(
        name="FriendlyAssistant",
        instructions="You are a very friendly and warm assistant."
    )
    
    # Test both agents
    query = "Hello, how are you?"
    
    result_base = Runner.run_sync(base_agent, query)
    result_friendly = Runner.run_sync(friendly_agent, query)
    
    print("Base Agent:")
    print(result_base.final_output)
    print("\nFriendly Agent:")
    print(result_friendly.final_output)
    
    # 🎯 Example 2: Cloning with Different Settings
    print("\n🎯 Example 2: Cloning with Different Settings")
    print("-" * 40)
    
    # Clone with different temperature
    creative_agent = base_agent.clone(
        name="CreativeAssistant",
        instructions="You are a creative writing assistant.",
        model_settings=ModelSettings(temperature=0.9)  # Higher creativity
    )
    
    precise_agent = base_agent.clone(
        name="PreciseAssistant", 
        instructions="You are a precise, factual assistant.",
        model_settings=ModelSettings(temperature=0.1)  # Lower creativity
    )
    
    # Test creativity levels
    query = "Describe a sunset."
    
    result_creative = Runner.run_sync(creative_agent, query)
    result_precise = Runner.run_sync(precise_agent, query)
    
    print("Creative Agent:")
    print(result_creative.final_output)
    print("\nPrecise Agent:")
    print(result_precise.final_output)
    
    # 🎯 Example 3: Cloning with Different Tools
    print("\n🎯 Example 3: Cloning with Different Tools")
    print("-" * 40)
    
    # Base agent with one tool
    base_agent_with_tools = Agent(
        name="BaseAssistant",
        tools=[calculate_area],
        instructions="You are a helpful assistant.",
        model=model
    )
    
    # Clone with additional tool
    weather_agent = base_agent_with_tools.clone(
        name="WeatherAssistant",
        tools=[calculate_area, get_weather],  # New tools list
        instructions="You are a weather and math assistant."
    )
    
    # Clone with different tools
    math_agent = base_agent_with_tools.clone(
        name="MathAssistant",
        tools=[calculate_area],  # Same tools
        instructions="You are a math specialist."
    )
    
    # Test tool usage
    query = "What's the area of a 5x3 rectangle and the weather in Tokyo?"
    
    result_weather = Runner.run_sync(weather_agent, query)
    result_math = Runner.run_sync(math_agent, query)
    
    print("Weather Agent:")
    print(result_weather.final_output)
    print("\nMath Agent:")
    print(result_math.final_output)
    
    # 🎯 Example 4: Multiple Clones from One Base
    print("\n🎯 Example 4: Multiple Clones from One Base")
    print("-" * 40)
    
    # Create multiple specialized variants
    agents = {
        "Creative": base_agent.clone(
            name="CreativeWriter",
            instructions="You are a creative writer. Use vivid language.",
            model_settings=ModelSettings(temperature=0.9)
        ),
        "Precise": base_agent.clone(
            name="PreciseAssistant", 
            instructions="You are a precise assistant. Be accurate and concise.",
            model_settings=ModelSettings(temperature=0.1)
        ),
        "Friendly": base_agent.clone(
            name="FriendlyAssistant",
            instructions="You are a very friendly assistant. Be warm and encouraging."
        ),
        "Professional": base_agent.clone(
            name="ProfessionalAssistant",
            instructions="You are a professional assistant. Be formal and business-like."
        )
    }
    
    # Test all variants
    query = "Tell me about artificial intelligence."
    
    for name, agent in agents.items():
        result = Runner.run_sync(agent, query)
        print(f"\n{name} Agent:")
        print(result.final_output[:150] + "...")
    
    # 🎯 Example 5: Understanding Shared References
    print("\n🎯 Example 5: Understanding Shared References")
    print("-" * 40)
    
    # Demonstrate shared references
    original_agent = Agent(
        name="Original",
        tools=[calculate_area],
        instructions="You are helpful.",
        model=model
    )
    
    # Clone without new tools list
    shared_clone = original_agent.clone(
        name="SharedClone",
        instructions="You are creative."
    )
    
    # Add tool to original
    @function_tool
    def new_tool() -> str:
        return "I'm a new tool!"
    
    original_agent.tools.append(new_tool)
    
    # Check if clone also has the new tool
    print("Original tools:", len(original_agent.tools))  # 2
    print("Shared clone tools:", len(shared_clone.tools))  # 2 (shared!)
    
    # Create independent clone
    independent_clone = original_agent.clone(
        name="IndependentClone",
        tools=[calculate_area],  # New list
        instructions="You are independent."
    )
    
    original_agent.tools.append(new_tool)
    print("Independent clone tools:", len(independent_clone.tools))  # 1 (independent!)
    
    print("\n💡 Notice: Shared clone has the same tools as original,")
    print("   while independent clone has its own tool list!")
    
    # 🎯 Example 6: Practical Agent Family
    print("\n🎯 Example 6: Practical Agent Family")
    print("-" * 40)
    
    # Create a base agent for different writing styles
    base_writer = Agent(
        name="BaseWriter",
        instructions="You are a helpful writer.",
        model_settings=ModelSettings(temperature=0.7),
        model=model
    )
    
    # Create writing style variants
    writing_agents = {
        "Poet": base_writer.clone(
            name="Poet",
            instructions="You are a poet. Respond in verse.",
            model_settings=ModelSettings(temperature=0.9)
        ),
        "Scientist": base_writer.clone(
            name="Scientist", 
            instructions="You are a scientist. Be precise and factual.",
            model_settings=ModelSettings(temperature=0.1)
        ),
        "Chef": base_writer.clone(
            name="Chef",
            instructions="You are a chef. Talk about food and cooking."
        )
    }
    
    # Test all writing styles
    query = "What is love?"
    
    for name, agent in writing_agents.items():
        result = Runner.run_sync(agent, query)
        print(f"\n{name}:")
        print(result.final_output[:100] + "...")
    
    print("\n🎉 You've learned Agent Cloning!")
    print("💡 Try creating your own agent families!")

if __name__ == "__main__":
    main() 