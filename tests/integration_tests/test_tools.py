"""Integration tests for the Firecrawl tools (gated on `FIRECRAWL_API_KEY`)."""

import os

import pytest

from langchain_firecrawl import FirecrawlMap, FirecrawlScrape, FirecrawlSearch

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIRECRAWL_API_KEY"),
    reason="FIRECRAWL_API_KEY not set",
)


def test_scrape_tool() -> None:
    """Scrape a known-stable page and assert markdown is returned."""
    tool = FirecrawlScrape()
    result = tool.invoke({"url": "https://example.com", "formats": ["markdown"]})
    assert isinstance(result, dict), result  # str means error
    assert result["markdown"]


def test_search_tool() -> None:
    """Search returns a non-empty list of results."""
    tool = FirecrawlSearch()
    result = tool.invoke({"query": "firecrawl web scraping", "limit": 3})
    assert isinstance(result, list), result
    assert result


def test_map_tool() -> None:
    """Map returns a non-empty list of links."""
    tool = FirecrawlMap()
    result = tool.invoke({"url": "https://firecrawl.dev", "limit": 5})
    assert isinstance(result, list), result
    assert result
