# Changelog

## 0.2.0

### Changed

- `FirecrawlExtract` and `FirecrawlLoader(mode="extract")` no longer call the deprecated `/v2/extract` endpoint. Each URL is scraped with a `json` format that carries the `prompt` and `schema`.
- `FirecrawlExtract` with several URLs now returns a `{url: json}` mapping, one entry per URL. With a single URL it still returns that page's JSON.
- `FirecrawlExtract` no longer accepts `system_prompt`, `enable_web_search` or `show_sources`. Put any extra instructions in `prompt`.

### Added

- Every tool has an `integration` field (default `"langchain"`) that is sent as the attribution tag on each Firecrawl request, so a host application can tag its own traffic.
- CI on GitHub Actions: ruff, mypy, import checks and the LangChain standard unit tests on every pull request. Integration tests run when the `FIRECRAWL_API_KEY` secret is configured.
- LangChain standard integration tests (`ToolsIntegrationTests`) for `FirecrawlScrape`, `FirecrawlSearch` and `FirecrawlExtract`.
- A release workflow that publishes to PyPI with trusted publishing when a `v*` tag is pushed.

## 0.1.1

### Fixed

- The PyPI Documentation link points at https://docs.firecrawl.dev/integrations/langchain.

## 0.1.0

- First release: `FirecrawlLoader` and the `FirecrawlScrape`, `FirecrawlCrawl`, `FirecrawlMap`, `FirecrawlExtract` and `FirecrawlSearch` tools.
