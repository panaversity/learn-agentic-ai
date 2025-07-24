# crawl4ai Examples

This directory contains hands-on code samples and resources for using [crawl4ai](https://pypi.org/project/crawl4ai/), a modern AI-powered web crawler for Python.

## What is crawl4ai?

crawl4ai is a powerful, flexible, and intelligent web crawling library designed for large-scale data extraction. It integrates with LLMs, supports advanced anti-bot features, and is suitable for both simple and complex scraping tasks.

## Official Resources & Documentation

- [Official Website](https://crawl4ai.com/)
- [GitHub Repository](https://github.com/unclecode/crawl4ai)
- [PyPI: crawl4ai](https://pypi.org/project/crawl4ai/)
- [YouTube Tutorial](https://youtu.be/xo3qK6Hg9AA)

## Helpful Videos

- [Crawl4AI Tutorial 1](https://www.youtube.com/watch?v=lpOb1bQO7aM)
- [Crawl4AI Tutorial 2](https://www.youtube.com/watch?v=Osl4NgAXvRk)

## Example Scripts

- [simple_crawling.py](./simple_crawling.py): Basic crawl of a single page and print markdown content.
- [custom_crawl_options.py](./custom_crawl_options.py): Customize crawl options (content filtering, tag exclusion, iframes, etc.).
- [error_handling.py](./error_handling.py): Graceful error handling for failed crawls.
- [deep_crawling.py](./deep_crawling.py): Deep crawl using BFS strategy, print URLs and depth.
- [bestfirst_crawling.py](./bestfirst_crawling.py): Prioritized deep crawling with BestFirstCrawlingStrategy and KeywordRelevanceScorer.
- [llm_integration.py](./llm_integration.py): Template for LLM-powered extraction (edit with your LLM config as needed).
- [proxy_usage.py](./proxy_usage.py): Use proxies for anti-bot evasion.
- [multi_url_crawling.py](./multi_url_crawling.py): Crawl multiple URLs in sequence.
- [config_examples.py](./config_examples.py): Demonstrates BrowserConfig, CrawlerRunConfig, and LLMConfig usage.
- [deep_crawl_to_files.py](./deep_crawl_to_files.py): Deep crawl and save markdown for each URL to data/crawlers, with a summary JSON file.

> **Contributions welcome!** Add your own examples or tips to help others learn crawl4ai.

---
