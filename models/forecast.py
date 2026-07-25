"""
Forecast domain models.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ForecastDay:
    """
    Represents one day's weather forecast.
    """

    date: str

    condition: str

    max_temperature: float

    min_temperature: float

    rain_probability: int


@dataclass(slots=True, frozen=True)
class Forecast:
    """
    Represents a city's seven-day forecast.
    """

    city: str

    country: str

    forecast_days: list[ForecastDay]