"""
Weather Intelligence tools exposed to Google ADK.

This tool combines multiple services and analytics
to generate actionable weather recommendations.
"""

from weather_intelligence_agent_v2.analytics.forecast_analytics import (
    ForecastAnalytics,
)

from weather_intelligence_agent_v2.analytics.weather_intelligence import (
    WeatherIntelligence,
)

from weather_intelligence_agent_v2.services.weather_service import (
    get_7_day_forecast,
    get_weather_multiple,
)


def get_weather_intelligence(city: str) -> dict:
    """
    Generate weather intelligence for a city.

    Use this tool when users ask:

    - Is it safe to go outside?
    - Should I carry an umbrella?
    - Is it good for walking?
    - Weather alerts
    - Weather recommendations
    - Weather risk
    """

    weather_list = get_weather_multiple([city])

    forecast = get_7_day_forecast(city)

    rainiest_day = ForecastAnalytics.rainiest_day(
        forecast
    )

    report = WeatherIntelligence.generate_report(
        weather_list,
        rainiest_day,
    )

    return {
        "city": city,
        "risk_level": next(
            (
                item.replace(
                    "Overall Weather Risk Level : ",
                    "",
                )
                for item in report
                if item.startswith(
                    "Overall Weather Risk Level"
                )
            ),
            "UNKNOWN",
        ),
        "recommendations": report,
    }