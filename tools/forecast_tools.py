"""
Forecast tools exposed to Google ADK.

This module wraps the production weather forecast
service for use by Google ADK.
"""

from weather_intelligence_agent_v2.observability.tool_tracing import (
    trace_tool,
)
from weather_intelligence_agent_v2.services.weather_service import (
    get_7_day_forecast,
)


@trace_tool("get_forecast")
def get_forecast(
    city: str,
) -> dict:
    """
    Retrieve the seven-day weather forecast.

    Use this tool whenever a user asks about:

    - tomorrow
    - next week
    - forecast
    - rain prediction
    - future weather

    Args:
        city:
            City name.

    Returns:
        Structured seven-day forecast response.
    """

    forecast = get_7_day_forecast(
        city
    )

    return {
        "city": forecast.city,
        "country": forecast.country,
        "forecast": [
            {
                "date": day.date,
                "condition": day.condition,
                "max_temperature": day.max_temperature,
                "min_temperature": day.min_temperature,
                "rain_probability": day.rain_probability,
            }
            for day in forecast.forecast_days
        ],
    }