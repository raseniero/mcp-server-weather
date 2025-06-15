import pytest
import httpx
from weather.nws_client import NWSClient

@pytest.mark.asyncio
async def test_make_request_returns_data(monkeypatch):
    """
    Failing test for NWSClient._make_request: should return parsed JSON data for valid response.
    """
    class DummyResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
        def raise_for_status(self):
            if self.status_code != 200:
                raise httpx.HTTPStatusError("error", request=None, response=None)
    async def dummy_get(*args, **kwargs):
        return DummyResponse({"key": "value"})
    monkeypatch.setattr(httpx.AsyncClient, "get", dummy_get)
    client = NWSClient()
    result = await client._make_request("https://example.com")
    assert result == {"key": "value"}

@pytest.mark.asyncio
async def test_make_request_http_error(monkeypatch):
    """
    Failing test: _make_request should raise or handle HTTP errors (non-200 response).
    """
    class DummyResponse:
        def __init__(self, status_code=500):
            self.status_code = status_code
        def json(self):
            return {}
        def raise_for_status(self):
            raise httpx.HTTPStatusError("error", request=None, response=None)
    async def dummy_get(*args, **kwargs):
        return DummyResponse(status_code=500)
    monkeypatch.setattr(httpx.AsyncClient, "get", dummy_get)
    client = NWSClient()
    with pytest.raises(httpx.HTTPStatusError):
        await client._make_request("https://example.com/fail")

@pytest.mark.asyncio
async def test_make_request_invalid_json(monkeypatch):
    """
    Failing test: _make_request should raise or handle invalid JSON response.
    """
    class DummyResponse:
        def __init__(self, status_code=200):
            self.status_code = status_code
        def json(self):
            raise ValueError("Invalid JSON")
        def raise_for_status(self):
            pass
    async def dummy_get(*args, **kwargs):
        return DummyResponse(status_code=200)
    monkeypatch.setattr(httpx.AsyncClient, "get", dummy_get)
    client = NWSClient()
    with pytest.raises(ValueError):
        await client._make_request("https://example.com/badjson")
