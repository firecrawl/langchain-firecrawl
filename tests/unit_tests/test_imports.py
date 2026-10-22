"""Unit tests for imports in `langchain_firecrawl`."""

from langchain_firecrawl import __all__

EXPECTED_ALL = [
    "FireCrawlLoader",
    "FirecrawlCrawl",
    "FirecrawlExtract",
    "FirecrawlFindTools",
    "FirecrawlLoader",
    "FirecrawlMap",
    "FirecrawlProviderTool",
    "FirecrawlScrape",
    "FirecrawlSearch",
    "__version__",
]


def test_all_imports() -> None:
    """Test that all expected names are exported in `__all__`."""
    assert sorted(EXPECTED_ALL) == sorted(__all__)
