"""Integration tests for the Firecrawl tools (gated on `FIRECRAWL_API_KEY`)."""

import os

import pytest

from langchain_firecrawl import (
    FirecrawlAgent,
    FirecrawlBatchScrape,
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


def test_batch_scrape_tool() -> None:
    """Batch scrape returns one page per URL."""
    tool = FirecrawlBatchScrape()
    result = tool.invoke(
        {"urls": ["https://example.com", "https://example.org"], "wait_timeout": 120}
    )
    assert isinstance(result, list), result
    assert len(result) == 2
    assert all(page["markdown"] for page in result)


def test_agent_tool() -> None:
    """Agent returns data for a small, credit-capped prompt."""
    tool = FirecrawlAgent()
    result = tool.invoke(
        {
            "prompt": "What is the main heading of this page?",
            "urls": ["https://example.com"],
            "max_credits": 50,
            "timeout": 300,
        }
    )
    assert not isinstance(result, str), result
    assert result
