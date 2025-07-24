import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer


async def main():
    keyword_scorer = KeywordRelevanceScorer(
        keywords=["crawl", "example", "async", "configuration"], weight=0.7
    )
    config = CrawlerRunConfig(
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=2, url_scorer=keyword_scorer
        ),
        stream=True,
    )
    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun("https://example.com", config=config):
            score = result.metadata.get("score", 0)
            print(f"Score: {score:.2f} | {result.url}")


if __name__ == "__main__":
    asyncio.run(main())
