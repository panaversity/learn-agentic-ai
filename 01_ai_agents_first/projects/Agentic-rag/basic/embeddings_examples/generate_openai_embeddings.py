#!/usr/bin/env python3
"""
Generate Embeddings with OpenAI API
===================================

Usage:
    python generate_openai_embeddings.py --input data.json --output embeddings.json

Environment Variables:
    OPENAI_API_KEY: Your OpenAI API key (required)
    BATCH_SIZE: Number of texts per batch (default: 100)
    RATE_LIMIT_DELAY: Delay between batches in seconds (default: 1)
    EMBEDDING_MODEL: OpenAI embedding model (default: text-embedding-3-small)
    EMBEDDING_DIMENSIONS: Embedding dimensions (default: 1536)
"""

import argparse
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import openai
import tiktoken
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration with environment variable fallbacks
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1"))


class OpenAIEmbeddingGenerator:
    """Generate embeddings from categorized chunked RAG data using OpenAI API."""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.embeddings.create(
                    model=EMBEDDING_MODEL, input=texts, dimensions=EMBEDDING_DIMENSIONS
                )
                embeddings = [embedding.embedding for embedding in response.data]
                for i, embedding in enumerate(embeddings):
                    if len(embedding) != EMBEDDING_DIMENSIONS:
                        raise ValueError(
                            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
                            f"got {len(embedding)} for text {i}"
                        )
                return embeddings
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RATE_LIMIT_DELAY * (2**attempt))
                else:
                    raise

    def load_chunked_data(self, data_path: Path) -> List[Dict[str, Any]]:
        """Load chunked RAG data from JSON file."""
        logger.info(f"Loading chunked data from: {data_path}")
        if not data_path.exists():
            raise FileNotFoundError(f"Input file not found: {data_path}")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_chunks = []
        if isinstance(data, dict):
            for category, items in data.items():
                all_chunks.extend(items)
        elif isinstance(data, list):
            all_chunks = data
        else:
            raise ValueError(f"Unexpected data format: {type(data)}")
        logger.info(f"Loaded {len(all_chunks)} total chunks")
        return all_chunks

    def prepare_texts_for_embedding(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prepare texts for embedding generation."""
        prepared_items = []
        for chunk in chunks:
            content = chunk.get("content", "")
            if not content:
                logger.warning(f"Empty content for chunk: {chunk.get('id', 'unknown')}")
                continue
            token_count = self.count_tokens(content)
            item = {
                "id": chunk.get("id", f"chunk_{len(prepared_items)}"),
                "content": content,
                "token_count": token_count,
                "content_type": chunk.get("content_type", "unknown"),
                "source_url": chunk.get("url", ""),
                "metadata": chunk.get("metadata", {}),
                "original_data": chunk,
            }
            prepared_items.append(item)
        logger.info(f"Prepared {len(prepared_items)} items for embedding")
        return prepared_items

    async def generate_all_embeddings(
        self, prepared_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for all prepared items."""
        logger.info(f"Generating embeddings for {len(prepared_items)} items")
        embedded_items = []
        for i in tqdm(
            range(0, len(prepared_items), BATCH_SIZE), desc="Generating embeddings"
        ):
            batch = prepared_items[i : i + BATCH_SIZE]
            batch_texts = [item["content"] for item in batch]
            batch_tokens = sum(item["token_count"] for item in batch)
            logger.info(
                f"Processing batch {i//BATCH_SIZE + 1}, {len(batch)} items, {batch_tokens} tokens"
            )
            try:
                embeddings = await self.generate_embeddings_batch(batch_texts)
                for item, embedding in zip(batch, embeddings):
                    embedded_item = item.copy()
                    embedded_item["embedding"] = embedding
                    embedded_item["embedding_model"] = EMBEDDING_MODEL
                    embedded_item["embedding_dimensions"] = EMBEDDING_DIMENSIONS
                    embedded_item["generated_at"] = datetime.now().isoformat()
                    embedded_items.append(embedded_item)
                await asyncio.sleep(RATE_LIMIT_DELAY)
            except Exception as e:
                logger.error(f"Failed to process batch {i//BATCH_SIZE + 1}: {e}")
                raise
        logger.info(f"Generated embeddings for {len(embedded_items)} items")
        return embedded_items

    def save_embeddings(self, embedded_items: List[Dict[str, Any]], output_path: Path):
        """Save embeddings to JSON file."""
        logger.info(f"Saving embeddings to: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        total_tokens = sum(item["token_count"] for item in embedded_items)
        output_data = {
            "metadata": {
                "total_items": len(embedded_items),
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
                "generated_at": datetime.now().isoformat(),
                "total_tokens": total_tokens,
            },
            "embeddings": embedded_items,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(embedded_items)} embeddings to {output_path}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate embeddings from chunked RAG data using OpenAI API"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("data/chunked_rag_ready/chunked_rag_data.json"),
        help="Input JSON file path (default: data/chunked_rag_ready/chunked_rag_data.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/embeddings/openai_embeddings_with_metadata.json"),
        help="Output JSON file path (default: data/embeddings/openai_embeddings_with_metadata.json)",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=BATCH_SIZE,
        help=f"Batch size for processing (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--rate-limit-delay",
        "-r",
        type=float,
        default=RATE_LIMIT_DELAY,
        help=f"Delay between batches in seconds (default: {RATE_LIMIT_DELAY})",
    )
    parser.add_argument(
        "--embedding-model",
        "-m",
        type=str,
        default=EMBEDDING_MODEL,
        help=f"OpenAI embedding model (default: {EMBEDDING_MODEL})",
    )
    parser.add_argument(
        "--embedding-dimensions",
        "-d",
        type=int,
        default=EMBEDDING_DIMENSIONS,
        help=f"Embedding dimensions (default: {EMBEDDING_DIMENSIONS})",
    )
    parser.add_argument(
        "--max-retries",
        "-t",
        type=int,
        default=MAX_RETRIES,
        help=f"Maximum retry attempts (default: {MAX_RETRIES})",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    return parser.parse_args()


async def main():
    args = parse_arguments()
    global BATCH_SIZE, RATE_LIMIT_DELAY, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, MAX_RETRIES
    BATCH_SIZE = args.batch_size
    RATE_LIMIT_DELAY = args.rate_limit_delay
    EMBEDDING_MODEL = args.embedding_model
    EMBEDDING_DIMENSIONS = args.embedding_dimensions
    MAX_RETRIES = args.max_retries
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        return
    generator = OpenAIEmbeddingGenerator(api_key)
    try:
        chunks = generator.load_chunked_data(args.input)
        prepared_items = generator.prepare_texts_for_embedding(chunks)
        if not prepared_items:
            logger.error("No items to process")
            return
        embedded_items = await generator.generate_all_embeddings(prepared_items)
        generator.save_embeddings(embedded_items, args.output)
        logger.info("=" * 50)
        logger.info("OPENAI EMBEDDING GENERATION COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Total items processed: {len(embedded_items)}")
        logger.info(f"Output file: {args.output}")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
