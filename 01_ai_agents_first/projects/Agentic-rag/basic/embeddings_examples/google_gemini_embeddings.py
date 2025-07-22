# Example: Generate embeddings using Google Gemini API
# Docs: https://ai.google.dev/gemini-api/docs/embeddings#python

import google.generativeai as genai

# Configure your API key
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# The model to use for embeddings
model = genai.GenerativeModel("embedding-001")

# The text to embed
text = "The quick brown fox jumps over the lazy dog."

# Generate the embedding
response = model.embed_content(
    content=text, task_type="retrieval_document"  # or "retrieval_query" for queries
)

embedding = response["embedding"]
print("Embedding vector:", embedding)
