"""Tools for the Firecrawl v2 API.

Each capability of the Firecrawl v2 API is exposed as a ``BaseTool`` so it can be
bound to an agent: scrape, crawl, map, extract, and search. Responses are the
typed pydantic models returned by ``firecrawl-py`` >= 4.3.6, normalized into
JSON-friendly dicts. Every call is tagged with ``integration="langchain"`` for
attribution (see :mod:`langchain_firecrawl._utilities`).
"""

from __future__ import annotations

from typing import Any, Literal

from firecrawl import Firecrawl  # type: ignore[import-untyped]
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field, SecretStr, model_validator

from langchain_firecrawl._utilities import (
    INTEGRATION,
    clean_params,
    initialize_client,
    to_dict,
)


def _page_to_dict(doc: Any) -> dict[str, Any]:
    """Normalize a v2 ``Document`` into ``{"markdown", "metadata"}``."""
    content = (
        getattr(doc, "markdown", None)
        or getattr(doc, "html", None)
        or getattr(doc, "raw_html", None)
        or ""
    )
    return {"markdown": content, "metadata": to_dict(getattr(doc, "metadata", None))}


def _search_results(data: Any) -> list[dict[str, Any]]:
    """Flatten a v2 ``SearchData`` (web/news/images) into result dicts."""
    results: list[dict[str, Any]] = []
    for kind in ("web", "news", "images"):
        for item in getattr(data, kind, None) or []:
            entry = to_dict(item)
            entry["type"] = kind
            results.append(entry)
    return results


class _FirecrawlBaseTool(BaseTool):
    """Shared configuration for Firecrawl tools (client + credentials)."""

    client: Firecrawl = Field(default=None)  # type: ignore[assignment]
    api_key: SecretStr = Field(default=SecretStr(""))
    api_url: str | None = None
    integration: str = INTEGRATION
    """Attribution tag sent as ``integration`` on every call."""

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: dict) -> Any:
        """Resolve credentials and instantiate the Firecrawl client."""
        return initialize_client(values)


