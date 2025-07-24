import asyncio
import json
import os

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "crawlers")
SUMMARY_PATH = os.path.join(DATA_DIR, "summary.json")


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
            # Sanitize filename from URL
            safe_url = (
                result.url.replace("https://", "")
                .replace("http://", "")
                .replace("/", "_")
            )
            md_path = os.path.join(DATA_DIR, f"{safe_url}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result.markdown or "")
            summary.append(
                {
                    "url": result.url,
                    "file": md_path,
                    "success": result.success,
                    "status_code": result.status_code,
                    "depth": result.metadata.get("depth", 0),
                    "title": getattr(result, "title", None),
                }
            )
        # Write summary JSON
        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Saved {len(results)} markdown files and summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
