"""
Weather Analytics Engine.

This module contains business logic for analyzing weather
data. It operates only on domain models and never calls
external APIs.
"""

from weather_intelligence_agent_v2.models import CurrentWeather

from weather_intelligence_agent_v2.models import (
    WeatherSummary,
)


class WeatherAnalytics:
    """
    Performs analytics on weather data.
    """

    @staticmethod
    def average_temperature(
        weather_list: list[CurrentWeather],
    ) -> float:
        """
        Calculate the average temperature.
        """

        if not weather_list:
            return 0.0

        total = sum(
            weather.temperature
            for weather in weather_list
        )

        return round(total / len(weather_list), 2)

    @staticmethod
    def hottest_city(
        weather_list: list[CurrentWeather],
    ) -> CurrentWeather:
        """
        Return the hottest city.
        """

        return max(
            weather_list,
            key=lambda weather: weather.temperature,
        )

    @staticmethod
    def coolest_city(
        weather_list: list[CurrentWeather],
    ) -> CurrentWeather:
        """
        Return the coolest city.
        """

        return min(
            weather_list,
            key=lambda weather: weather.temperature,
        )
    
    @staticmethod
    def highest_wind_city(
        weather_list: list[CurrentWeather],
    ) -> CurrentWeather:
        """
        Return the city with the highest wind speed.
        """

        return max(
            weather_list,
            key=lambda weather: weather.wind_speed,
        )
    @staticmethod
    def temperature_spread(
        weather_list: list[CurrentWeather],
    ) -> float:
        """
        Difference between hottest and coolest cities.
        """

        hottest = WeatherAnalytics.hottest_city(weather_list)

        coolest = WeatherAnalytics.coolest_city(weather_list)

        return round(
            hottest.temperature - coolest.temperature,
            2,
        )
    
    @staticmethod
    def generate_summary(
        weather_list: list[CurrentWeather],
    ) -> WeatherSummary:
        """
        Generate a complete weather summary.
        """

        return WeatherSummary(

            average_temperature=(
                WeatherAnalytics.average_temperature(
                    weather_list
                )
            ),

            hottest_city=(
                WeatherAnalytics.hottest_city(
                    weather_list
                )
            ),

            coolest_city=(
                WeatherAnalytics.coolest_city(
                    weather_list
                )
            ),

            highest_wind_city=(
                WeatherAnalytics.highest_wind_city(
                    weather_list
                )
            ),

            temperature_spread=(
                WeatherAnalytics.temperature_spread(
                    weather_list
                )
            ),
        )