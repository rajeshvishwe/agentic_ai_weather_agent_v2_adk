"""
Weather Intelligence Engine

Provides high-level reasoning and
recommendations based on weather analytics.

This layer represents deterministic AI.

Later it can be enhanced by an LLM.
"""

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    ForecastDay,
)


class WeatherIntelligence:
    """
    Advanced weather intelligence engine.
    """

    @staticmethod
    def generate_report(
        weather_list: list[CurrentWeather],
        rainiest_day: ForecastDay,
    ) -> list[str]:

        report: list[str] = []

        hottest = max(
            weather_list,
            key=lambda city: city.temperature,
        )

        coolest = min(
            weather_list,
            key=lambda city: city.temperature,
        )

        windiest = max(
            weather_list,
            key=lambda city: city.wind_speed,
        )

        # ----------------------------
        # Extreme Heat
        # ----------------------------

        if hottest.temperature >= 40:

            report.append(
                f"🔥 Extreme Heat Alert: "
                f"{hottest.city} is experiencing "
                f"{hottest.temperature:.1f}°C."
            )

            report.append(
                "Recommendation: Stay hydrated "
                "and avoid prolonged outdoor exposure."
            )

        elif hottest.temperature >= 35:

            report.append(
                f"🌡 Hot Weather: "
                f"{hottest.city} is warm at "
                f"{hottest.temperature:.1f}°C."
            )

        # ----------------------------
        # Cool Weather
        # ----------------------------

        if coolest.temperature <= 10:

            report.append(
                f"❄ Cold Conditions in "
                f"{coolest.city}."
            )

        # ----------------------------
        # Wind Alert
        # ----------------------------

        if windiest.wind_speed >= 15:

            report.append(
                f"💨 Strong winds expected in "
                f"{windiest.city} "
                f"({windiest.wind_speed:.1f} km/h)."
            )

        # ----------------------------
        # Rain Alert
        # ----------------------------

        if rainiest_day.rain_probability >= 80:

            report.append(
                f"🌧 Heavy rain likely on "
                f"{rainiest_day.date} "
                f"({rainiest_day.rain_probability}%)."
            )

            report.append(
                "Carry an umbrella or raincoat."
            )

        # ----------------------------
        # Risk Level
        # ----------------------------

        if (
            hottest.temperature >= 40
            or rainiest_day.rain_probability >= 90
        ):

            risk = "HIGH"

        elif (
            hottest.temperature >= 35
            or rainiest_day.rain_probability >= 60
        ):

            risk = "MEDIUM"

        else:

            risk = "LOW"

        report.append(
            f"Overall Weather Risk Level : {risk}"
        )

        return report