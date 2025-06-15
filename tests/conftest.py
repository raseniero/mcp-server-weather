"""Pytest configuration and fixtures for the test suite."""

import json
import os
import sys
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="module")
def server_module():
    """Fixture to import the server module dynamically."""
    server_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "weather", "server.py"
    )
    spec = importlib.util.spec_from_file_location("weather.server", server_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["weather.server"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.AsyncClient."""
    with patch("httpx.AsyncClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_nws_client():
    """Fixture to mock NWSClient and its _make_request method."""
    with patch("src.weather.nws_client.NWSClient") as mock_client:
        mock_client.return_value._make_request = AsyncMock()
        yield mock_client


@pytest.fixture
def test_client(server_module):
    """Fixture to create a test client for the FastMCP server."""
    from httpx import ASGITransport

    app = server_module.mcp.streamable_http_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# Add any other common test utilities or fixtures here
