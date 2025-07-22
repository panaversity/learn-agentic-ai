import asyncio

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CacheMode, CrawlerRunConfig


async def main():
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=10,
        excluded_tags=["form", "header"],
        exclude_external_links=True,
        process_iframes=True,
        remove_overlay_elements=True,
        cache_mode=CacheMode.ENABLED,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com", config=run_config)
        if result.success:
            print("Content:", result.markdown[:500])  # First 500 chars
            for image in result.media["images"]:
                print(f"Found image: {image['src']}")
            for link in result.links["internal"]:
                print(f"Internal link: {link['href']}")
        else:
            print(f"Crawl failed: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
