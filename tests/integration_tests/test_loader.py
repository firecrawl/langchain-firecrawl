"""Integration tests for `FirecrawlLoader` (gated on `FIRECRAWL_API_KEY`)."""

import os

import pytest
from langchain_core.documents import Document

from langchain_firecrawl import FirecrawlLoader

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIRECRAWL_API_KEY"),
    reason="FIRECRAWL_API_KEY not set",
)


def test_loader_scrape() -> None:
    """Scrape mode returns at least one populated `Document`."""
    loader = FirecrawlLoader(url="https://example.com", mode="scrape")
    docs = loader.load()
    assert docs
    assert isinstance(docs[0], Document)
    assert docs[0].page_content


def test_loader_map() -> None:
    """Map mode returns `Document`s whose content is a URL."""
    loader = FirecrawlLoader(
        url="https://firecrawl.dev", mode="map", params={"limit": 5}
    )
    docs = loader.load()
    assert docs
    assert docs[0].page_content.startswith("http")
