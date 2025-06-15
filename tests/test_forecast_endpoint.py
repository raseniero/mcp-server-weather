import pytest
from src.weather.server import get_forecast


@pytest.mark.asyncio
async def test_get_forecast_endpoint(monkeypatch):
    """
    RED: Test the /get_forecast endpoint returns forecast periods for valid coordinates.
    This test should fail initially because the endpoint is not yet refactored to use NWSClient and is not isolated.
    """
    # Arrange: monkeypatch NWSClient._make_request to avoid real API calls
    from src.weather.nws_client import NWSClient

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
                    "temperature": 55,
                    "temperatureUnit": "F",
                    "windSpeed": "5 mph",
                    "windDirection": "NW",
                    "detailedForecast": "Clear. Low 55.",
                },
                {
                    "name": "Tomorrow",
                    "temperature": 75,
                    "temperatureUnit": "F",
                    "windSpeed": "10 mph",
                    "windDirection": "W",
                    "detailedForecast": "Sunny. High 75.",
                },
            ]
        }
    }
    responses = [fake_points, fake_forecast]

    async def fake_make_nws_request(self, url):
        return responses.pop(0)

    monkeypatch.setattr(NWSClient, "_make_request", fake_make_nws_request)

    # Act: call the get_forecast tool function directly
    result = await get_forecast(34.05, -118.25)

    # Assert: check the response contains both forecast periods
    assert "Tonight" in result
    assert "Tomorrow" in result
    assert "Clear. Low 55." in result
    assert "Sunny. High 75." in result
