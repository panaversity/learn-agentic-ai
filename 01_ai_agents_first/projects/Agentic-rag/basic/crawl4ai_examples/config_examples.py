import asyncio

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
)


async def main():
    # 1. BrowserConfig: Controls browser launch and behavior
    browser_conf = BrowserConfig(
        browser_type="chromium",  # Options: 'chromium', 'firefox', 'webkit'
        headless=True,  # Run browser in headless mode
        viewport_width=1280,
        viewport_height=720,
        verbose=True,  # Print extra logs for debugging
        # proxy_config={"server": "http://proxy.example.com:8080"},  # Uncomment to use a proxy
    )

    # 2. LLMConfig: Configure LLM provider (optional, for LLM-powered extraction)
    llm_config = LLMConfig(
        provider="openai/gpt-4o-mini",  # LLM provider
        api_token="env:OPENAI_API_KEY",  # Reads from environment variable
        # base_url="https://api.openai.com/v1"   # Uncomment for custom endpoint
    )

    # 3. CrawlerRunConfig: Controls crawl operation
    run_conf = CrawlerRunConfig(
        word_count_threshold=100,  # Minimum words per content block
        cache_mode=CacheMode.ENABLED,  # Use cache if available
        wait_for="css:.main-loaded",  # Wait for this CSS selector before extracting
        verbose=True,  # Print crawl details
        # Add extraction_strategy, markdown_generator, or LLM content filter as needed
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun("https://example.com", config=run_conf)
        if result.success:
            print("Extracted markdown:")
            print(result.markdown[:500])
        else:
            print("Crawl failed:", result.error_message)


if __name__ == "__main__":
    asyncio.run(main())
