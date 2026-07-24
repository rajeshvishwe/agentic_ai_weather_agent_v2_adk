"""
File:
weather_intelligence_agent_v2/tools/planning_tools.py

Phase:
6.9 - Structured Outputs

Purpose:
Google ADK tool exposing the enterprise
Weather Planning orchestration service.

This tool delegates all business logic to the
WeatherPlanningService and returns a JSON-
serializable representation of the planning model.
"""

from dataclasses import asdict

from weather_intelligence_agent_v2.services.weather_planning_service import (
    WeatherPlanningService,
)


def get_weather_plan(city: str) -> dict:
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

    return asdict(plan)