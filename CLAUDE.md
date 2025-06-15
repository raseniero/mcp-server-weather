# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Weather MCP (Model Context Protocol) Server that exposes National Weather Service (NWS) alerts and forecasts via FastMCP tools. The server is built with Python 3.13+ and uses httpx for async HTTP requests.

## Common Development Commands

### Running the Server
```bash
# Run with uv (recommended)
uv run main.py

# Or run directly
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_get_alerts
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Development Setup
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx

# Install dev dependencies
pip install -e ".[dev]"
```

## Architecture

### Core Components
- **main.py**: Entry point that runs the MCP server
- **src/weather/server.py**: FastMCP server with two tools:
  - `get_alerts(state)`: Fetches weather alerts for US states
  - `get_forecast(latitude, longitude)`: Fetches weather forecasts by coordinates
- **src/weather/nws_client.py**: NWS API client with retry logic and error handling

### Key Design Patterns
- **Async/await** throughout for non-blocking I/O operations
- **MCP tools pattern** for exposing weather functionality via RPC
- **Client abstraction** (NWSClient) isolates API interactions
- **Retry logic** for handling rate limits (429 responses)
- **Input validation** on all tool parameters

### Testing Strategy
- Tests use pytest with asyncio support
- Network calls are mocked using monkeypatch
- Test fixtures in `tests/conftest.py` provide sample API responses
- Coverage requirement: 80% minimum

## Important Notes

1. **Known Issues**: There's a duplicate `get_alerts` function definition in server.py (lines 90-112 and 132-155) that should be resolved.

2. **API Rate Limits**: The NWS API client includes retry logic for 429 responses. Be mindful of rate limits during development.

3. **Error Handling**: All tools return user-friendly error messages as strings rather than raising exceptions to the MCP client.

4. **Type Safety**: The project uses type hints throughout. Run mypy before committing changes.

5. **Code Style**: Follow Black formatting (88 char line length) and Flake8 linting rules defined in pyproject.toml.