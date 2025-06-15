import httpx
from typing import Any

class NWSClient:
    """
    Client for interacting with the National Weather Service (NWS) API.
    """
    def __init__(self) -> None:
        pass

    async def get_alerts(self, state: str):
        """
        Fetch active weather alerts for a given US state.
        Returns a list of dicts with keys: headline, event, severity.
        """
        import asyncio
        url = f"https://api.weather.gov/alerts/active?area={state}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                data = await self._make_request(url)
                break
            except httpx.HTTPStatusError as e:
                if hasattr(e, 'response') and e.response is not None and getattr(e.response, 'status_code', None) == 429:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1)
                        continue
                raise
        else:
            raise httpx.HTTPStatusError("Too Many Requests after retries", request=None, response=None)
        features = data.get("features")
        if not isinstance(features, list):
            raise ValueError("Malformed response: missing or invalid 'features' key")
        alerts = []
        for feature in features:
            prop = feature.get("properties", {})
            alerts.append({
                "headline": prop.get("headline"),
                "event": prop.get("event"),
                "severity": prop.get("severity"),
            })
        return alerts

    async def _make_request(self, url: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Will raise HTTPStatusError for non-200
            try:
                return response.json()
            except ValueError as e:
                # Let JSON errors propagate for test coverage
                raise
