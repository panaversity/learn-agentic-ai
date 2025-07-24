import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import BrowserConfig

# NOTE: LLM integration specifics may require additional config or API keys


async def main():
    browser_config = BrowserConfig()
    # Example: Add LLM-related config if available in your crawl4ai version
    run_config = CrawlerRunConfig(
        # llm_config=YourLLMConfig(...),  # Uncomment and configure as needed
        verbose=True
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun("https://example.com", config=run_config)
        print(result.markdown)
        # If LLM extraction is enabled, print LLM-augmented results here


if __name__ == "__main__":
    asyncio.run(main())
