import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig


async def main():
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig()  # Default crawl run configuration

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        print(result.markdown)  # Print clean markdown content


if __name__ == "__main__":
    asyncio.run(main())
