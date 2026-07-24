"""
Weather Planning API response schema.
"""

from pydantic import BaseModel
from pydantic import ConfigDict

from weather_intelligence_agent_v2.schemas.current_weather_schema import (
    CurrentWeatherResponse,
)
from weather_intelligence_agent_v2.schemas.forecast_schema import (
    ForecastResponse,
)
from weather_intelligence_agent_v2.schemas.weather_analytics_schema import (
    WeatherAnalyticsResponse,
)
from weather_intelligence_agent_v2.schemas.weather_intelligence_schema import (
    WeatherIntelligenceResponse,
)


class WeatherPlanningResponse(BaseModel):
    """
    Complete response returned by the Weather Planning API.

    The schema mirrors the WeatherPlanning domain model while
    maintaining a clean separation between domain models and
    external API contracts.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    current_weather: CurrentWeatherResponse

    forecast: ForecastResponse

    analytics: WeatherAnalyticsResponse

    intelligence: WeatherIntelligenceResponse