"""
Tests for the weather_hz3161 package.

Copied from my HW6 tests (QMSS G5072 Homework 6), with the imports changed to use
the package. The tests for fetch_forecast, heat_alert and run_pipeline were dropped,
because those functions are not part of the package.
"""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

import weather_hz3161
from weather_hz3161 import (
    celsius_to_fahrenheit,
    clean_readings,
    summarize_temperatures,
)


def test_version_is_defined():
    assert isinstance(weather_hz3161.__version__, str)


# =============================================================================
# UNIT TESTS
# =============================================================================


@pytest.mark.parametrize("celsius, expected", [
    (0, 32.0),            # freezing point
    (100, 212.0),         # boiling point
    (-40, -40.0),         # both scales meet
    (37, 98.6),           # body temperature (float result is 98.60000000000001)
    (-273.15, -459.67),   # absolute zero itself is allowed
])
def test_celsius_to_fahrenheit(celsius, expected):
    """Check known Celsius-to-Fahrenheit conversions, allowing for float rounding."""
    assert celsius_to_fahrenheit(celsius) == pytest.approx(expected)


@pytest.mark.parametrize("bad_input, expected_error", [
    ("30", TypeError),        # a string is not a number
    (None, TypeError),        # missing value
    ([25.0], TypeError),      # a list is not a number
    (-273.16, ValueError),    # just below absolute zero
])
def test_celsius_to_fahrenheit_invalid(bad_input, expected_error):
    """Check that invalid inputs raise the error named in the docstring."""
    with pytest.raises(expected_error):
        celsius_to_fahrenheit(bad_input)


def test_summarize_temperatures():
    """Check all four summary values for a list that contains one NaN."""
    # Arrange
    temps = [10.0, float("nan"), 20.0, 30.0]

    # Act
    result = summarize_temperatures(temps)

    # Assert
    assert result["mean"] == pytest.approx(20.0)
    assert result["min"] == 10.0
    assert result["max"] == 30.0
    assert result["n_missing"] == 1


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def raw_readings():
    """Unsorted readings with one missing and one implausible temperature."""
    return pd.DataFrame({
        "station": ["JFK", "CPK", "JFK", "CPK", "LGA"],
        "date": ["2026-07-02", "2026-07-01", "2026-07-01", "2026-07-02", "2026-07-01"],
        "temp_c": [30.0, 25.0, float("nan"), 999.0, 28.0],
    })


def test_raw_readings_fixture(raw_readings):
    """Check the fixture's columns, number of rows, and number of missing values."""
    assert list(raw_readings.columns) == ["station", "date", "temp_c"]
    assert len(raw_readings) == 5
    assert raw_readings["temp_c"].isna().sum() == 1


# =============================================================================
# TESTING DATAFRAMES
# =============================================================================


def test_clean_readings(raw_readings):
    """Compare clean_readings with an expected DataFrame built by hand."""
    # Arrange: the NaN (JFK, 07-01) and the 999.0 (CPK, 07-02) rows are dropped,
    # the rest is sorted by station, then date, with a fresh 0..n-1 index.
    expected = pd.DataFrame({
        "station": ["CPK", "JFK", "LGA"],
        "date": ["2026-07-01", "2026-07-02", "2026-07-01"],
        "temp_c": [25.0, 30.0, 28.0],
        "temp_f": [77.0, 86.0, 82.4],
    })

    # Act
    result = clean_readings(raw_readings)

    # Assert
    assert_frame_equal(result, expected)
