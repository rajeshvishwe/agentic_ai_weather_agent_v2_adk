"""
Weather planning tool exposed to Google ADK.

This module exposes the enterprise Weather Planning
orchestration service while keeping business logic inside
the service layer.
"""

from dataclasses import asdict

from weather_intelligence_agent_v2.observability.tool_tracing import (
    trace_tool,
)
from weather_intelligence_agent_v2.services.weather_planning_service import (
    WeatherPlanningService,
)


@trace_tool("get_weather_plan")
def get_weather_plan(
    city: str,
) -> dict:
    """
    Generate a complete weather planning report.

    Use this tool when users ask for:

    - Complete weather report
    - Travel planning
    - Outdoor activity planning
    - Combined weather insights
    - Weather recommendations
    - End-to-end weather analysis

    Args:
        city:
            Name of the city.

    Returns:
        JSON-serializable weather planning response.
    """

    plan = WeatherPlanningService.build_weather_plan(
        city
    )

    return asdict(
        plan
    )