import asyncio
import json
import os
import re
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "crawlers_json")
SUMMARY_JSON = os.path.join(DATA_DIR, "scraped_content_summary.json")


def url_to_filename(url: str) -> str:
    """Create a safe filename from a URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "home"
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", path)
    return f"{slug}.json"


async def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=2, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://example.com", config=config)
        summary = []
        for result in results:
            url = getattr(result, "url", "unknown")
            # Use robust filename sanitizer
            filename = url_to_filename(url)
            json_path = os.path.join(DATA_DIR, filename)
            # Prepare data to store
            data = {
                "url": url,
                "success": getattr(result, "success", False),
                "status_code": getattr(result, "status_code", None),
                "depth": getattr(result, "metadata", {}).get("depth", 0),
                "title": getattr(result, "title", None),
                "cleaned_html": getattr(result, "cleaned_html", None),
                "markdown": getattr(result, "markdown", None),
                "chunks": getattr(result, "chunks", None),
                "metadata": getattr(result, "metadata", {}),
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved: {json_path}")
            summary.append(data)
        # Save a summary file with all results
        with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Crawled {len(results)} pages and saved JSON files to {DATA_DIR}")
        print(f"Summary written to {SUMMARY_JSON} ({len(summary)} entries).")


if __name__ == "__main__":
    asyncio.run(main())
