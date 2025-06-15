"""
Tests for mock NWS API responses.

This module contains tests that verify our mock NWS API response data structures
match the expected formats for both alerts and forecast endpoints.
"""

import pytest
from pathlib import Path
import json

# Sample response data will be loaded from files in tests/fixtures/
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Test data file paths
ALERTS_RESPONSE_FILE = FIXTURES_DIR / "sample_alerts_response.json"
FORECAST_RESPONSE_FILE = FIXTURES_DIR / "sample_forecast_response.json"

# Expected top-level keys for API responses
ALERTS_TOP_LEVEL_KEYS = {"@context", "features", "title", "updated", "type"}
FORECAST_TOP_LEVEL_KEYS = {"@context", "geometry", "properties", "type"}


class TestNWSMockResponses:
    """Test that our mock NWS API responses have the expected structure."""

    @pytest.fixture(scope="class")
    def sample_alerts_response(self):
        """Load sample alerts response from fixture file."""
        with open(ALERTS_RESPONSE_FILE) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def sample_forecast_response(self):
        """Load sample forecast response from fixture file."""
        with open(FORECAST_RESPONSE_FILE) as f:
            return json.load(f)

    def test_alerts_response_structure(self, sample_alerts_response):
        """Verify the structure of the sample alerts response."""
        # Check top-level keys
        assert set(sample_alerts_response.keys()) == ALERTS_TOP_LEVEL_KEYS

        # Check features array exists and has at least one alert
        assert "features" in sample_alerts_response
        assert isinstance(sample_alerts_response["features"], list)

        # If there are alerts, check their structure
        if sample_alerts_response["features"]:
            alert = sample_alerts_response["features"][0]
            assert "properties" in alert
            assert "event" in alert["properties"]
            assert "headline" in alert["properties"]
            assert "description" in alert["properties"]

    def test_forecast_response_structure(self, sample_forecast_response):
        """Verify the structure of the sample forecast response."""
        # Check top-level keys
        assert set(sample_forecast_response.keys()) == FORECAST_TOP_LEVEL_KEYS

        # Check properties exists and has forecast data
        assert "properties" in sample_forecast_response
        properties = sample_forecast_response["properties"]

        # Check forecast periods exist
        assert "periods" in properties
        assert isinstance(properties["periods"], list)

        # If there are forecast periods, check their structure
        if properties["periods"]:
            period = properties["periods"][0]
            assert "name" in period
            assert "temperature" in period
            assert "shortForecast" in period
            assert "detailedForecast" in period

    def test_forecast_geometry_structure(self, sample_forecast_response):
        """Verify the structure of the forecast response geometry."""
        assert "geometry" in sample_forecast_response
        geometry = sample_forecast_response["geometry"]
        assert "type" in geometry
        assert "coordinates" in geometry

        # Should be a polygon with coordinates
        assert geometry["type"] == "Polygon"
        assert isinstance(geometry["coordinates"], list)
