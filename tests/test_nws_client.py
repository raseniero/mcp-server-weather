"""
Test suite for NWSClient: Task 4.2.1 - Test successful API responses
"""
import pytest
from weather.nws_client import NWSClient

@pytest.mark.asyncio
async def test_get_alerts_success(monkeypatch):
    """
    RED: NWSClient.get_alerts should return a list of alerts for a valid state code.
    This test should fail initially because the method is not yet implemented or not returning the expected structure.
    """
    # Arrange: patch _make_request to return a fake API response
    fake_response = {
        "features": [
            {"properties": {"headline": "Test Alert", "event": "Storm", "severity": "Severe"}},
            {"properties": {"headline": "Test Alert 2", "event": "Flood", "severity": "Moderate"}},
        ]
    }
    async def fake_make_request(self, url):
        return fake_response
    monkeypatch.setattr(NWSClient, "_make_request", fake_make_request)
    client = NWSClient()
    # Act
    alerts = await client.get_alerts("CA")
    # Assert
    assert isinstance(alerts, list)
    assert len(alerts) == 2
    assert alerts[0]["headline"] == "Test Alert"
    assert alerts[1]["event"] == "Flood"
    assert alerts[1]["severity"] == "Moderate"

@pytest.mark.asyncio
async def test_get_alerts_http_error(monkeypatch):
    """
    RED: NWSClient.get_alerts should raise httpx.HTTPStatusError if the underlying _make_request raises it.
    """
    import httpx
    async def fake_make_request(self, url):
        raise httpx.HTTPStatusError("error", request=None, response=None)
    monkeypatch.setattr(NWSClient, "_make_request", fake_make_request)
    client = NWSClient()
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_alerts("CA")

@pytest.mark.asyncio
async def test_get_alerts_malformed_response(monkeypatch):
    """
    RED: NWSClient.get_alerts should raise ValueError if the API response is missing 'features' or has a malformed structure.
    """
    async def fake_make_request(self, url):
        return {"unexpected": "data"}
    monkeypatch.setattr(NWSClient, "_make_request", fake_make_request)
    client = NWSClient()
    with pytest.raises(ValueError):
        await client.get_alerts("CA")

@pytest.mark.asyncio
async def test_get_alerts_rate_limit_retries(monkeypatch):
    """
    RED: NWSClient.get_alerts should retry on HTTP 429 (Too Many Requests) and eventually raise after max retries.
    """
    import httpx
    call_count = {"count": 0}
    class MockResponse:
        status_code = 429
    async def fake_make_request(self, url):
        call_count["count"] += 1
        raise httpx.HTTPStatusError("429 Too Many Requests", request=None, response=MockResponse())
    monkeypatch.setattr(NWSClient, "_make_request", fake_make_request)
    client = NWSClient()
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_alerts("CA")
    assert call_count["count"] > 1  # Should retry at least once
