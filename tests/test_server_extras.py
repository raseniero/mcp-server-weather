"""
Additional unit tests to increase coverage of server module error paths and helpers.
"""
import pytest
import httpx

from weather.server import (
    make_nws_request,
    get_alerts_data,
    format_alert,
    get_forecast_data,
)
from src.weather.nws_client import NWSClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_type, error_value",
    [
        ("json", ValueError("bad json")),
        ("http", httpx.HTTPStatusError("err", request=None, response=None)),
        ("request", httpx.RequestError("network")),
        ("generic", Exception("oops")),
    ],
)
async def test_make_nws_request_errors(monkeypatch, error_type, error_value):
    class DummyResponse:
        def raise_for_status(self):
            if error_type == "http":
                raise error_value
        def json(self):
            if error_type == "json":
                raise error_value
            return {}

    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, headers=None, timeout=None):
            return DummyResponse()

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    assert await make_nws_request("http://dummy") is None


@pytest.mark.asyncio
async def test_make_nws_request_request_error(monkeypatch):
    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, headers=None, timeout=None):
            raise httpx.RequestError("network")

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    assert await make_nws_request("http://dummy") is None


@pytest.mark.asyncio
async def test_make_nws_request_generic_error(monkeypatch):
    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, headers=None, timeout=None):
            raise Exception("oops")

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    assert await make_nws_request("http://dummy") is None


@pytest.mark.asyncio
async def test_get_alerts_data_invalid_and_malformed():
    # None response
    class C1:
        async def _make_request(self, url):
            return None

    assert await get_alerts_data("CA", client=C1()) is None

    # Missing or non-list 'features'
    class C2:
        async def _make_request(self, url):
            return {"foo": "bar"}

    class C3:
        async def _make_request(self, url):
            return {"features": "nope"}

    assert await get_alerts_data("CA", client=C2()) is None
    assert await get_alerts_data("CA", client=C3()) is None


def test_format_alert_defaults():
    out = format_alert({"properties": {}})
    assert "No headline available" in out
    assert "Unknown" in out


@pytest.mark.asyncio
async def test_get_forecast_data_error_paths(monkeypatch):
    # Missing points data or properties/forecast
    async def r1(self, url):
        return None

    monkeypatch.setattr(NWSClient, "_make_request", r1)
    with pytest.raises(ValueError):
        await get_forecast_data(1.0, 2.0)

    # Missing forecast URL
    async def r2(self, url):
        return {"properties": {}}

    monkeypatch.setattr(NWSClient, "_make_request", r2)
    with pytest.raises(ValueError):
        await get_forecast_data(1.0, 2.0)

    # Missing periods
    seq = [{"properties": {"forecast": "u"}}, {"properties": {}}]

    async def r3(self, url):
        return seq.pop(0)

    monkeypatch.setattr(NWSClient, "_make_request", r3)
    with pytest.raises(ValueError):
        await get_forecast_data(1.0, 2.0)

    # Periods not a list
    seq2 = [{"properties": {"forecast": "u"}}, {"properties": {"periods": "no"}}]

    async def r4(self, url):
        return seq2.pop(0)

    monkeypatch.setattr(NWSClient, "_make_request", r4)
    with pytest.raises(ValueError):
        await get_forecast_data(1.0, 2.0)