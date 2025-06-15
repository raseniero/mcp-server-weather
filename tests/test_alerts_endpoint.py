import pytest
from httpx import AsyncClient
from mcp.server.fastmcp import FastMCP
from src.weather.server import get_alerts

@pytest.mark.asyncio
async def test_get_alerts_endpoint(monkeypatch):
    """
    RED: Test the /get_alerts endpoint returns alerts for a valid state code.
    This test should fail initially because the endpoint is not yet implemented as an HTTP route.
    """
    # Arrange: monkeypatch the internal data fetch to avoid real API calls
    async def fake_make_nws_request(url):
        return {
            "features": [
                {"properties": {"event": "Flood Warning", "severity": "Severe", "headline": "Flooding in effect"}}
            ]
        }
    monkeypatch.setattr("src.weather.server.make_nws_request", fake_make_nws_request)

    # Act: call the get_alerts tool function directly
    result = await get_alerts("CA")

    # Assert: check the response contains the expected alert
    assert "Flood Warning" in result
    assert "Severe" in result
    assert "Flooding in effect" in result
