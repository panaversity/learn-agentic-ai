import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import BrowserConfig


async def main():
    urls = ["https://example.com", "https://example.org", "https://example.net"]
    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            result = await crawler.arun(url, config=run_config)
            print(f"Crawled {url}:")
            print(result.markdown[:300])
            print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
