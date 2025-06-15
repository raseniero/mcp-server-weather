"""Pytest configuration and fixtures for the test suite."""
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add common fixtures here that will be available to all tests

@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.AsyncClient."""
    with patch('httpx.AsyncClient') as mock_client:
        yield mock_client

# Add any other common test utilities or fixtures here
