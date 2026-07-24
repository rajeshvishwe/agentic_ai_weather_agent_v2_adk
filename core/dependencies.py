"""
FastAPI dependency providers.

Application-scoped services are created during FastAPI lifespan
startup and retrieved from application state by dependency
providers.
"""

from fastapi import Request

from weather_intelligence_agent_v2.services.async_weather_planning_service import (
    AsyncWeatherPlanningService,
)
from weather_intelligence_agent_v2.services.weather_chat_service import (
    WeatherChatService,
)


def get_async_weather_planning_service(
    request: Request,
) -> AsyncWeatherPlanningService:
    """
    Retrieve the application-scoped async weather planning service.

    Args:
        request:
            Current FastAPI request.

    Returns:
        Application-scoped AsyncWeatherPlanningService.
    """

    return (
        request.app.state
        .async_weather_planning_service
    )


def get_weather_chat_service(
    request: Request,
) -> WeatherChatService:
    """
    Retrieve the application-scoped weather chat service.

    Args:
        request:
            Current FastAPI request.

    Returns:
        Application-scoped WeatherChatService.
    """

    return request.app.state.weather_chat_service