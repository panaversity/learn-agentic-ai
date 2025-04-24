[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/16PwQS1ZlDMn-hCL4666cKLnEewS1E-TV?usp=sharing)

# LiteLLM Agent SDK with Google Gemini

This repository contains a Jupyter Notebook demonstrating how to use the `openai-agents` SDK with LiteLLM to integrate Google Gemini models for building conversational agents. The notebook showcases setting up an agent that responds in haikus and includes a simple weather function tool.

## Prerequisites

- Python 3.6 or higher
- Jupyter Notebook or JupyterLab
- Google Colab (optional, for running in a cloud environment)
- A valid Google Gemini API key

## Installation

1. Install the required Python packages by running the following command in the notebook:
   ```bash
   !pip install -Uq openai-agents "openai-agents[litellm]"
   ```

2. Ensure your Jupyter environment supports asynchronous functions by applying `nest_asyncio`:
   ```python
   import nest_asyncio
   nest_asyncio.apply()
   ```

3. Set up your Google Gemini API key in your environment. In Google Colab, you can store it in the `userdata` module:
   ```python
   from google.colab import userdata
   GEMINI_API_KEY = userdata.get("GEMINI_API_KEY")
   ```

## Notebook Overview

The Jupyter Notebook (`03_Litellm_agent_sdk.ipynb`) includes the following sections:

1. **Install openai-agents SDK**: Installs the `openai-agents` package along with the `litellm` extension.
2. **Enable Asynchronous Support**: Configures the notebook to handle asynchronous functions using `nest_asyncio`.
3. **Run Google Gemini with LiteLLM and openai-agents SDK**: Demonstrates how to:
   - Create an agent using the `openai-agents` SDK.
   - Integrate Google Gemini via LiteLLM.
   - Define a function tool (`get_weather`) to simulate retrieving weather data.
   - Run the agent synchronously to respond to a query in haiku format.

### Key Code Example

```python
from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel

MODEL = 'gemini/gemini-2.0-flash'

@function_tool
def get_weather(city: str) -> str:
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."

agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
    model=LitellmModel(model=MODEL, api_key=GEMINI_API_KEY),
    tools=[get_weather]
)

result = Runner.run_sync(agent, "What's the weather in Tokyo?")
print(result.final_output)
```

### Expected Output

The agent responds to the query "What's the weather in Tokyo?" with a haiku, such as:
```
Skies now partly clear,
Seventy degrees in Tokyo,
Gentle breeze abounds.
```

## Usage

1. Open the `03_Litellm_agent_sdk.ipynb` notebook in Jupyter or Google Colab.
2. Ensure your Gemini API key is configured.
3. Run the cells in sequence to install dependencies, enable async support, and execute the agent.
4. Modify the `MODEL` or query to experiment with different Gemini models or questions.

## Notes

- The `get_weather` function is a placeholder. Replace it with a real API call (e.g., OpenWeatherMap) for production use.
- The notebook disables tracing (`set_tracing_disabled(True)`) to simplify output. Enable tracing for debugging if needed.
- Ensure your API key is securely stored and not hardcoded in production environments.
