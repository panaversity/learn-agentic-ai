#!/usr/bin/env python3
"""
Smart Chunking for Gemini Embeddings
====================================

- Chunks text for Gemini embedding models (token estimate: 1 token ≈ 4 chars).
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
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GeminiSmartChunker:
    def __init__(
        self,
        input_file: str = "data/rag_ready/rag_ready_data.json",
        output_dir: str = "data/gemini_chunked",
        max_tokens: int = 3072,
    ):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_tokens = max_tokens - 200  # Safe buffer

    def estimate_tokens(self, text: str) -> int:
        # Conservative estimate: 1 token ≈ 4 chars
        return max(1, len(text) // 4)

    def smart_chunk(
        self, text: str, max_tokens: int = None, overlap_tokens: int = 150
    ) -> List[str]:
        if max_tokens is None:
            max_tokens = self.max_tokens
        if not text or not text.strip():
            return []
        if self.estimate_tokens(text) <= max_tokens:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_tokens * 4, len(text))
            chunk = text[start:end].strip()
            chunks.append(chunk)
            if end >= len(text):
                break
            start = end - overlap_tokens * 4
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
                            "token_count": self.estimate_tokens(chunk),
                        },
                    }
                )
        # Save output
        output_file = self.output_dir / "gemini_chunked_data.json"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(processed, indent=2, ensure_ascii=False))
        logger.info(f"Saved {len(processed)} Gemini-chunked items to {output_file}")


if __name__ == "__main__":
    asyncio.run(GeminiSmartChunker().process_all_items())
