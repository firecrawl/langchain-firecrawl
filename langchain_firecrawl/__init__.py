"""LangChain integration for Firecrawl."""

from importlib import metadata

from langchain_firecrawl.document_loaders import FireCrawlLoader, FirecrawlLoader
from langchain_firecrawl.tools import (
    FirecrawlCrawl,
    FirecrawlExtract,
    FirecrawlFindTools,
    FirecrawlMap,
    FirecrawlProviderTool,
    FirecrawlScrape,
    FirecrawlSearch,
)

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
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
