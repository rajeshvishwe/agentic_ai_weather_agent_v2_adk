"""
Insight Engine

Generates human-readable weather insights from
analytics results.

This layer is intentionally rule-based.

Later, a Google ADK Agent or Gemini model can
enhance or replace these insights.
"""

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    ForecastDay,
)


class InsightEngine:
    """
    Generate natural-language weather insights.
    """

    @staticmethod
    def build_summary(
        weather_list: list[CurrentWeather],
        rainiest_day: ForecastDay,
    ) -> list[str]:
        """
        Build a collection of weather insights.

        Args:
            weather_list:
                Current weather from multiple cities.

            rainiest_day:
                Forecast day with the highest probability
                of rainfall.

        Returns:
            List of insight strings.
        """

        insights: list[str] = []

        hottest = max(
            weather_list,
            key=lambda city: city.temperature,
        )

        coolest = min(
            weather_list,
            key=lambda city: city.temperature,
        )

        windy = max(
            weather_list,
            key=lambda city: city.wind_speed,
        )

        spread = (
            hottest.temperature
            - coolest.temperature
        )

        average = (
            sum(
                city.temperature
                for city in weather_list
            )
            / len(weather_list)
        )

        insights.append(
            f"{hottest.city} is currently the hottest city "
            f"at {hottest.temperature:.1f}°C."
        )

        insights.append(
            f"{coolest.city} is currently the coolest city "
            f"at {coolest.temperature:.1f}°C."
        )

        insights.append(
            f"{windy.city} has the strongest wind "
            f"at {windy.wind_speed:.1f} km/h."
        )

        insights.append(
            f"The average temperature across all "
            f"selected cities is {average:.1f}°C."
        )

        insights.append(
            f"The temperature spread is "
            f"{spread:.1f}°C."
        )

        insights.append(
            f"The highest chance of rain "
            f"is on {rainiest_day.date} "
            f"({rainiest_day.rain_probability}%)."
        )

        return insights