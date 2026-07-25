"""
File:
weather_intelligence_agent_v2/models/weather_planning.py

Phase:
6.9 - Structured Outputs

Purpose:
Aggregate domain model representing a complete
weather planning result.

This model combines current weather, forecast,
analytics and AI-generated intelligence into a
single strongly typed object.

It is produced by the WeatherPlanningService and
consumed by higher application layers such as
Google ADK tools, FastAPI endpoints and
Streamlit dashboards.
"""

from dataclasses import dataclass, field
from datetime import datetime

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
)

from weather_intelligence_agent_v2.models.weather_analytics_result import (
    WeatherAnalyticsResult,
)

from weather_intelligence_agent_v2.models.weather_intelligence_result import (
    WeatherIntelligenceResult,
)


@dataclass(slots=True, frozen=True)
class WeatherPlanning:
    """
    Aggregate weather planning domain model.

    Represents the complete planning information
    required for weather-aware decision making.

    This model intentionally contains only
    strongly typed domain objects.
    """

    city: str

    current_weather: CurrentWeather

    forecast: Forecast

    analytics: WeatherAnalyticsResult

    intelligence: WeatherIntelligenceResult

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )