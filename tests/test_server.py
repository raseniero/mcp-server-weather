import pytest
from mcp.server.fastmcp import FastMCP
import asyncio

import sys
import os
import types

import importlib.util

# Helper to import the server module
@pytest.fixture(scope="module")
def server_module():
    server_path = os.path.join(os.path.dirname(__file__), "..", "src", "weather", "server.py")
    spec = importlib.util.spec_from_file_location("weather.server", server_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["weather.server"] = module
    spec.loader.exec_module(module)
    return module

@pytest.mark.asyncio
async def test_server_initialization(server_module):
    """Test that the FastMCP server initializes without error."""
    assert hasattr(server_module, "mcp")
    assert isinstance(server_module.mcp, FastMCP)
    assert server_module.mcp.name == "weather"

@pytest.mark.asyncio
async def test_get_alerts_tool_registration(server_module):
    """Test that get_alerts is registered as a tool."""
    assert hasattr(server_module, "get_alerts")
    assert callable(server_module.get_alerts)
    # Check if get_alerts is registered as a tool in FastMCP
    assert "get_alerts" in server_module.mcp.tools

@pytest.mark.asyncio
async def test_get_forecast_tool_registration(server_module):
    """Test that get_forecast is registered as a tool."""
    assert hasattr(server_module, "get_forecast")
    assert callable(server_module.get_forecast)
    assert "get_forecast" in server_module.mcp.tools

@pytest.mark.asyncio
async def test_get_alerts_invalid_state(server_module):
    """Test get_alerts with an invalid state code returns an error message."""
    result = await server_module.get_alerts("XX")
    assert "Unable to fetch alerts" in result or "No active alerts" in result

@pytest.mark.asyncio
async def test_get_forecast_invalid_coords(server_module):
    """Test get_forecast with invalid coordinates returns an error message."""
    result = await server_module.get_forecast(0.0, 0.0)
    assert "Unable to fetch forecast" in result or "Unable to fetch detailed forecast." in result
