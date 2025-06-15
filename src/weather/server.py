from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

class WeatherServer:
    """
    WeatherServer encapsulates the FastMCP server instance for weather tools.
    """
    def __init__(self) -> None:
        """
        Initialize the WeatherServer with a FastMCP instance named 'weather'.
        """
        self.mcp: FastMCP = FastMCP("weather")

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                # JSON decoding error
                # Optionally log error here
                return None
        except httpx.HTTPStatusError:
            # Non-200 HTTP response
            # Optionally log error here
            return None
        except httpx.RequestError:
            # Network error
            # Optionally log error here
            return None
        except Exception:
            # Catch-all for unexpected errors
            # Optionally log error here
            return None



async def get_alerts_data(state: str) -> list[dict[str, Any]]:
    """
    Fetch weather alerts for a given US state from the NWS API.

    Args:
        state: Two-letter US state code (e.g. 'CA', 'NY').

    Returns:
        A list of alert dictionaries with keys: 'headline', 'event', 'severity'.
        Returns an empty list if no alerts are found or the response is malformed.
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return []
    if not isinstance(data["features"], list):
        raise ValueError("Malformed response: 'features' is not a list.")
    alerts: list[dict[str, Any]] = []
    for feature in data["features"]:
        props = feature.get("properties", {})
        alerts.append({
            "headline": props.get("headline"),
            "event": props.get("event"),
            "severity": props.get("severity"),
        })
    return alerts

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    FastMCP tool: Returns formatted weather alerts string for a US state.
    """
    alerts = await get_alerts_data(state)
    if not alerts:
        return f"No alerts found for state: {state}"
    formatted = []
    for alert in alerts:
        formatted.append(
            f"Event: {alert['event']}\nSeverity: {alert['severity']}\nHeadline: {alert['headline']}"
        )
    return "\n---\n".join(formatted)


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
    """


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    FastMCP tool: Return formatted weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. 'CA', 'NY').

    Returns:
        A formatted string of alerts or an error message.
    """
    # Input validation
    if not isinstance(state, str) or len(state) != 2 or not state.isalpha() or not state.isupper() or state not in US_STATES:
        return "Invalid state code. Please provide a two-letter uppercase state abbreviation."
    data = await make_nws_request(f"{NWS_API_BASE}/alerts/active?area={state}")
    if not data:
        return "Unable to fetch alerts or no alerts found."
    if "features" not in data:
        return "Malformed response from weather service."
    if not data["features"]:
        return f"No active alerts for state: {state}"
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


async def get_forecast_data(latitude: float, longitude: float) -> list[dict[str, Any]]:
    """
    Fetch forecast periods for given coordinates from the NWS API.

    Args:
        latitude: Latitude of the location (-90 to 90).
        longitude: Longitude of the location (-180 to 180).

    Returns:
        A list of forecast period dictionaries.
    Raises:
        ValueError: If the response is malformed or missing required keys.
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data or "properties" not in points_data or "forecast" not in points_data["properties"]:
        raise ValueError("Malformed response: missing 'properties' or 'forecast'.")
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data or "properties" not in forecast_data or "periods" not in forecast_data["properties"]:
        raise ValueError("Malformed response: missing 'properties' or 'periods'.")
    periods = forecast_data["properties"]["periods"]
    if not isinstance(periods, list):
        raise ValueError("Malformed response: 'periods' is not a list.")
    return periods

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    FastMCP tool: Return formatted weather forecast for a location.

    Args:
        latitude: Latitude of the location (-90 to 90).
        longitude: Longitude of the location (-180 to 180).

    Returns:
        A formatted string of the weather forecast or an error message.
    """
    # Input validation
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return "Invalid coordinates. Latitude and longitude must be numbers."
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."
    try:
        periods = await get_forecast_data(lat, lon)
    except ValueError as e:
        # Malformed or missing keys in response
        # Optionally log error here
        return f"Malformed response from weather service. {str(e)}"
    except Exception:
        # Optionally log error here
        return "Malformed response from weather service."
    if not periods:
        return "Unable to fetch forecast data for this location."
    forecasts: list[str] = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
            {period['name']}:
            Temperature: {period['temperature']}°{period['temperatureUnit']}
            Wind: {period['windSpeed']} {period['windDirection']}
            Forecast: {period['detailedForecast']}
        """
        forecasts.append(forecast)
    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
