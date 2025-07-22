# Example: Generate embeddings using OpenAI API
# Docs: https://platform.openai.com/docs/guides/embeddings

import openai

# Configure your API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# The model to use for embeddings
model = "text-embedding-ada-002"

# The text to embed
text = "The quick brown fox jumps over the lazy dog."

# Generate the embedding
response = openai.Embedding.create(input=text, model=model)

embedding = response["data"][0]["embedding"]
print("Embedding vector:", embedding)
