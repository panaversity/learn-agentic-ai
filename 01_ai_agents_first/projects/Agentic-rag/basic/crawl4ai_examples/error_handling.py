import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig


async def main():
    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        if not result.success:
            print(f"Crawl failed: {result.error_message}")
            print(f"Status code: {result.status_code}")
        else:
            print("Crawl succeeded!")
            print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
