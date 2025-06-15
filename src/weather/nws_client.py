import httpx
from typing import Any

class NWSClient:
    """
    Client for interacting with the National Weather Service (NWS) API.
    """
    def __init__(self) -> None:
        pass

    async def _make_request(self, url: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Will raise HTTPStatusError for non-200
            try:
                return response.json()
            except ValueError as e:
                # Let JSON errors propagate for test coverage
                raise e
