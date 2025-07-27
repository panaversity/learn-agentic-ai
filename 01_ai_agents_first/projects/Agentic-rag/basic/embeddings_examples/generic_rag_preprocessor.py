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
        iteration_count = 0
        max_iterations = len(text) // (max_chunk_size - overlap) + 10  # Safety limit

        while start < len(text) and iteration_count < max_iterations:
            iteration_count += 1
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

        if iteration_count >= max_iterations:
            logger.warning(
                f"Reached maximum iterations in chunking for text of length {len(text)}"
            )

        return chunks

    async def process_all_files(self) -> List[Dict[str, Any]]:
        """Process all JSON files in the input directory."""
        files = list(self.input_dir.glob("*.json"))
        logger.info(f"Processing {len(files)} files from {self.input_dir}")
        processed = []
        for file_path in tqdm(files, desc="Processing files"):
            try:
                logger.info(f"Starting to process {file_path.name}")
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    logger.info(f"Read {len(content)} characters from {file_path.name}")

                    data = json.loads(content)
                    logger.info(f"Successfully parsed JSON from {file_path.name}")

                    # Handle both single objects and arrays of objects
                    items = []
                    if isinstance(data, list):
                        items = data
                        logger.info(
                            f"Processing {len(items)} items from array in {file_path.name}"
                        )
                    else:
                        items = [data]
                        logger.info(f"Processing single item from {file_path.name}")

                    for item_index, item in enumerate(items):
                        logger.info(
                            f"Processing item {item_index + 1}/{len(items)} from {file_path.name}"
                        )

                        # Try to get the main text field
                        text = (
                            item.get("content")
                            or item.get("text")
                            or item.get("markdown")
                            or ""
                        )
                        logger.info(
                            f"Extracted {len(text)} characters of text from item {item_index}"
                        )

                        text = self.clean_text(text)
                        logger.info(f"After cleaning: {len(text)} characters")

                        if not text:
                            logger.info(f"Skipping item {item_index} - no text content")
                            continue

                        # Create a unique ID for this item
                        if isinstance(data, list):
                            item_id = f"{file_path.stem}_item_{item_index}"
                        else:
                            item_id = file_path.stem

                        # Chunk if needed
                        if len(text) > 1000:
                            logger.info(
                                f"Chunking text of length {len(text)} for {item_id}"
                            )
                            chunks = self.smart_chunk_text(text)
                            logger.info(f"Created {len(chunks)} chunks")

                            for i, chunk in enumerate(chunks):
                                processed.append(
                                    {
                                        "id": f"{item_id}_chunk_{i}",
                                        "title": item.get("title", f"Chunk {i}"),
                                        "content": chunk,
                                        "metadata": {
                                            "source_file": str(file_path),
                                            "item_index": item_index,
                                            "chunk_index": i,
                                            "total_chunks": len(chunks),
                                            "original_url": item.get("url", ""),
                                            "processed_at": datetime.now().isoformat(),
                                        },
                                    }
                                )
                        else:
                            logger.info(
                                f"Adding single item {item_id} with {len(text)} characters"
                            )
                            processed.append(
                                {
                                    "id": item_id,
                                    "title": item.get("title", item_id),
                                    "content": text,
                                    "metadata": {
                                        "source_file": str(file_path),
                                        "item_index": item_index,
                                        "original_url": item.get("url", ""),
                                        "processed_at": datetime.now().isoformat(),
                                    },
                                }
                            )

                        logger.info(
                            f"Completed processing item {item_index + 1}/{len(items)} from {file_path.name}"
                        )

                    logger.info(f"Completed processing {file_path.name}")

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")
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
