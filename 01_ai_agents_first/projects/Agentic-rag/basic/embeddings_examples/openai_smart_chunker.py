#!/usr/bin/env python3
"""
Smart Chunking for OpenAI Embeddings
====================================

- Uses tiktoken to chunk text for OpenAI embedding models.
- Ensures each chunk fits within the model's token limit.
- Reads rag_ready_data.json and outputs chunked data and a summary for RAG workflows.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
import tiktoken
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAISmartChunker:
    def __init__(
        self,
        input_file: str = "data/rag_ready/rag_ready_data.json",
        output_dir: str = "data/openai_chunked",
        model_name: str = "text-embedding-3-small",
    ):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = 8191 - 200  # Safe buffer

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def smart_chunk(
        self, text: str, max_tokens: int = None, overlap_tokens: int = 150
    ) -> List[str]:
        if max_tokens is None:
            max_tokens = self.max_tokens
        if not text or not text.strip():
            return []
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return [text]
        # Chunk by tokens, try to break at sentence boundaries
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text.strip())
            if end >= len(tokens):
                break
            start = end - overlap_tokens
        return chunks

    async def process_all_items(self):
        if not self.input_file.exists():
            logger.error(f"Input file not found: {self.input_file}")
            return
        async with aiofiles.open(self.input_file, "r", encoding="utf-8") as f:
            items = json.loads(await f.read())
        logger.info(f"Processing {len(items)} items from {self.input_file}")
        processed = []
        for idx, item in enumerate(tqdm(items, desc="Chunking items")):
            text = item.get("content") or item.get("text") or item.get("markdown") or ""
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            chunks = self.smart_chunk(text)
            for i, chunk in enumerate(chunks):
                processed.append(
                    {
                        "id": f"{item.get('id', idx)}_chunk_{i}",
                        "title": item.get("title", f"Chunk {i}"),
                        "content": chunk,
                        "metadata": {
                            **item.get("metadata", {}),
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "processed_at": datetime.now().isoformat(),
                            "token_count": self.count_tokens(chunk),
                        },
                    }
                )
        # Save output
        output_file = self.output_dir / "openai_chunked_data.json"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(processed, indent=2, ensure_ascii=False))
        logger.info(f"Saved {len(processed)} OpenAI-chunked items to {output_file}")


if __name__ == "__main__":
    asyncio.run(OpenAISmartChunker().process_all_items())
