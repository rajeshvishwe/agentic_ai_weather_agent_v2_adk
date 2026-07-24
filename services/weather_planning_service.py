"""
File:
weather_intelligence_agent_v2/services/weather_planning_service.py

Phase:
6.9 - Structured Outputs

Purpose:
Enterprise orchestration service that coordinates
weather retrieval, forecasting, analytics and AI
weather intelligence while preventing duplicate
service calls.

This service produces a strongly typed
WeatherPlanning domain model.
"""

from weather_intelligence_agent_v2.analytics.forecast_analytics import (
    ForecastAnalytics,
)
from weather_intelligence_agent_v2.analytics.weather_intelligence import (
    WeatherIntelligence,
)
from weather_intelligence_agent_v2.models.weather_analytics_result import (
    WeatherAnalyticsResult,
)
from weather_intelligence_agent_v2.models.weather_context import (
    WeatherContext,
)
from weather_intelligence_agent_v2.models.weather_intelligence_result import (
    WeatherIntelligenceResult,
)
from weather_intelligence_agent_v2.models.weather_planning import (
    WeatherPlanning,
)
from weather_intelligence_agent_v2.services.weather_service import (
    get_7_day_forecast,
    get_weather_multiple,
)


class WeatherPlanningService:
    """
    Enterprise orchestration service.

    Coordinates all weather services required
    to generate a complete weather planning report.
    """

    def build_weather_plan(
        city: str,
    ) -> WeatherPlanning:
        """
        Build a complete weather planning report.

        Args:
            city:
                City name.

        Returns:
            WeatherPlanning domain model.
        """

        # ----------------------------------
        # Create request-scoped context
        # ----------------------------------

        context = WeatherContext(city=city)

        # ----------------------------------
        # Current Weather
        # ----------------------------------

        context.current_weather = (
            get_weather_multiple([city])[0]
        )

        # ----------------------------------
        # Forecast
        # ----------------------------------

        context.forecast = (
            get_7_day_forecast(city)
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        rainiest_day = (
            ForecastAnalytics.rainiest_day(
                context.forecast
            )
        )

        context.analytics = (
            WeatherAnalyticsResult(
                rainiest_day=rainiest_day
            )
        )

        # ----------------------------------
        # Intelligence
        # ----------------------------------

        recommendations = (
            WeatherIntelligence.generate_report(
                [context.current_weather],
                rainiest_day,
            )
        )

        risk_level = next(
            (
                item.replace(
                    "Overall Weather Risk Level : ",
                    "",
                )
                for item in recommendations
                if item.startswith(
                    "Overall Weather Risk Level"
                )
            ),
            "UNKNOWN",
        )

        context.intelligence = (
            WeatherIntelligenceResult(
                risk_level=risk_level,
                recommendations=recommendations,
            )
        )

        # ----------------------------------
        # Aggregate Response
        # ----------------------------------

        return WeatherPlanning(
            city=city,
            current_weather=context.current_weather,
            forecast=context.forecast,
            analytics=context.analytics,
            intelligence=context.intelligence,
        )