class FirecrawlScrape(_FirecrawlBaseTool):
    """Scrape a single URL and return its content as clean markdown.

    Setup:
        Install ``langchain-firecrawl`` and set ``FIRECRAWL_API_KEY``.

        ```bash
        pip install -U langchain-firecrawl
        export FIRECRAWL_API_KEY="your-api-key"
        ```

    Instantiation:
        ```python
        from langchain_firecrawl import FirecrawlScrape

        tool = FirecrawlScrape()
        tool.invoke({"url": "https://firecrawl.dev"})
        ```
    """

    name: str = "firecrawl_scrape"
    description: str = (
        "Scrape a single web page and return its content as clean, "
        "LLM-ready markdown along with page metadata. "
        "Input should be a URL."
    )

    def _run(
        self,
        url: str,
        formats: list[str] | None = None,
        only_main_content: bool | None = None,  # noqa: FBT001
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
        wait_for: int | None = None,
        timeout: int | None = None,
        mobile: bool | None = None,  # noqa: FBT001
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> dict[str, Any] | str:
        """Scrape ``url``.

        Args:
            url: The URL to scrape.
            formats: Output formats to request (e.g. ``["markdown"]``).
            only_main_content: Whether to return only the main page content.
            include_tags: HTML tags to include.
            exclude_tags: HTML tags to exclude.
            wait_for: Milliseconds to wait for the page to render.
            timeout: Request timeout in milliseconds.
            mobile: Whether to emulate a mobile device.
            run_manager: The run manager for callbacks.

        Returns:
            A dict with ``markdown`` and ``metadata``, or an error string.
        """
        try:
            doc = self.client.scrape(
                url,
                **clean_params(
                    {
                        "formats": formats,
                        "only_main_content": only_main_content,
                        "include_tags": include_tags,
                        "exclude_tags": exclude_tags,
                        "wait_for": wait_for,
                        "timeout": timeout,
                        "mobile": mobile,
                    },
                    self.integration,
                ),
            )
            return _page_to_dict(doc)
        except Exception as e:
            return repr(e)


class FirecrawlCrawl(_FirecrawlBaseTool):
    """Crawl a site starting from a URL and return each page as markdown.

    Setup:
        Install ``langchain-firecrawl`` and set ``FIRECRAWL_API_KEY``.

    Instantiation:
        ```python
        from langchain_firecrawl import FirecrawlCrawl

        tool = FirecrawlCrawl()
        tool.invoke({"url": "https://firecrawl.dev", "limit": 10})
        ```
    """

    name: str = "firecrawl_crawl"
    description: str = (
        "Crawl a website starting from a URL, following accessible sub-pages, "
        "and return each page's content as clean markdown. "
        "Input should be a URL; use 'limit' to cap the number of pages."
    )

    def _run(
        self,
        url: str,
        limit: int | None = None,
        prompt: str | None = None,
        include_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
        max_discovery_depth: int | None = None,
        crawl_entire_domain: bool | None = None,  # noqa: FBT001
        allow_external_links: bool | None = None,  # noqa: FBT001
        poll_interval: int | None = None,
        timeout: int | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> list[dict[str, Any]] | str:
        """Crawl from ``url``.

        Args:
            url: The URL to start crawling from.
            limit: Maximum number of pages to crawl.
            prompt: Natural-language instruction to steer the crawl.
            include_paths: URL path patterns to include.
            exclude_paths: URL path patterns to exclude.
            max_discovery_depth: Maximum link-discovery depth.
            crawl_entire_domain: Whether to crawl the entire domain.
            allow_external_links: Whether to follow links to other domains.
            poll_interval: Seconds between status polls.
            timeout: Request timeout in seconds.
            run_manager: The run manager for callbacks.

        Returns:
            A list of page dicts (``markdown`` + ``metadata``), or an error string.
        """
        try:
            job = self.client.crawl(
                url,
                **clean_params(
                    {
                        "limit": limit,
                        "prompt": prompt,
                        "include_paths": include_paths,
                        "exclude_paths": exclude_paths,
                        "max_discovery_depth": max_discovery_depth,
                        "crawl_entire_domain": crawl_entire_domain,
                        "allow_external_links": allow_external_links,
                        "poll_interval": poll_interval,
                        "timeout": timeout,
                    },
                    self.integration,
                ),
            )
            return [_page_to_dict(doc) for doc in getattr(job, "data", None) or []]
        except Exception as e:
            return repr(e)


class FirecrawlMap(_FirecrawlBaseTool):
    """Map a site and return the list of discovered, related URLs.

    Setup:
        Install ``langchain-firecrawl`` and set ``FIRECRAWL_API_KEY``.

    Instantiation:
        ```python
        from langchain_firecrawl import FirecrawlMap

        tool = FirecrawlMap()
        tool.invoke({"url": "https://firecrawl.dev"})
        ```
    """

    name: str = "firecrawl_map"
    description: str = (
        "Map a website and return a list of URLs that are semantically related "
        "to the input URL. Useful for discovering a site's pages quickly. "
        "Input should be a URL."
    )

    def _run(
        self,
        url: str,
        search: str | None = None,
        limit: int | None = None,
        sitemap: Literal["skip", "include", "only"] | None = None,
        include_subdomains: bool | None = None,  # noqa: FBT001
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> list[dict[str, Any]] | str:
        """Map ``url``.

        Args:
            url: The URL to map.
            search: Optional query to filter the discovered links.
            limit: Maximum number of links to return.
            sitemap: How to use the site's sitemap (``skip``/``include``/``only``).
            include_subdomains: Whether to include links on subdomains.
            run_manager: The run manager for callbacks.

        Returns:
            A list of link dicts (``url`` plus optional ``title``/``description``),
            or an error string.
        """
        try:
            map_data = self.client.map(
                url,
                **clean_params(
                    {
                        "search": search,
                        "limit": limit,
                        "sitemap": sitemap,
                        "include_subdomains": include_subdomains,
                    },
                    self.integration,
                ),
            )
            return [
                to_dict(link)
                for link in getattr(map_data, "links", None) or []
                if getattr(link, "url", None)
            ]
        except Exception as e:
            return repr(e)


class FirecrawlExtract(_FirecrawlBaseTool):
    """Extract structured data from one or more URLs using a prompt/schema.

    Setup:
        Install ``langchain-firecrawl`` and set ``FIRECRAWL_API_KEY``.

    Instantiation:
        ```python
        from langchain_firecrawl import FirecrawlExtract

        tool = FirecrawlExtract()
        tool.invoke(
            {
                "urls": ["https://firecrawl.dev"],
                "prompt": "Extract the product name and pricing tiers.",
            }
        )
        ```
    """

    name: str = "firecrawl_extract"
    description: str = (
        "Extract structured data from one or more web pages. "
        "Provide a list of URLs and a natural-language 'prompt' describing the "
        "data to extract (optionally a JSON 'schema')."
    )

    def _run(
        self,
        urls: list[str],
        prompt: str | None = None,
        schema: dict[str, Any] | None = None,
        system_prompt: str | None = None,
        enable_web_search: bool | None = None,  # noqa: FBT001
        show_sources: bool | None = None,  # noqa: FBT001
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> Any:
        """Extract from ``urls``.

        Args:
            urls: The URLs to extract data from.
            prompt: Natural-language description of the data to extract.
            schema: Optional JSON schema describing the desired output shape.
            system_prompt: Optional system prompt to steer extraction.
            enable_web_search: Whether the extractor may search the web.
            show_sources: Whether to include source references.
            run_manager: The run manager for callbacks.

        Returns:
            The extracted data (``response.data``), or an error string.
        """
        try:
            response = self.client.extract(
                urls,
                **clean_params(
                    {
                        "prompt": prompt,
                        "schema": schema,
                        "system_prompt": system_prompt,
                        "enable_web_search": enable_web_search,
                        "show_sources": show_sources,
                    },
                    self.integration,
                ),
            )
            data = getattr(response, "data", None)
            return data if data is not None else to_dict(response)
        except Exception as e:
            return repr(e)


class FirecrawlSearch(_FirecrawlBaseTool):
    """Search the web and return results with optional page content.

    Setup:
        Install ``langchain-firecrawl`` and set ``FIRECRAWL_API_KEY``.

    Instantiation:
        ```python
        from langchain_firecrawl import FirecrawlSearch

        tool = FirecrawlSearch()
        tool.invoke({"query": "best web scraping libraries", "limit": 5})
        ```
    """

    name: str = "firecrawl_search"
    description: str = (
        "Search the web and return a list of results (url, title, description). "
        "Input should be a search query; use 'limit' to cap the number of results."
    )

    def _run(
        self,
        query: str,
        limit: int | None = None,
        sources: list[str] | None = None,
        categories: list[str] | None = None,
        tbs: str | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> list[dict[str, Any]] | str:
        """Search the web for ``query``.

        Args:
            query: The search query.
            limit: Maximum number of results to return.
            sources: Result sources to include (e.g. ``["web", "news"]``).
            categories: Result categories to include.
            tbs: Time-based search filter (e.g. ``"qdr:d"`` for the past day).
            run_manager: The run manager for callbacks.

        Returns:
            A list of result dicts, or an error string.
        """
        try:
            data = self.client.search(
                query,
                **clean_params(
                    {
                        "limit": limit,
                        "sources": sources,
                        "categories": categories,
                        "tbs": tbs,
                    },
                    self.integration,
                ),
            )
            return _search_results(data)
        except Exception as e:
            return repr(e)
