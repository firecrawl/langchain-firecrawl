"""Shared fixtures for unit tests.

Network access is disabled for every unit test so they cannot accidentally hit
the live Firecrawl API; the client is always mocked.
"""

from pytest_socket import disable_socket


def pytest_runtest_setup() -> None:
    """Disable sockets for all unit tests (no network allowed)."""
    disable_socket()
