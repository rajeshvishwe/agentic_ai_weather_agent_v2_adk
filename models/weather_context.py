"""
File:
weather_intelligence_agent_v2/models/weather_context.py

Phase:
6.8 - AI Orchestration Layer

Purpose:
Internal orchestration model that stores all shared
weather information during a single request.

This model is NOT returned to the user.

It exists only while WeatherPlanningService
coordinates multiple business services.
"""

from dataclasses import dataclass, field

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
)


@dataclass(slots=True)
class WeatherContext:
    """
    Shared orchestration context.

    This object acts as a request-scoped cache.

    All downstream analytics and intelligence
    consume data from this context instead of
    performing duplicate API calls.
    """

    city: str

    current_weather: CurrentWeather | None = None

    forecast: Forecast | None = None

    analytics: dict = field(default_factory=dict)

    intelligence: dict = field(default_factory=dict)