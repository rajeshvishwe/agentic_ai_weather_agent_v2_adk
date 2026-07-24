"""
Async Weather Planning Service.

This module provides asynchronous orchestration for
building complete weather planning reports.

Responsibilities:
- Retrieve current weather asynchronously.
- Retrieve forecast data asynchronously.
- Execute weather analytics.
- Generate weather intelligence.
- Return a strongly typed WeatherPlanning domain model.

The service coordinates domain operations but does not
implement HTTP communication directly.
"""

import asyncio

from weather_intelligence_agent_v2.analytics.forecast_analytics import (
    ForecastAnalytics,
)
from weather_intelligence_agent_v2.analytics.weather_intelligence import (
    WeatherIntelligence,
)
from weather_intelligence_agent_v2.models.weather_analytics_result import (
    WeatherAnalyticsResult,
)
from weather_intelligence_agent_v2.models.weather_intelligence_result import (
    WeatherIntelligenceResult,
)
from weather_intelligence_agent_v2.models.weather_planning import (
    WeatherPlanning,
)
from weather_intelligence_agent_v2.services.async_weather_service import (
    AsyncWeatherService,
)


class AsyncWeatherPlanningService:
    """
    Asynchronous weather planning orchestration service.

    Coordinates asynchronous weather retrieval,
    analytics, and intelligence generation.

    The service returns a complete WeatherPlanning
    domain model.
    """

    def __init__(
        self,
        weather_service: AsyncWeatherService | None = None,
    ) -> None:
        """
        Initialize the async planning service.

        Args:
            weather_service:
                Optional AsyncWeatherService dependency.

                Supplying the dependency enables dependency
                injection and simplifies unit testing.
        """

        self._weather_service = (
            weather_service
            or AsyncWeatherService()
        )

    async def build_weather_plan(
        self,
        city: str,
    ) -> WeatherPlanning:
        """
        Build a complete weather planning report.

        Current weather and forecast retrieval are independent
        network operations and are therefore executed concurrently.

        Args:
            city:
                City name.

        Returns:
            Complete WeatherPlanning domain model.
        """

        (
            current_weather,
            forecast,
        ) = await asyncio.gather(
            self._weather_service.get_current_weather(
                city
            ),
            self._weather_service.get_7_day_forecast(
                city
            ),
        )

        rainiest_day = (
            ForecastAnalytics.rainiest_day(
                forecast
            )
        )

        analytics = WeatherAnalyticsResult(
            rainiest_day=rainiest_day
        )

        recommendations = (
            WeatherIntelligence.generate_report(
                [current_weather],
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

        intelligence = (
            WeatherIntelligenceResult(
                risk_level=risk_level,
                recommendations=recommendations,
            )
        )

        return WeatherPlanning(
            city=city,
            current_weather=current_weather,
            forecast=forecast,
            analytics=analytics,
            intelligence=intelligence,
        )

    async def close(
        self,
    ) -> None:
        """
        Release resources owned by the underlying
        asynchronous weather service.
        """

        await self._weather_service.close()