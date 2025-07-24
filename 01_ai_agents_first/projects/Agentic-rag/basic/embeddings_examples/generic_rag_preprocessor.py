#!/usr/bin/env python3
"""
Generic RAG Preprocessor
========================

Reads a directory of JSON files (from web crawls or other sources),
cleans and chunks the text, and outputs RAG-ready data for embeddings.
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


class GenericRAGPreprocessor:
    def __init__(
        self, input_dir: str = "data/crawlers_json", output_dir: str = "data/rag_ready"
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Basic text cleaning: remove extra whitespace and unwanted characters."""
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def smart_chunk_text(
        self, text: str, max_chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """Chunk text for embeddings, preserving meaning."""
        if len(text) <= max_chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_chunk_size, len(text))
            # Try to break at a sentence boundary
            if end < len(text):
                for i in range(end, start, -1):
                    if text[i - 1] in ".!?":
                        end = i
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap
            if start >= len(text):
                break
        return chunks

    async def process_all_files(self) -> List[Dict[str, Any]]:
        """Process all JSON files in the input directory."""
        files = list(self.input_dir.glob("*.json"))
        logger.info(f"Processing {len(files)} files from {self.input_dir}")
        processed = []
        for file_path in tqdm(files, desc="Processing files"):
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    item = json.loads(content)
                    # Try to get the main text field
                    text = (
                        item.get("content")
                        or item.get("text")
                        or item.get("markdown")
                        or ""
                    )
                    text = self.clean_text(text)
                    if not text:
                        continue
                    # Chunk if needed
                    if len(text) > 1000:
                        chunks = self.smart_chunk_text(text)
                        for i, chunk in enumerate(chunks):
                            processed.append(
                                {
                                    "id": f"{file_path.stem}_chunk_{i}",
                                    "title": item.get("title", f"Chunk {i}"),
                                    "content": chunk,
                                    "metadata": {
                                        "source_file": str(file_path),
                                        "chunk_index": i,
                                        "total_chunks": len(chunks),
                                        "original_url": item.get("url", ""),
                                        "processed_at": datetime.now().isoformat(),
                                    },
                                }
                            )
                    else:
                        processed.append(
                            {
                                "id": file_path.stem,
                                "title": item.get("title", file_path.stem),
                                "content": text,
                                "metadata": {
                                    "source_file": str(file_path),
                                    "original_url": item.get("url", ""),
                                    "processed_at": datetime.now().isoformat(),
                                },
                            }
                        )
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        return processed

    async def run(self):
        """Main entry point: process files and save output."""
        processed = await self.process_all_files()
        output_file = self.output_dir / "rag_ready_data.json"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(processed, indent=2, ensure_ascii=False))
        logger.info(f"Saved {len(processed)} RAG-ready items to {output_file}")


if __name__ == "__main__":
    asyncio.run(GenericRAGPreprocessor().run())
