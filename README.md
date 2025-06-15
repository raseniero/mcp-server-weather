# Weather MCP Server

A lightweight FastMCP service exposing National Weather Service alerts and forecasts via simple RPC-style “tools”.

## Installation

Install from PyPI:

```bash
pip install weather-mcp-server
```

Or install from source for development:

```bash
git clone https://github.com/YourOrg/weather-mcp-server.git
cd weather-mcp-server
pip install -e ".[dev]"
```

## Usage

### As a Python library

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

### As a FastMCP server

```bash
weather-mcp-server --transport stdio
```

## API Reference

### get_alerts

Fetch formatted weather alerts for a given two-letter US state code.

**Arguments:**
- `state` (str): Two-letter uppercase state abbreviation (e.g. "CA").

**Returns:**
- `str`: Formatted alerts separated by `---`, or an error message.

### get_forecast

Fetch formatted weather forecast for a location.

**Arguments:**
- `latitude` (float): Latitude between -90 and 90.
- `longitude` (float): Longitude between -180 and 180.

**Returns:**
- `str`: Forecast for up to next 5 periods or an error message.

### /health

Health check endpoint.

**HTTP GET** `/health`

**Returns JSON:**
- `{"status": "ok"}`

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
