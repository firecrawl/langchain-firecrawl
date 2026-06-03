"""Unit tests for `FirecrawlLoader` (mocked client, no network)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from langchain_firecrawl import FireCrawlLoader, FirecrawlLoader


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch the loader's client factory to return a mock client."""
    client = MagicMock()
    monkeypatch.setattr(
        "langchain_firecrawl.document_loaders.create_client",
        lambda **_: client,
    )
    return client


def _doc(markdown: str, metadata: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        markdown=markdown, html=None, raw_html=None, metadata=metadata
    )


def test_alias_is_canonical_class() -> None:
    """`FireCrawlLoader` is an alias of `FirecrawlLoader`."""
    assert FireCrawlLoader is FirecrawlLoader


def test_scrape_mode(mock_client: MagicMock) -> None:
    """Scrape mode yields one document tagged with the integration."""
    mock_client.scrape.return_value = _doc(
        "# Hello", {"source_url": "https://example.com", "title": "T"}
    )
    loader = FirecrawlLoader(url="https://example.com", mode="scrape")
    docs = list(loader.lazy_load())

    assert len(docs) == 1
    assert docs[0].page_content == "# Hello"
    assert docs[0].metadata["source_url"] == "https://example.com"
    assert mock_client.scrape.call_args.kwargs["integration"] == "langchain"


def test_crawl_mode(mock_client: MagicMock) -> None:
    """Crawl mode yields one document per page in `job.data`."""
    mock_client.crawl.return_value = SimpleNamespace(
        status="completed",
        data=[
            _doc("page one", {"source_url": "https://example.com/1"}),
            _doc("page two", {"source_url": "https://example.com/2"}),
        ],
    )
    loader = FirecrawlLoader(url="https://example.com", mode="crawl")
    docs = list(loader.lazy_load())

    assert [d.page_content for d in docs] == ["page one", "page two"]
    assert mock_client.crawl.call_args.kwargs["integration"] == "langchain"


def test_map_mode(mock_client: MagicMock) -> None:
    """Map mode yields one document per discovered link."""
    mock_client.map.return_value = SimpleNamespace(
        links=[
            SimpleNamespace(
                url="https://example.com/a", title="A", description="first"
            ),
            SimpleNamespace(url="https://example.com/b", title=None, description=None),
        ]
    )
    loader = FirecrawlLoader(url="https://example.com", mode="map")
    docs = list(loader.lazy_load())

    assert docs[0].page_content == "https://example.com/a"
    assert docs[0].metadata == {"title": "A", "description": "first"}
    assert docs[1].page_content == "https://example.com/b"
    assert docs[1].metadata == {}


def test_extract_mode(mock_client: MagicMock) -> None:
    """Extract mode serializes the structured data into page content."""
    mock_client.extract.return_value = SimpleNamespace(
        data={"title": "Firecrawl", "price": 0}, sources=None
    )
    loader = FirecrawlLoader(url="https://example.com", mode="extract")
    docs = list(loader.lazy_load())

    assert len(docs) == 1
    assert "Firecrawl" in docs[0].page_content
    args, _ = mock_client.extract.call_args
    assert args[0] == ["https://example.com"]
    assert mock_client.extract.call_args.kwargs["integration"] == "langchain"


def test_search_mode(mock_client: MagicMock) -> None:
    """Search mode flattens web/news/images into documents."""
    mock_client.search.return_value = SimpleNamespace(
        web=[
            SimpleNamespace(
                url="https://example.com",
                title="Example",
                description="An example result",
                category=None,
            )
        ],
        news=None,
        images=None,
    )
    loader = FirecrawlLoader(mode="search", query="example")
    docs = list(loader.lazy_load())

    assert len(docs) == 1
    assert docs[0].page_content == "An example result"
    assert docs[0].metadata["type"] == "web"
    assert mock_client.search.call_args.kwargs["query"] == "example"
    assert mock_client.search.call_args.kwargs["integration"] == "langchain"


def test_invalid_mode_raises(mock_client: MagicMock) -> None:
    """An unknown mode is rejected at construction time."""
    with pytest.raises(ValueError, match="Invalid mode"):
        FirecrawlLoader(url="https://example.com", mode="bogus")  # type: ignore[arg-type]


def test_url_required_for_scrape(mock_client: MagicMock) -> None:
    """A URL is required for non-search modes."""
    with pytest.raises(ValueError, match="Url must be provided"):
        FirecrawlLoader(mode="scrape")


def test_query_required_for_search(mock_client: MagicMock) -> None:
    """A query is required for search mode."""
    with pytest.raises(ValueError, match="Query must be provided"):
        FirecrawlLoader(mode="search")
