"""Firecrawl document loader.

Built against the Firecrawl v2 API (``firecrawl-py`` >= 4.3.6), which returns
typed pydantic models (``Document``, ``CrawlJob``, ``MapData``, ``SearchData``,
``ExtractResponse``). The canonical class is :class:`FirecrawlLoader`;
:class:`FireCrawlLoader` remains as a back-compat alias for the casing used by
the (now-sunset) ``langchain-community`` loader.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any, Literal

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_firecrawl._utilities import INTEGRATION, create_client, to_dict

# Per-mode allowlists of params forwarded to the Firecrawl v2 client methods.
_SCRAPE_PARAMS = {
    "formats",
    "headers",
    "include_tags",
    "exclude_tags",
    "only_main_content",
    "timeout",
    "wait_for",
    "mobile",
    "parsers",
    "actions",
    "location",
    "skip_tls_verification",
    "remove_base64_images",
    "fast_mode",
    "block_ads",
    "proxy",
    "max_age",
    "store_in_cache",
}
_CRAWL_PARAMS = {
    "prompt",
    "exclude_paths",
    "include_paths",
    "max_discovery_depth",
    "sitemap",
    "ignore_query_parameters",
    "limit",
    "crawl_entire_domain",
    "allow_external_links",
    "allow_subdomains",
    "delay",
    "max_concurrency",
    "webhook",
    "scrape_options",
    "zero_data_retention",
    "poll_interval",
    "timeout",
}
_MAP_PARAMS = {
    "search",
    "include_subdomains",
    "limit",
    "sitemap",
    "timeout",
    "ignore_query_parameters",
    "location",
}
_EXTRACT_PARAMS = {
    "prompt",
    "schema",
    "system_prompt",
    "allow_external_links",
    "enable_web_search",
    "show_sources",
    "scrape_options",
    "ignore_invalid_urls",
    "poll_interval",
    "timeout",
}
_SEARCH_PARAMS = {
    "sources",
    "categories",
    "limit",
    "tbs",
    "location",
    "ignore_invalid_urls",
    "timeout",
    "scrape_options",
}


def _page_content(doc: Any) -> str:
    """Return the best textual content from a v2 ``Document`` (markdown first)."""
    return doc.markdown or doc.html or doc.raw_html or ""


class FirecrawlLoader(BaseLoader):
    """Firecrawl document loader integration.

    Setup:
        Install ``langchain-firecrawl`` and set the environment variable
        ``FIRECRAWL_API_KEY``.

        ```bash
        pip install -U langchain-firecrawl
        export FIRECRAWL_API_KEY="your-api-key"
        ```

    Instantiate:
        ```python
        from langchain_firecrawl import FirecrawlLoader

        loader = FirecrawlLoader(
            url="https://firecrawl.dev",
            mode="crawl",
            # other params = ...
        )
        ```

    Lazy load:
        ```python
        docs = []
        docs_lazy = loader.lazy_load()

        # async variant:
        # docs_lazy = await loader.alazy_load()

        for doc in docs_lazy:
            docs.append(doc)
        print(docs[0].page_content[:100])
        print(docs[0].metadata)
        ```

    Async load:
        ```python
        docs = await loader.aload()
        print(docs[0].page_content[:100])
        print(docs[0].metadata)
        ```
    """

    def __init__(
        self,
        url: str | None = None,
        *,
        query: str | None = None,
        api_key: str | None = None,
        api_url: str | None = None,
        mode: Literal["crawl", "scrape", "map", "extract", "search"] = "crawl",
        params: dict | None = None,
    ) -> None:
        """Initialize with API key and url.

        Args:
            url: The url to be crawled.
            query: The query to use in ``search`` mode (alternative to
                ``params["query"]``).
            api_key: The Firecrawl API key. If not specified will be read from env
                var ``FIRECRAWL_API_KEY``.
            api_url: The Firecrawl API URL. If not specified will be read from env
                var ``FIRECRAWL_API_URL`` or defaults to
                ``https://api.firecrawl.dev``.
            mode: The mode to run the loader in. Default is ``"crawl"``.
                Options include ``"scrape"`` (single url),
                ``"crawl"`` (all accessible sub pages),
                ``"map"`` (returns list of links that are semantically related),
                ``"extract"`` (extracts structured data from a page),
                ``"search"`` (search for data across the web).
            params: Additional parameters forwarded to the Firecrawl v2 client.
                See https://docs.firecrawl.dev for the full set per method.
        """
        if mode not in ("crawl", "scrape", "search", "map", "extract"):
            msg = (
                f"Invalid mode '{mode}'. "
                "Allowed: 'crawl', 'scrape', 'search', 'map', 'extract'."
            )
            raise ValueError(msg)

        if mode in ("scrape", "crawl", "map", "extract") and not url:
            msg = "Url must be provided for modes other than 'search'"
            raise ValueError(msg)
        if mode == "search" and not (query or (params and params.get("query"))):
            msg = "Query must be provided for search mode"
            raise ValueError(msg)

        self.firecrawl = create_client(api_key=api_key, api_url=api_url)
        self.url = url or ""
        self.mode = mode
        self.params = params or {}
        if query is not None:
            self.params["query"] = query

    def _kwargs(self, allowed: set[str]) -> dict[str, Any]:
        """Filter ``self.params`` to ``allowed`` keys and tag the call."""
        kwargs = {k: v for k, v in self.params.items() if k in allowed}
        kwargs["integration"] = INTEGRATION
        return kwargs

    def lazy_load(self) -> Iterator[Document]:
        """Lazily load documents from Firecrawl, one per result."""
        if self.mode == "scrape":
            yield from self._load_scrape()
        elif self.mode == "crawl":
            yield from self._load_crawl()
        elif self.mode == "map":
            yield from self._load_map()
        elif self.mode == "extract":
            yield from self._load_extract()
        elif self.mode == "search":
            yield from self._load_search()

    def _load_scrape(self) -> Iterator[Document]:
        doc = self.firecrawl.scrape(self.url, **self._kwargs(_SCRAPE_PARAMS))
        content = _page_content(doc)
        if content:
            yield Document(page_content=content, metadata=to_dict(doc.metadata))

    def _load_crawl(self) -> Iterator[Document]:
        job = self.firecrawl.crawl(self.url, **self._kwargs(_CRAWL_PARAMS))
        for doc in job.data or []:
            content = _page_content(doc)
            if content:
                yield Document(page_content=content, metadata=to_dict(doc.metadata))

    def _load_map(self) -> Iterator[Document]:
        map_data = self.firecrawl.map(self.url, **self._kwargs(_MAP_PARAMS))
        for link in map_data.links or []:
            if not link.url:
                continue
            metadata = {
                k: v
                for k, v in {
                    "title": link.title,
                    "description": link.description,
                }.items()
                if v is not None
            }
            yield Document(page_content=link.url, metadata=metadata)

    def _load_extract(self) -> Iterator[Document]:
        response = self.firecrawl.extract([self.url], **self._kwargs(_EXTRACT_PARAMS))
        data = getattr(response, "data", None)
        if data is None:
            return
        page_content = json.dumps(data, default=str, ensure_ascii=False)
        metadata: dict[str, Any] = {}
        sources = getattr(response, "sources", None)
        if sources:
            metadata["sources"] = sources
        yield Document(page_content=page_content, metadata=metadata)

    def _load_search(self) -> Iterator[Document]:
        data = self.firecrawl.search(
            query=self.params.get("query"), **self._kwargs(_SEARCH_PARAMS)
        )
        for kind, items in (
            ("web", getattr(data, "web", None)),
            ("news", getattr(data, "news", None)),
            ("images", getattr(data, "images", None)),
        ):
            for item in items or []:
                url = getattr(item, "url", None)
                title = getattr(item, "title", None)
                description = getattr(item, "description", None)
                content = description or title or url or ""
                if not content:
                    continue
                metadata = {
                    k: v
                    for k, v in {
                        "url": url,
                        "title": title,
                        "category": getattr(item, "category", None),
                        "type": kind,
                    }.items()
                    if v is not None
                }
                yield Document(page_content=content, metadata=metadata)


#: Back-compat alias matching the (sunset) community package's class name.
FireCrawlLoader = FirecrawlLoader
