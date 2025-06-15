# Weather MCP Server

A lightweight FastMCP service exposing National Weather Service alerts and forecasts via simple RPC-style "tools".

## Installation

First, install [uv](https://github.com/astral-sh/uv) (a fast Python package manager) if you don't have it already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Create virtual environment and activate it
```bash
uv venv
source .venv/bin/activate
```

# Install dependencies
```bash
uv add "mcp[cli]" httpx
```

Then install from PyPI:

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

Or

```bash
uv run main.py
```

To run the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```
Copy the Session token and the Proxy server listening on, example below:

```bash
Proxy server listening on 127.0.0.1:6277
Session token: dc7a47f8b6b1a3eede7c507a8d1c9a7f7e6b3ff46c138f8480bbfbae3c45a9e4
```

Open the MCP Inspector in your browser:http://127.0.0.1:6274, and in the Configuration, paste the *Inspector Proxy Address* and *Proxy Session Token*

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
