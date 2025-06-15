import httpx
from typing import Any

class NWSClient:
    """
    Client for interacting with the National Weather Service (NWS) API.

    Provides methods to fetch weather alerts and other data from the NWS API asynchronously.
    """
    def __init__(self) -> None:
        """
        Initialize a new NWSClient instance.
        """
        pass

    async def get_alerts(self, state: str) -> list[dict[str, Any]]:
        """
        Fetch active weather alerts for a given US state from the NWS API.

        Args:
            state (str): Two-letter US state code (e.g., 'CA', 'NY').

        Returns:
            list[dict[str, Any]]: A list of alert dictionaries, each containing:
                - 'headline': str or None
                - 'event': str or None
                - 'severity': str or None

        Raises:
            httpx.HTTPStatusError: If the response status is not 200.
            ValueError: If the response is not valid JSON.
        """
        url = f"https://api.weather.gov/alerts/active?area={state}"
        data = await self._make_request(url)
        features = data.get("features", [])
        alerts = []
        for feature in features:
            props = feature.get("properties", {})
            alerts.append({
                "headline": props.get("headline"),
                "event": props.get("event"),
                "severity": props.get("severity"),
            })
        return alerts

    async def _make_request(self, url: str) -> dict[str, Any]:
        """
        Make an asynchronous GET request to the given URL and return the parsed JSON response.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            dict[str, Any]: The parsed JSON response.

        Raises:
            httpx.HTTPStatusError: If the response status is not 200.
            ValueError: If the response body is not valid JSON.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Will raise HTTPStatusError for non-200
            try:
                return response.json()
            except ValueError as e:
                # Let JSON errors propagate for test coverage
                raise
