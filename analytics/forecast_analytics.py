"""
Forecast analytics engine.
"""

from weather_intelligence_agent_v2.models import (
    Forecast,
    ForecastDay,
)


class ForecastAnalytics:
    """
    Business analytics for forecast data.
    """

    @staticmethod
    def highest_rain_probability(
        forecast: Forecast,
    ) -> int:
        """
        Return the maximum rain probability.
        """

        return max(
            day.rain_probability
            for day in forecast.forecast_days
        )

    @staticmethod
    def rainiest_day(
        forecast: Forecast,
    ) -> ForecastDay:
        """
        Return the forecast day with the
        highest rain probability.
        """

        return max(
            forecast.forecast_days,
            key=lambda day: day.rain_probability,
        )