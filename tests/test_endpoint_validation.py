import pytest
from src.weather.server import get_alerts, get_forecast

@pytest.mark.asyncio
@pytest.mark.parametrize("state,expected", [
    (None, "Invalid state code"),
    ("", "Invalid state code"),
    ("C", "Invalid state code"),
    ("cal", "Invalid state code"),
    ("ca", "Invalid state code"),
    ("C1", "Invalid state code"),
    ("ZZ", "Invalid state code"),  # Not in US_STATES
    ("NY", None),  # valid
])
async def test_get_alerts_state_validation(state, expected):
    result = await get_alerts(state)
    if expected:
        assert expected in result
    else:
        # For valid, just check not the error
        assert "Invalid state code" not in result

@pytest.mark.asyncio
@pytest.mark.parametrize("lat,lon,expected", [
    (None, -74.0, "Invalid coordinates. Latitude and longitude must be numbers."),
    (40.7, None, "Invalid coordinates. Latitude and longitude must be numbers."),
    ("abc", "def", "Invalid coordinates. Latitude and longitude must be numbers."),
    (1000, 0, "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."),
    (0, 2000, "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."),
    (-91, 0, "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."),
    (0, -181, "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."),
    (34.05, -118.25, None),  # valid
])
async def test_get_forecast_latlon_validation(lat, lon, expected):
    result = await get_forecast(lat, lon)
    if expected:
        assert expected in result
    else:
        # For valid, just check not the error
        assert "Invalid coordinates" not in result
