"""
Weather Analytics tools exposed to Google ADK.

These tools wrap the production analytics layer and
return structured analytical results.
"""

from weather_intelligence_agent_v2.analytics.weather_analytics import (
    WeatherAnalytics,
)
from weather_intelligence_agent_v2.observability.tool_tracing import (
    trace_tool,
)
from weather_intelligence_agent_v2.services.weather_service import (
    get_weather_multiple,
)


@trace_tool("analyze_weather")
def analyze_weather(
    cities: list[str],
) -> dict:
    """
    Analyze weather for multiple cities.

    Use this tool when users ask:

    - Compare cities
    - Which city is hottest?
    - Which city is coolest?
    - Highest wind speed
    - Average temperature

    Args:
        cities:
            Cities to analyze.

    Returns:
        Structured weather analytics response.
    """

    weather_list = get_weather_multiple(
        cities
    )

    summary = WeatherAnalytics.generate_summary(
        weather_list
    )

    return {
        "cities": cities,
        "average_temperature": summary.average_temperature,
        "temperature_spread": summary.temperature_spread,
        "hottest_city": {
            "city": summary.hottest_city.city,
            "temperature": summary.hottest_city.temperature,
        },
        "coolest_city": {
            "city": summary.coolest_city.city,
            "temperature": summary.coolest_city.temperature,
        },
        "highest_wind_city": {
            "city": summary.highest_wind_city.city,
            "wind_speed": summary.highest_wind_city.wind_speed,
        },
    }