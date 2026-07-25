"""
File:
weather_intelligence_agent_v2/models/weather_plan_result.py

Phase:
6.9 – Structured Outputs

Purpose:
Complete structured weather planning result.
"""

from dataclasses import dataclass

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
)

from weather_intelligence_agent_v2.models.response_metadata import (
    ResponseMetadata,
)

from weather_intelligence_agent_v2.models.weather_analytics_result import (
    WeatherAnalyticsResult,
)

from weather_intelligence_agent_v2.models.weather_intelligence_result import (
    WeatherIntelligenceResult,
)


@dataclass(slots=True, frozen=True)
class WeatherPlanResult:
    """
    Public weather planning response.
    """

    metadata: ResponseMetadata

    city: str

    current_weather: CurrentWeather

    forecast: Forecast

    analytics: WeatherAnalyticsResult

    intelligence: WeatherIntelligenceResult