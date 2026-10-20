# langchain-firecrawl

[![PyPI - Version](https://img.shields.io/pypi/v/langchain-firecrawl?label=%20)](https://pypi.org/project/langchain-firecrawl/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langchain-firecrawl)](https://opensource.org/licenses/MIT)

This package contains the LangChain integration with [Firecrawl](https://www.firecrawl.dev),
an API that turns websites into clean, LLM-ready data. It lets you scrape, crawl,
map, extract structured data from, and search the web — as a document loader or
as agent tools.

## Quick Install

```bash
pip install langchain-firecrawl
```

Get an API key from [firecrawl.dev](https://www.firecrawl.dev) and set it as the
`FIRECRAWL_API_KEY` environment variable (or pass `api_key=...`).

```bash
export FIRECRAWL_API_KEY="fc-your-api-key"
```

## Document loader

`FirecrawlLoader` loads web content as LangChain `Document`s. Pick a `mode`:
`scrape` (one page), `crawl` (a whole site), `map` (discover URLs), `extract`
(structured data), or `search` (web search).

```python
from langchain_firecrawl import FirecrawlLoader

loader = FirecrawlLoader(url="https://www.firecrawl.dev", mode="scrape")
docs = loader.load()
print(docs[0].page_content[:200])
print(docs[0].metadata)
```

## Tools

Each Firecrawl capability is also available as a `BaseTool` you can bind to an
agent:

```python
from langchain_firecrawl import (
    FirecrawlScrape,
    FirecrawlCrawl,
    FirecrawlMap,
    FirecrawlExtract,
    FirecrawlSearch,
)

scrape = FirecrawlScrape()
result = scrape.invoke({"url": "https://www.firecrawl.dev"})
print(result["markdown"])

search = FirecrawlSearch()
print(search.invoke({"query": "best web scraping libraries", "limit": 5}))
```

## Documentation

- Firecrawl LangChain guide: [docs.firecrawl.dev](https://docs.firecrawl.dev/developer-guides/llm-sdks-and-frameworks/langchain)
- Firecrawl docs: [docs.firecrawl.dev](https://docs.firecrawl.dev)
- Firecrawl homepage: [firecrawl.dev](https://www.firecrawl.dev)
