"""Standard LangChain integration tests for the Firecrawl tools.

These are the ``langchain-tests`` ``ToolsIntegrationTests``: they invoke each tool
against the live Firecrawl API, directly and through a ``ToolCall``, sync and
async. Scrape and search are covered because they return quickly and cost
little; crawl, map and extract stay in the hand-written tests.
"""

import os
from typing import Any

import pytest
from langchain_tests.integration_tests import ToolsIntegrationTests

from langchain_firecrawl import FirecrawlScrape, FirecrawlSearch

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIRECRAWL_API_KEY"),
    reason="FIRECRAWL_API_KEY not set",
)


class TestFirecrawlScrapeIntegration(ToolsIntegrationTests):
    """Standard integration tests for `FirecrawlScrape`."""

    @property
    def tool_constructor(self) -> type[FirecrawlScrape]:
        """The tool class under test."""
        return FirecrawlScrape

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor (the key comes from the env)."""
        return {}

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"url": "https://example.com", "formats": ["markdown"]}


class TestFirecrawlSearchIntegration(ToolsIntegrationTests):
    """Standard integration tests for `FirecrawlSearch`."""

    @property
    def tool_constructor(self) -> type[FirecrawlSearch]:
        """The tool class under test."""
        return FirecrawlSearch

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor (the key comes from the env)."""
        return {}

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"query": "firecrawl web scraping", "limit": 3}
