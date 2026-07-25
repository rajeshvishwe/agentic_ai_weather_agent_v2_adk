"""
Domain model representing the current weather for a city.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CurrentWeather:
    """
    Immutable domain model representing
    the current weather conditions for a city.
    """

    city: str
    country: str

    temperature: float

    wind_speed: float

    wind_direction: float

    condition: str

    observation_time: str