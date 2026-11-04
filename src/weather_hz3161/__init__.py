# read version from installed package
from importlib.metadata import version
__version__ = version("weather_hz3161")

from .weather_hz3161 import celsius_to_fahrenheit, summarize_temperatures, clean_readings
