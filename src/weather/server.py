from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from src.weather.nws_client import NWSClient


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




async def get_alerts_data(
    state: str, client: NWSClient | None = None
) -> list[dict[str, Any]] | None:
    """
    Fetch weather alerts for a given US state from the NWS API using NWSClient.

    Args:
        state: Two-letter US state code (e.g. 'CA', 'NY').
        client: Optional NWSClient instance (for mocking/testing).

    Returns:
        A list of alert dictionaries with keys: 'headline', 'event', 'severity'.
        Returns None if the response is missing or malformed.
    """
    if client is None:
        client = NWSClient()
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    try:
        data = await client._make_request(url)
        if not data:
            return None
        if "features" not in data:
            return None
        if not isinstance(data["features"], list):
            return None
        alerts: list[dict[str, Any]] = []
        for feature in data["features"]:
            props = feature.get("properties", {})
            alerts.append(
                {
                    "headline": props.get("headline"),
                    "event": props.get("event"),
                    "severity": props.get("severity"),
                    "areaDesc": props.get("areaDesc"),
                    "description": props.get("description"),
                    "instruction": props.get("instruction"),
                }
            )
        return alerts
    except (httpx.HTTPStatusError, ValueError):
        return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string, including the headline."""
    props = feature["properties"]
    return f"""
        Headline: {props.get('headline', 'No headline available')}
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
    """


US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}


@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    FastMCP tool: Return formatted weather alerts for a US state using NWSClient.

    Args:
        state: Two-letter US state code (e.g. 'CA', 'NY').

    Returns:
        A formatted string of alerts or an error message.
    """
    # Input validation
    if (
        not isinstance(state, str)
        or len(state) != 2
        or not state.isalpha()
        or not state.isupper()
        or state not in US_STATES
    ):
        return (
            "Invalid state code. Please provide a two-letter uppercase "
            "state abbreviation."
        )
    client = NWSClient()
    alerts_data = await get_alerts_data(state, client=client)
    if alerts_data is None:
        # Distinguish between malformed and empty
        # If the API response is missing or malformed
        return "Malformed response from weather service."
    if not alerts_data:
        return f"No active alerts for state: {state}"
    # Format each alert using the format_alert function
    formatted = [format_alert({"properties": alert}) for alert in alerts_data]
    return "\n---\n".join(formatted)


async def get_forecast_data(
    latitude: float, longitude: float, client: NWSClient | None = None
) -> list[dict[str, Any]]:
    """
    Fetch forecast periods for given coordinates from the NWS API using NWSClient.

    Args:
        latitude: Latitude of the location (-90 to 90).
        longitude: Longitude of the location (-180 to 180).
        client: Optional NWSClient instance (for mocking/testing).

    Returns:
        A list of forecast period dictionaries.
    Raises:
        ValueError: If the response is malformed or missing required keys.
    """
    if client is None:
        client = NWSClient()
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await client._make_request(points_url)
    if (
        not points_data
        or "properties" not in points_data
        or "forecast" not in points_data["properties"]
    ):
        raise ValueError("Malformed response: missing 'properties' or 'forecast'.")
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await client._make_request(forecast_url)
    if (
        not forecast_data
        or "properties" not in forecast_data
        or "periods" not in forecast_data["properties"]
    ):
        raise ValueError("Malformed response: missing 'properties' or 'periods'.")
    periods = forecast_data["properties"]["periods"]
    if not isinstance(periods, list):
        raise ValueError("Malformed response: 'periods' is not a list.")
    return periods


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    FastMCP tool: Return formatted weather forecast for a location using NWSClient.

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
        return (
            "Invalid coordinates. Latitude must be between -90 and 90, "
            "longitude between -180 and 180."
        )
    client = NWSClient()
    try:
        periods = await get_forecast_data(lat, lon, client=client)
    except (httpx.HTTPStatusError, ValueError):
        return "Malformed response from weather service."
    except Exception:
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


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
