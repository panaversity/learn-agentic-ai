import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import BrowserConfig


async def main():
    # Example proxy config (replace with your proxy details)
    browser_config = BrowserConfig(proxy_server="http://your-proxy-server:port")
    run_config = CrawlerRunConfig()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun("https://example.com", config=run_config)
        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
