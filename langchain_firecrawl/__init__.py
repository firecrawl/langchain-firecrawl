"""LangChain integration for Firecrawl."""

from importlib import metadata

from langchain_firecrawl.document_loaders import FireCrawlLoader, FirecrawlLoader
from langchain_firecrawl.tools import (
    FirecrawlAgent,
    FirecrawlBatchScrape,
    FirecrawlCrawl,
    FirecrawlExtract,
    FirecrawlMap,
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
    "FirecrawlAgent",
    "FirecrawlBatchScrape",
    "FirecrawlCrawl",
    "FirecrawlExtract",
    "FirecrawlLoader",
    "FirecrawlMap",
    "FirecrawlScrape",
    "FirecrawlSearch",
    "__version__",
]
