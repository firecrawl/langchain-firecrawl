"""Standard LangChain unit tests for the Firecrawl tools.

These are the ``langchain-tests`` ``ToolsUnitTests`` that LangChain uses to bless
an integration package: init, init-from-env, name, input schema, and that the
example invoke params validate against the declared schema.
"""

from typing import Any

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_firecrawl import (
    FirecrawlCrawl,
    FirecrawlExtract,
    FirecrawlMap,
    FirecrawlScrape,
    FirecrawlSearch,
)

_ENV = {"FIRECRAWL_API_KEY": "fc-test"}
_EXPECTED = {"api_key": "fc-test"}
_PARAMS = {"api_key": "fc-test"}


class TestFirecrawlScrapeUnit(ToolsUnitTests):
    """Standard unit tests for `FirecrawlScrape`."""

    @property
    def tool_constructor(self) -> type[FirecrawlScrape]:
        """The tool class under test."""
        return FirecrawlScrape

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor."""
        return _PARAMS

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"url": "https://example.com"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        """Env vars, init args, and expected attrs for env init."""
        return _ENV, {}, _EXPECTED


class TestFirecrawlCrawlUnit(ToolsUnitTests):
    """Standard unit tests for `FirecrawlCrawl`."""

    @property
    def tool_constructor(self) -> type[FirecrawlCrawl]:
        """The tool class under test."""
        return FirecrawlCrawl

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor."""
        return _PARAMS

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"url": "https://example.com"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        """Env vars, init args, and expected attrs for env init."""
        return _ENV, {}, _EXPECTED


class TestFirecrawlMapUnit(ToolsUnitTests):
    """Standard unit tests for `FirecrawlMap`."""

    @property
    def tool_constructor(self) -> type[FirecrawlMap]:
        """The tool class under test."""
        return FirecrawlMap

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor."""
        return _PARAMS

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"url": "https://example.com"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        """Env vars, init args, and expected attrs for env init."""
        return _ENV, {}, _EXPECTED


class TestFirecrawlExtractUnit(ToolsUnitTests):
    """Standard unit tests for `FirecrawlExtract`."""

    @property
    def tool_constructor(self) -> type[FirecrawlExtract]:
        """The tool class under test."""
        return FirecrawlExtract

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor."""
        return _PARAMS

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"urls": ["https://example.com"], "prompt": "Extract the title"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        """Env vars, init args, and expected attrs for env init."""
        return _ENV, {}, _EXPECTED


class TestFirecrawlSearchUnit(ToolsUnitTests):
    """Standard unit tests for `FirecrawlSearch`."""

    @property
    def tool_constructor(self) -> type[FirecrawlSearch]:
        """The tool class under test."""
        return FirecrawlSearch

    @property
    def tool_constructor_params(self) -> dict[str, Any]:
        """Params passed to the constructor."""
        return _PARAMS

    @property
    def tool_invoke_params_example(self) -> dict[str, Any]:
        """Example args matching the tool's input schema."""
        return {"query": "what is firecrawl"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        """Env vars, init args, and expected attrs for env init."""
        return _ENV, {}, _EXPECTED
