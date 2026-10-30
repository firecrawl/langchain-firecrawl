"""Integration tests for the Firecrawl tools (gated on `FIRECRAWL_API_KEY`)."""

import os

import pytest

from langchain_firecrawl import (
    FirecrawlExtract,
    FirecrawlMap,
    FirecrawlScrape,
    FirecrawlSearch,
)

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


def test_extract_tool_single_url() -> None:
    """Extract with one URL returns that page's JSON."""
    tool = FirecrawlExtract()
    schema = {"type": "object", "properties": {"title": {"type": "string"}}}
    result = tool.invoke({"urls": ["https://example.com"], "schema": schema})
    assert isinstance(result, dict), result
    assert result.get("title")


def test_extract_tool_multiple_urls() -> None:
    """Extract with several URLs returns a url -> json mapping."""
    tool = FirecrawlExtract()
    urls = ["https://example.com", "https://example.org"]
    result = tool.invoke({"urls": urls, "prompt": "Extract the page title as 'title'."})
    assert isinstance(result, dict), result
    assert set(result) == set(urls)
    assert all(isinstance(v, dict) for v in result.values())
