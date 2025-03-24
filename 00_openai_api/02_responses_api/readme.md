# Tutorial: Using OpenAI's Responses API

https://platform.openai.com/docs/guides/text?api-mode=responses

https://platform.openai.com/docs/api-reference/responses

[Web Search and States with Responses API](https://cookbook.openai.com/examples/responses_api/responses_example)

[Doing RAG on PDFs using File Search in the Responses API](https://cookbook.openai.com/examples/file_search_responses)

## Step 1: Installation

Install the OpenAI Python library using `uv`:

```bash
uv pip install openai
```

## Step 2: Getting Your API Key

Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys).

## Step 3: Using Responses API (Basic Example)

Here's a simple Python example using the `chatgpt-4.5` model:

```python
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

response = openai.Response.create(
    model="chatgpt-4.5",
    messages=[
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Explain the theory of relativity in simple terms."}
    ],
    response_format={"type": "json_object"}
)

print(response.choices[0].message.content)
```

## Step 4: Advanced Example with Structured Outputs

Customize responses by defining structured outputs with the `chatgpt-4.5` model:

```python
response = openai.Response.create(
    model="chatgpt-4.5",
    messages=[{"role": "user", "content": "List 5 practical uses of AI."}],
    response_format={"type": "json_object", "schema": {"uses": ["string"]}},
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

## Step 5: Streaming Structured Responses

Stream structured responses using `chatgpt-4.5`:

```python
response = openai.Response.create(
    model="chatgpt-4.5",
    messages=[{"role": "user", "content": "Provide a structured joke about AI."}],
    response_format={"type": "json_object"},
    stream=True
)

for chunk in response:
    content = chunk['choices'][0].get('delta', {}).get('content')
    if content:
        print(content, end="", flush=True)
```

## Tips for Future Cross-Provider Compatibility

- **Endpoints and API keys differ**: Set the `api_base` for different providers when they become compatible.
- **Models vary**: Replace model names with those provided by your chosen provider.
- **Structured response support**: Ensure the provider supports structured responses.

## Conclusion

The OpenAI Responses API simplifies structured data integration, potentially enhancing compatibility across providers supporting structured outputs, fostering flexibility and reducing vendor lock-in.
