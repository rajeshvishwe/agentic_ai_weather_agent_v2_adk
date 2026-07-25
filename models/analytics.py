"""
Analytics domain models.
"""

from dataclasses import dataclass

from weather_intelligence_agent_v2.models.current_weather import (
    CurrentWeather,
)


@dataclass(slots=True, frozen=True)
class WeatherSummary:
    """
    Aggregated analytics for multiple cities.
    """

    average_temperature: float

    hottest_city: CurrentWeather

    coolest_city: CurrentWeather

    highest_wind_city: CurrentWeather

    temperature_spread: float