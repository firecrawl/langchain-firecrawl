"""Unit tests for API key / URL resolution (no network)."""

import os
from unittest import mock

from pydantic import SecretStr

from langchain_firecrawl import FirecrawlScrape
from langchain_firecrawl._utilities import (
    DEFAULT_API_URL,
    resolve_api_key,
    resolve_api_url,
)


def test_api_key_from_init() -> None:
    """An explicit API key is stored as a `SecretStr`."""
    tool = FirecrawlScrape(api_key="fc-secret")  # type: ignore[arg-type]
    assert isinstance(tool.api_key, SecretStr)
    assert tool.api_key.get_secret_value() == "fc-secret"


def test_api_key_masked() -> None:
    """The API key is not exposed via its string representation."""
    tool = FirecrawlScrape(api_key="fc-secret")  # type: ignore[arg-type]
    assert "fc-secret" not in str(tool.api_key)


def test_api_key_from_env() -> None:
    """The API key falls back to the `FIRECRAWL_API_KEY` env var."""
    with mock.patch.dict(os.environ, {"FIRECRAWL_API_KEY": "fc-env"}):
        tool = FirecrawlScrape()
    assert tool.api_key.get_secret_value() == "fc-env"


def test_resolve_api_url_default() -> None:
    """The API URL defaults when neither argument nor env var is set."""
    with mock.patch.dict(os.environ, {}, clear=True):
        assert resolve_api_url(None) == DEFAULT_API_URL
        assert resolve_api_url("https://custom.example") == "https://custom.example"


def test_resolve_api_url_from_env() -> None:
    """The API URL is read from `FIRECRAWL_API_URL`."""
    with mock.patch.dict(os.environ, {"FIRECRAWL_API_URL": "https://eu.firecrawl.dev"}):
        assert resolve_api_url(None) == "https://eu.firecrawl.dev"


def test_resolve_api_key_empty_when_unset() -> None:
    """Key resolution returns an empty string when nothing is configured."""
    with mock.patch.dict(os.environ, {}, clear=True):
        assert resolve_api_key(None) == ""
