"""Shared utilities for the Firecrawl integration.

This module centralizes API key / URL resolution, client construction, and the
``integration="langchain"`` attribution tag that Firecrawl uses to attribute
LangChain-sourced usage. Every loader and tool routes through here so the tag is
applied uniformly.
"""

from __future__ import annotations

import os
from typing import Any

from firecrawl import Firecrawl  # type: ignore[import-untyped]
from langchain_core.utils import convert_to_secret_str

#: Value forwarded as ``integration`` on every Firecrawl API call so usage
#: originating from this package is attributed to LangChain.
INTEGRATION: str = "langchain"

#: Default Firecrawl API base URL used when none is supplied via argument or the
#: ``FIRECRAWL_API_URL`` environment variable.
DEFAULT_API_URL: str = "https://api.firecrawl.dev"


def resolve_api_key(api_key: str | None) -> str:
    """Resolve the Firecrawl API key.

    Args:
        api_key: An explicit API key, or ``None`` to read ``FIRECRAWL_API_KEY``.

    Returns:
        The resolved API key, or an empty string if none is set.
    """
    return api_key or os.environ.get("FIRECRAWL_API_KEY") or ""


def resolve_api_url(api_url: str | None) -> str:
    """Resolve the Firecrawl API URL.

    Args:
        api_url: An explicit API URL, or ``None`` to read ``FIRECRAWL_API_URL``.

    Returns:
        The resolved API URL, falling back to :data:`DEFAULT_API_URL`.
    """
    return api_url or os.environ.get("FIRECRAWL_API_URL") or DEFAULT_API_URL


def create_client(api_key: str | None = None, api_url: str | None = None) -> Firecrawl:
    """Build a Firecrawl client from resolved credentials.

    Args:
        api_key: Explicit API key, or ``None`` to read from the environment.
        api_url: Explicit API URL, or ``None`` to read from the environment.

    Returns:
        A configured :class:`firecrawl.Firecrawl` client.
    """
    return Firecrawl(
        api_key=resolve_api_key(api_key),
        api_url=resolve_api_url(api_url),
    )


def initialize_client(values: dict) -> dict:
    """Validate environment and instantiate the client for a pydantic tool.

    Mirrors the pattern used by sibling integrations: resolves the API key into a
    ``SecretStr``, resolves the API URL, and stores a ready client under
    ``"client"``. Intended for use from a ``model_validator(mode="before")``.

    Args:
        values: The raw init values for a pydantic model.

    Returns:
        The updated values dict with ``api_key``, ``api_url`` and ``client`` set.
    """
    api_key = resolve_api_key(values.get("api_key"))
    values["api_key"] = convert_to_secret_str(api_key)
    api_url = resolve_api_url(values.get("api_url"))
    values["api_url"] = api_url
    values["client"] = Firecrawl(
        api_key=values["api_key"].get_secret_value(),
        api_url=api_url,
    )
    return values


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Drop ``None`` values and inject the LangChain attribution tag.

    Args:
        params: Keyword arguments destined for a Firecrawl client method.

    Returns:
        A new mapping without ``None`` values and with ``integration`` set to
        :data:`INTEGRATION`.
    """
    cleaned = {k: v for k, v in params.items() if v is not None}
    cleaned["integration"] = INTEGRATION
    return cleaned


def to_dict(obj: Any) -> dict[str, Any]:
    """Coerce a Firecrawl v2 response field into a plain ``dict``.

    Firecrawl v2 returns typed pydantic models (e.g. ``DocumentMetadata``); this
    flattens them (and plain dicts / arbitrary objects) into a JSON-friendly dict
    with ``None`` values dropped.

    Args:
        obj: A pydantic model, dict, or arbitrary object (or ``None``).

    Returns:
        A plain dict; empty when ``obj`` is ``None``.
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items() if v is not None}
    if hasattr(obj, "model_dump") and callable(obj.model_dump):
        return obj.model_dump(exclude_none=True)
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if v is not None}
    return {"value": str(obj)}
