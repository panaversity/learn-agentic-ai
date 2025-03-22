# LiteLLM Python SDK

[Watch: LiteLLM - One Unified API for for all LLMs](https://www.youtube.com/watch?v=29_ipKNI8I0)

[Repo](https://github.com/BerriAI/litellm)

[Docs](https://docs.litellm.ai/docs/#litellm-python-sdk)

CrewAI has transitioned to using LiteLLM for integrating with various Large Language Models (LLMs). LiteLLM serves as an intermediary, allowing CrewAI to connect seamlessly with multiple LLM providers. This approach offers flexibility in choosing the appropriate model for specific use cases.  

Despite this shift, CrewAI maintains compatibility with LangChain tools. You can continue to integrate LangChain’s comprehensive set of tools into your CrewAI agents to enhance their capabilities.  

In summary, while CrewAI now utilizes LiteLLM for LLM integrations, it still supports the use of LangChain tools within its framework.  

LiteLLM is a Python SDK designed to simplify interactions with over 100 Large Language Models (LLMs) from various providers, including OpenAI, Anthropic, VertexAI, HuggingFace, Azure OpenAI, Ollama, and OpenRouter. It offers a unified interface, consistent output formatting, and built-in retry and fallback mechanisms, making it an invaluable tool for developers working with multiple LLMs.  

## Getting Started with LiteLLM
**1.	Installation:**  
Ensure you have Python installed, then install LiteLLM using pip:

```python
pip install litellm
```

**2.	Setting Up Environment Variables:**  
To authenticate with different LLM providers, set your API keys as environment variables. For example:

```python
import os
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key"
# Add other keys as needed
```


**3.	Making a Completion Request:**  
With LiteLLM, you can make completion requests to various models using a consistent interface. Here’s how to interact with OpenAI’s GPT-3.5-Turbo:

```python
from litellm import completion
messages = [{"role": "user", "content": "Hello, how are you?"}]
response = completion(model="gpt-3.5-turbo", messages=messages)
print(response['choices'][0]['message']['content'])
```

For other providers, such as Anthropic’s Claude or VertexAI’s Gemini, simply change the model parameter accordingly:

**For Anthropic's Claude**
```python
response = completion(model="claude-2", messages=messages)
```

**For VertexAI's Gemini**
```python
response = completion(model="gemini-2.0", messages=messages)
```


**4.	Handling Streaming Responses:**  
LiteLLM supports streaming responses, allowing you to process outputs in real-time. To enable streaming:

```python
response = completion(model="gpt-3.5-turbo", messages=messages, stream=True)
for part in response:
    print(part['choices'][0]['delta'].get('content', ''), end='')
```


**5.	Exception Handling:**  
LiteLLM maps exceptions across all supported providers to OpenAI’s exception types, enabling uniform error handling:

```python
from openai.error import OpenAIError
from litellm import completion
import os

os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key"

try:
    response = completion(model="claude-2", messages=messages)
except OpenAIError as e:
    print(f"An error occurred: {e}")
```


**6.	Logging and Observability:**  
LiteLLM provides pre-defined callbacks to send data to logging and monitoring tools like Lunary, Langfuse, and Helicone. To set up logging:

```python
from litellm import completion
import os

os.environ["LUNARY_PUBLIC_KEY"] = "your_lunary_public_key"
os.environ["HELICONE_API_KEY"] = "your_helicone_api_key"

litellm.success_callback = ["lunary", "langfuse", "helicone"]

response = completion(model="gpt-3.5-turbo", messages=messages)
```

## Fallback Example:
```python
from litellm import completion, exceptions
import os

os.environ["LUNARY_PUBLIC_KEY"] = "your_lunary_public_key"
os.environ["HELICONE_API_KEY"] = "your_helicone_api_key"

def anthropic():
    try:
        print("Attempting to use anthropic model")
        response = completion(
            model="claude-3-5-sonnet-20241022",
            messages=[{ "content": "Hello, how are you?","role": "user"}]
        )
        
    except exceptions.BadRequestError as e:
        print(f"\n!!!!!!!!!!! E R R O R !!!!!!!!!!!!!!!!!!!!!!!")
        print(f"---ERROR DETAIL --- {e}\n")
        print("\n!!!!!!!!!!!! Attempting to use gemini model !!!!!!!!!!!!!!!!!!!\n")
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{ "content": "Hello, how are you?","role": "user"}]
            )
        print(response)
```
## Advanced Features:  
- **Model Fallbacks:** Implement fallback mechanisms to ensure reliability by specifying alternative models if the primary one fails.
- **Configuration Management:** Utilize a config.yaml file to manage model-specific parameters effectively, simplifying adjustments and maintaining organized configurations.
- **Retry Mechanisms:** Enhance reliability by implementing retry strategies to handle transient errors gracefully.

### Additional Resources:
For more detailed tutorials and examples, refer to the official LiteLLM documentation and community resources:

[LiteLLM Getting Started Guide](https://docs.litellm.ai/)  

[LiteLLM GitHub Repository](https://github.com/BerriAI/litellm)

By following this guide, you can effectively integrate LiteLLM into your Python projects, enabling seamless interaction with a wide range of LLMs through a unified interface.
