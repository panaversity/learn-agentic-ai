import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


async def main():
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=2, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://example.com", config=config)
        print(f"Crawled {len(results)} pages in total")
        for result in results[:3]:  # Show first 3 results
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
