"""
Weather tools exposed to Google ADK.

This module exposes production weather services as
Google ADK tools.

Business logic remains inside the service layer.
"""

from weather_intelligence_agent_v2.observability.tool_tracing import (
    trace_tool,
)
from weather_intelligence_agent_v2.services.async_weather_service import (
    AsyncWeatherService,
)


@trace_tool("get_current_weather")
async def get_current_weather(
    city: str,
) -> dict:
    """
    Get the current weather for a city.

    This function acts as a Google ADK tool adapter between
    the AI agent and the asynchronous weather service.

    Args:
        city:
            City name.

    Returns:
        Weather information as a dictionary suitable for
        Google ADK tool responses.
    """

    try:
        async with AsyncWeatherService() as service:

            weather = await service.get_current_weather(
                city
            )

        return {
            "success": True,
            "city": weather.city,
            "country": weather.country,
            "temperature": weather.temperature,
            "wind_speed": weather.wind_speed,
            "wind_direction": weather.wind_direction,
            "condition": weather.condition,
            "observation_time": weather.observation_time,
        }

    except ValueError as exc:

        return {
            "success": False,
            "message": str(exc),
        }