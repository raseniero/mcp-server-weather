# Weather MCP Server

## NWSClient Public Interface

The `NWSClient` class provides an async method to fetch weather alerts for a given US state:

```python
from weather.nws_client import NWSClient
import asyncio

async def main():
    client = NWSClient()
    alerts = await client.get_alerts("CA")
    for alert in alerts:
        print(alert["headline"], alert["event"], alert["severity"])

asyncio.run(main())
```

- `get_alerts(state: str)` returns a list of alerts with `headline`, `event`, and `severity` keys.
- All network calls are async and can raise `httpx.HTTPStatusError` or `ValueError` for malformed responses.

## Testing & Coverage

- Tests use `pytest`, `pytest-asyncio`, and `pytest-cov`.
- Network calls are monkeypatched for isolation in unit tests.
- Run all tests with:
  ```sh
  pytest
  ```
- Generate an HTML coverage report with:
  ```sh
  pytest --cov=src --cov-report=html
  open htmlcov/index.html
  ```

## Fixtures & Mocking

- Test fixtures and monkeypatching are used to mock NWS API responses and isolate tests from network dependencies.
- See `tests/conftest.py` for reusable fixtures.
