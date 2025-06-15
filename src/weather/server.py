from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

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
            return response.json()
        except Exception:
            return None


async def get_alerts_data(state: str) -> list[dict[str, Any]]:
    """
    Fetches weather alerts for a given US state and returns a list of alerts with event info.
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return []
    alerts = []
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


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


async def get_forecast_data(latitude: float, longitude: float) -> list[dict[str, Any]]:
    """
    Internal: Fetch forecast periods for given coordinates.
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data or "properties" not in points_data or "forecast" not in points_data["properties"]:
        return []
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data or "properties" not in forecast_data or "periods" not in forecast_data["properties"]:
        return []
    return forecast_data["properties"]["periods"]

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    periods = await get_forecast_data(latitude, longitude)
    if not periods:
        return "Unable to fetch forecast data for this location."
    forecasts = []
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
