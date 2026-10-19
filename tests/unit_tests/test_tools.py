"""Unit tests for the Firecrawl tools (mocked client, no network)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from langchain_firecrawl import (
    FirecrawlAgent,
    FirecrawlBatchScrape,
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


def test_batch_scrape_tool_returns_page_list() -> None:
    """Batch scrape returns one dict per page and forwards options."""
    tool = FirecrawlBatchScrape(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.batch_scrape.return_value = SimpleNamespace(
        data=[_doc("one", {"source_url": "https://a.example"}), _doc("two", {})]
    )

    result = tool.invoke(
        {
            "urls": ["https://a.example", "https://b.example"],
            "formats": ["markdown"],
            "max_concurrency": 2,
            "wait_timeout": 60,
        }
    )

    assert result == [
        {"markdown": "one", "metadata": {"source_url": "https://a.example"}},
        {"markdown": "two", "metadata": {}},
    ]
    call = tool.client.batch_scrape.call_args
    assert call.args[0] == ["https://a.example", "https://b.example"]
    assert call.kwargs["formats"] == ["markdown"]
    assert call.kwargs["max_concurrency"] == 2
    assert call.kwargs["wait_timeout"] == 60
    assert call.kwargs["integration"] == "langchain"
    assert "mobile" not in call.kwargs


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


def test_agent_tool_returns_data_and_tags_call() -> None:
    """Agent returns the result `data` and forwards its options."""
    tool = FirecrawlAgent(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.agent.return_value = SimpleNamespace(
        id="job-1", status="completed", data={"plan": "Free"}
    )

    result = tool.invoke(
        {
            "prompt": "Find the cheapest plan",
            "urls": ["https://example.com"],
            "max_credits": 50,
            "model": "spark-1-mini",
        }
    )

    assert result == {"plan": "Free"}
    call = tool.client.agent.call_args
    assert call.args[0] == ["https://example.com"]
    assert call.kwargs["prompt"] == "Find the cheapest plan"
    assert call.kwargs["max_credits"] == 50
    assert call.kwargs["model"] == "spark-1-mini"
    assert call.kwargs["integration"] == "langchain"
    assert "schema" not in call.kwargs


def test_agent_tool_without_urls_and_without_data() -> None:
    """Agent works without URLs and falls back to the status payload."""
    tool = FirecrawlAgent(api_key="fc-test")  # type: ignore[arg-type]
    tool.client = MagicMock()
    tool.client.agent.return_value = SimpleNamespace(
        id="job-2", status="processing", data=None, error=None
    )

    result = tool.invoke({"prompt": "Research Firecrawl"})

    assert result == {"id": "job-2", "status": "processing"}
    assert tool.client.agent.call_args.args[0] is None


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
        (
            FirecrawlBatchScrape,
            "batch_scrape",
            {"urls": ["https://example.com"]},
        ),
        (FirecrawlMap, "map", {"url": "https://example.com"}),
        (FirecrawlAgent, "agent", {"prompt": "x"}),
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
