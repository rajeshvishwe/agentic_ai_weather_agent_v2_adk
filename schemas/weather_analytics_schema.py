"""
Weather analytics API response schema.
"""

from pydantic import BaseModel
from pydantic import ConfigDict

from weather_intelligence_agent_v2.schemas.forecast_schema import (
    ForecastDayResponse,
)


class WeatherAnalyticsResponse(BaseModel):
    """
    API response representation of weather analytics.

    This schema maps the WeatherAnalyticsResult
    domain model into an API-safe response model.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    rainiest_day: ForecastDayResponse