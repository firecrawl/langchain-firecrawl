"""Unit tests for the Firecrawl tools (mocked client, no network)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from langchain_firecrawl import (
    FirecrawlCrawl,
    FirecrawlExtract,
    FirecrawlMap,
    FirecrawlScrape,
    FirecrawlSearch,
)


def _doc(markdown: str, metadata: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        markdown=markdown, html=None, raw_html=None, metadata=metadata
    )


def test_scrape_tool_returns_markdown_and_tags_call() -> None:
    """Scrape returns markdown + metadata and forwards the integration tag."""
    tool = FirecrawlScrape(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.scrape.return_value = _doc(
        "# Hi", {"source_url": "https://example.com"}
    )

    result = tool.invoke({"url": "https://example.com"})

    assert result == {
        "markdown": "# Hi",
        "metadata": {"source_url": "https://example.com"},
    }
    call = tool.client.scrape.call_args
    assert call.args[0] == "https://example.com"
    assert call.kwargs["integration"] == "langchain"
    # None-valued optional params are dropped before the call.
    assert "formats" not in call.kwargs


def test_scrape_tool_forwards_options() -> None:
    """Explicit options are forwarded to the client."""
    tool = FirecrawlScrape(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.scrape.return_value = _doc("x", {})

    tool.invoke({"url": "https://example.com", "formats": ["markdown"], "mobile": True})

    kwargs = tool.client.scrape.call_args.kwargs
    assert kwargs["formats"] == ["markdown"]
    assert kwargs["mobile"] is True


def test_crawl_tool_returns_page_list() -> None:
    """Crawl returns one dict per page in `job.data`."""
    tool = FirecrawlCrawl(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.crawl.return_value = SimpleNamespace(
        data=[_doc("one", {}), _doc("two", {})]
    )

    result = tool.invoke({"url": "https://example.com", "limit": 2})

    assert [page["markdown"] for page in result] == ["one", "two"]
    kwargs = tool.client.crawl.call_args.kwargs
    assert kwargs["limit"] == 2
    assert kwargs["integration"] == "langchain"


def test_map_tool_returns_links() -> None:
    """Map returns link dicts and skips entries without a URL."""
    tool = FirecrawlMap(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.map.return_value = SimpleNamespace(
        links=[
            SimpleNamespace(url="https://example.com/a", title="A", description=None),
            SimpleNamespace(url=None, title=None, description=None),
        ]
    )

    result = tool.invoke({"url": "https://example.com"})

    assert result == [{"url": "https://example.com/a", "title": "A"}]
    assert tool.client.map.call_args.kwargs["integration"] == "langchain"


def test_extract_tool_returns_data() -> None:
    """Extract returns the structured `data` payload."""
    tool = FirecrawlExtract(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.extract.return_value = SimpleNamespace(data={"title": "Firecrawl"})

    result = tool.invoke({"urls": ["https://example.com"], "prompt": "Get the title"})

    assert result == {"title": "Firecrawl"}
    call = tool.client.extract.call_args
    assert call.args[0] == ["https://example.com"]
    assert call.kwargs["prompt"] == "Get the title"
    assert call.kwargs["integration"] == "langchain"


def test_search_tool_flattens_sources() -> None:
    """Search flattens web/news/images results and stamps the source type."""
    tool = FirecrawlSearch(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.search.return_value = SimpleNamespace(
        web=[
            SimpleNamespace(
                url="https://example.com",
                title="Example",
                description="d",
                category=None,
            )
        ],
        news=None,
        images=None,
    )

    result = tool.invoke({"query": "example", "limit": 5})

    assert result[0]["url"] == "https://example.com"
    assert result[0]["type"] == "web"
    call = tool.client.search.call_args
    assert call.args[0] == "example"
    assert call.kwargs["limit"] == 5
    assert call.kwargs["integration"] == "langchain"


@pytest.mark.parametrize(
    ("tool_cls", "method", "params"),
    [
        (FirecrawlScrape, "scrape", {"url": "https://example.com"}),
        (FirecrawlMap, "map", {"url": "https://example.com"}),
        (FirecrawlSearch, "search", {"query": "x"}),
    ],
)
def test_tool_returns_error_string_on_exception(
    tool_cls: type, method: str, params: dict[str, Any]
) -> None:
    """Tools return a string (not raise) when the client errors."""
    tool = tool_cls(api_key="fc-test")
    tool.client = MagicMock()
    getattr(tool.client, method).side_effect = RuntimeError("boom")

    result = tool.invoke(params)

    assert isinstance(result, str)
    assert "boom" in result
