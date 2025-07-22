#!/usr/bin/env python3
"""
Add OpenAI Embeddings to Qdrant
==============================

This script reads OpenAI embeddings from a JSON file and inserts them into a Qdrant collection.

Usage:
    python add_openai_embeddings_to_qdrant.py

Requirements:
    - pip install qdrant-client
    - Qdrant running locally (see vectordb/README.md)
"""
import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# Config
EMBEDDINGS_PATH = Path("data/embeddings/openai_embeddings_with_metadata.json")
COLLECTION_NAME = "openai_vectors"
VECTOR_SIZE = 1536  # Default for text-embedding-3-small
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Load embeddings
with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
    embeddings = data.get("embeddings", [])

if not embeddings:
    raise ValueError(f"No embeddings found in {EMBEDDINGS_PATH}")

# Connect to Qdrant
client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

# Create collection if not exists
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)

# Prepare points
points = []
for idx, item in enumerate(embeddings):
    vector = item["embedding"]
    payload = {
        "id": item.get("id"),
        "content": item.get("content"),
        "content_type": item.get("content_type"),
        "source_url": item.get("source_url"),
        "metadata": item.get("metadata", {}),
    }
    points.append(PointStruct(id=idx, vector=vector, payload=payload))

# Insert into Qdrant
client.upsert(collection_name=COLLECTION_NAME, points=points)
print(
    f"Inserted {len(points)} OpenAI embeddings into Qdrant collection '{COLLECTION_NAME}'"
)
