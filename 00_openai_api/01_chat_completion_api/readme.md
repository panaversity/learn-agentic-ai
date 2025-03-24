# Tutorial: Using OpenAI's Chat Completion API

https://platform.openai.com/docs/guides/text?api-mode=chat

https://platform.openai.com/docs/api-reference/chat

## Step 1: Installation

Install the OpenAI Python library using `uv`:

```bash
uv add openai
```

## Step 2: Getting Your API Key

Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys).

## Step 3: Using Chat Completion API (Basic Example)

Here's a simple Python example:

```python
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Explain the theory of relativity in simple terms."}
    ]
)

print(response.choices[0].message.content)
```

## Step 4: Advanced Example with Parameters

Customize responses by adjusting parameters:

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "List 5 practical uses of AI."}],
    temperature=0.7,  # Creativity of the responses
    max_tokens=150,   # Length of the response
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

print(response.choices[0].message.content)
```

## Step 5: Streaming Responses

Get responses token-by-token:

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a joke about AI."}],
    stream=True
)

for chunk in response:
    content = chunk['choices'][0].get('delta', {}).get('content')
    if content:
        print(content, end="", flush=True)
```

## Compatibility with Other APIs (Using Chat Completion API)

The OpenAI Chat Completion API has become an industry standard, and APIs from Google, Anthropic, DeepSeek, etc., offer compatibility. You can call these providers directly using the same OpenAI Python library by changing the `api_base` URL.

### Google (Gemini)

```python
import openai

openai.api_key = "YOUR_GOOGLE_API_KEY"
openai.api_base = "https://generativelanguage.googleapis.com/v1beta"

response = openai.ChatCompletion.create(
    model="gemini-1.5-flash",
    messages=[{"role": "user", "content": "Explain AI in simple terms."}]
)

print(response.choices[0].message.content)
```

### Anthropic (Claude 3)

```python
import openai

openai.api_key = "YOUR_ANTHROPIC_API_KEY"
openai.api_base = "https://api.anthropic.com/v1"

response = openai.ChatCompletion.create(
    model="claude-3-haiku-20240307",
    messages=[{"role": "user", "content": "Summarize the plot of Hamlet in a paragraph."}],
    temperature=0.5,
    max_tokens=200
)

print(response.choices[0].message.content)
```

### DeepSeek

```python
import openai

openai.api_key = "YOUR_DEEPSEEK_API_KEY"
openai.api_base = "https://api.deepseek.com"

response = openai.ChatCompletion.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Describe Quantum Computing."}]
)

print(response.choices[0].message.content)
```

## Tips for Cross-Provider Compatibility

- **Endpoints and API keys differ**: Set the `api_base` for different providers.
- **Models vary**: Replace model names with those provided by your chosen provider.
- **Parameters compatibility**: Most parameters (`temperature`, `max_tokens`, etc.) remain consistent.

## Conclusion

The OpenAI Chat Completion API's standardization simplifies integration across multiple providers, fostering flexibility and reducing vendor lock-in.
