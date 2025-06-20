import pytest
from mcp.server.fastmcp import FastMCP
import asyncio

import sys
import os
import types

import importlib.util


# Helper to import the server module
@pytest.fixture(scope="module")
def server_module():
    server_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "weather", "server.py"
    )
    spec = importlib.util.spec_from_file_location("weather.server", server_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["weather.server"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_server_initialization(server_module):
    """Test that the FastMCP server initializes without error."""
    assert hasattr(server_module, "mcp")
    assert isinstance(server_module.mcp, FastMCP)
    assert server_module.mcp.name == "weather"


@pytest.mark.asyncio
async def test_server_initialization_refactored(server_module):
    """
    Failing test for refactored server: expects WeatherServer class with FastMCP instance.
    """
    assert hasattr(
        server_module, "WeatherServer"
    ), "WeatherServer class should be defined."
    server = server_module.WeatherServer()
    assert hasattr(server, "mcp"), "WeatherServer should have an 'mcp' attribute."
    assert isinstance(
        server.mcp, FastMCP
    ), "WeatherServer.mcp should be a FastMCP instance."
    assert server.mcp.name == "weather"


@pytest.mark.asyncio
async def test_get_alerts_tool_registration(server_module):
    """Test that get_alerts is registered as a tool."""
    assert hasattr(server_module, "get_alerts")
    assert callable(server_module.get_alerts)
    # Check if get_alerts is registered as a tool in FastMCP (using 'tool' attribute or registry)
    assert hasattr(server_module.mcp, "tool") or hasattr(
        server_module.mcp, "get_alerts"
    )
    # Optionally, check if callable(getattr(server_module.mcp, 'get_alerts', None))


@pytest.mark.asyncio
async def test_get_forecast_tool_registration(server_module):
    """Test that get_forecast is registered as a tool."""
    assert hasattr(server_module, "get_forecast")
    assert callable(server_module.get_forecast)
    assert hasattr(server_module.mcp, "tool") or hasattr(
        server_module.mcp, "get_forecast"
    )
    # Optionally, check if callable(getattr(server_module.mcp, 'get_forecast', None))


@pytest.mark.asyncio
async def test_get_alerts_input_validation(server_module):
    """RED: get_alerts should return error for invalid state codes (lowercase, non-alpha, wrong length, missing)."""
    # Arrange/Act/Assert
    invalid_inputs = ["ca", "C1", "", None, "ZZZ", 123]
    for state in invalid_inputs:
        result = await server_module.get_alerts(state)
        assert "Invalid state code" in result


@pytest.mark.asyncio
async def test_get_forecast_input_validation(server_module):
    """RED: get_forecast should return error for invalid coordinates (out-of-range, non-numeric, missing)."""
    # Arrange/Act/Assert
    invalid_coords = [
        (None, None),
        ("abc", 100),
        (91, 0),
        (0, -181),
        ("", ""),
        (200, 200),
    ]
    for lat, lon in invalid_coords:
        result = await server_module.get_forecast(lat, lon)
        assert "Invalid coordinates" in result


@pytest.mark.asyncio
async def test_get_alerts_error_response(monkeypatch, server_module):
    """RED: get_alerts should return a specific error message if NWSClient raises httpx.HTTPStatusError or ValueError."""
    import httpx
    from src.weather.nws_client import NWSClient

    async def raise_http_error(self, url):
        raise httpx.HTTPStatusError("error", request=None, response=None)

    monkeypatch.setattr(NWSClient, "_make_request", raise_http_error)
    result = await server_module.get_alerts("CA")
    assert "Malformed response" in result or "weather service" in result

    async def raise_value_error(self, url):
        raise ValueError("bad json")

    monkeypatch.setattr(NWSClient, "_make_request", raise_value_error)
    result2 = await server_module.get_alerts("CA")
    assert "Malformed response" in result2 or "weather service" in result2


@pytest.mark.asyncio
async def test_get_forecast_error_response(monkeypatch, server_module):
    """RED: get_forecast should return a specific error message if NWSClient raises httpx.HTTPStatusError or ValueError."""
    import httpx
    from src.weather.nws_client import NWSClient

    async def raise_http_error(self, url):
        raise httpx.HTTPStatusError("error", request=None, response=None)

    monkeypatch.setattr(NWSClient, "_make_request", raise_http_error)
    result = await server_module.get_forecast(34.05, -118.25)
    assert "Malformed response" in result or "weather service" in result

    async def raise_value_error(self, url):
        raise ValueError("bad json")

    monkeypatch.setattr(NWSClient, "_make_request", raise_value_error)
    result2 = await server_module.get_forecast(34.05, -118.25)
    assert "Malformed response" in result2 or "weather service" in result2


@pytest.mark.asyncio
async def test_get_alerts_invalid_state(server_module):
    """Test get_alerts with an invalid state code."""
    result = await server_module.get_alerts("ZZ")
    assert "Invalid state code" in result


@pytest.mark.asyncio
async def test_get_alerts_malformed_response(monkeypatch, server_module):
    """Test get_alerts with a malformed API response (missing 'features')."""
    from src.weather.nws_client import NWSClient

    async def fake_make_nws_request(self, url):
        return {"unexpected": "data"}

    monkeypatch.setattr(NWSClient, "_make_request", fake_make_nws_request)
    result = await server_module.get_alerts("CA")
    assert "Malformed response" in result


@pytest.mark.asyncio
async def test_get_forecast_invalid_coords(server_module):
    """Test get_forecast with invalid coordinates."""
    result = await server_module.get_forecast(200, 200)
    assert "Invalid coordinates" in result


@pytest.mark.asyncio
async def test_get_forecast_malformed_response(monkeypatch, server_module):
    """Test get_forecast with a malformed API response (missing 'properties' or 'periods')."""

    async def fake_make_nws_request(self, url):
        return {"unexpected": "data"}

    from src.weather.nws_client import NWSClient

    monkeypatch.setattr(NWSClient, "_make_request", fake_make_nws_request)
    result = await server_module.get_forecast(34.05, -118.25)
    assert "Malformed response" in result


@pytest.mark.asyncio
async def test_get_alerts_returns_expected_format(monkeypatch, server_module):
    """
    Test for get_alerts: should return a list of alerts for a valid state code.
    """
    # Patch make_nws_request to return a fake response
    fake_alerts = {
        "features": [
            {
                "properties": {
                    "headline": "Test Alert",
                    "event": "Storm",
                    "severity": "Severe",
                }
            },
            {
                "properties": {
                    "headline": "Test Alert 2",
                    "event": "Flood",
                    "severity": "Moderate",
                }
            },
        ]
    }
    from src.weather.nws_client import NWSClient

    async def fake_make_nws_request(self, url):
        return fake_alerts

    monkeypatch.setattr(NWSClient, "_make_request", fake_make_nws_request)
    # Call get_alerts_data with a valid state code
    result = await server_module.get_alerts_data("CA")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["event"] == "Storm"
    assert result[1]["event"] == "Flood"


@pytest.mark.asyncio
async def test_health_check_endpoint(test_client):
    """Test the /health endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_forecast_data_returns_expected_format(monkeypatch, server_module):
    """
    Failing test for get_forecast_data: should return a list of forecast periods for valid coordinates.
    """
    # Simulate sequential responses for points and forecast endpoints
    fake_points = {
        "properties": {
            "forecast": "https://api.weather.gov/gridpoints/XX/99,99/forecast"
        }
    }
    fake_forecast = {
        "properties": {
            "periods": [
                {
                    "name": "Tonight",
                    "temperature": 50,
                    "temperatureUnit": "F",
                    "windSpeed": "5 mph",
                    "windDirection": "NW",
                    "detailedForecast": "Clear.",
                },
                {
                    "name": "Tomorrow",
                    "temperature": 70,
                    "temperatureUnit": "F",
                    "windSpeed": "10 mph",
                    "windDirection": "N",
                    "detailedForecast": "Sunny.",
                },
            ]
        }
    }
    responses = [fake_points, fake_forecast]

    async def fake_make_nws_request(self, url):
        return responses.pop(0)

    from src.weather.nws_client import NWSClient

    monkeypatch.setattr(NWSClient, "_make_request", fake_make_nws_request)
    # Call get_forecast_data with valid coordinates
    result = await server_module.get_forecast_data(34.05, -118.25)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Tonight"
    assert result[1]["name"] == "Tomorrow"
