"""
Unit tests for the NWSClient class, focusing on the public get_alerts method.
Tests use monkeypatching to isolate network calls and ensure test reliability.
"""
import pytest
from weather.nws_client import NWSClient

@pytest.mark.asyncio
async def test_get_alerts_success(monkeypatch):
    """
    Test that NWSClient.get_alerts returns a list of alerts for a valid state.
    Uses monkeypatching to mock network calls and ensure test reliability.
    """
    """
    RED: Test that NWSClient.get_alerts returns alert data for a valid state.
    """
    fake_response = {
        "features": [
            {"properties": {"headline": "Test Alert", "event": "Flood", "severity": "Severe"}},
            {"properties": {"headline": "Another Alert", "event": "Storm", "severity": "Moderate"}},
        ]
    }
    async def fake_make_request(self, url):
        return fake_response
    monkeypatch.setattr(NWSClient, "_make_request", fake_make_request)
    client = NWSClient()
    alerts = await client.get_alerts("CA")
    assert isinstance(alerts, list)
    assert len(alerts) == 2
    assert alerts[0]["headline"] == "Test Alert"
    assert alerts[1]["event"] == "Storm"
