"""
Weather Service

This module is responsible for communicating with the Open-Meteo Weather API.

Responsibilities:
- Fetch current weather
- Fetch 7-day weather forecast
- Fetch weather for multiple cities

Business logic and analytics should NOT be implemented here.
"""

from typing import Any

import requests
import truststore

from weather_intelligence_agent_v2.config.constants import (
    DAILY_FORECAST_FIELDS,
    REQUEST_TIMEOUT,
    WEATHER_API,
    WEATHER_CODES,
)

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
    ForecastDay,
)

from weather_intelligence_agent_v2.services.geocoding_service import (
    get_coordinates,
)

# Use Windows trusted certificates
truststore.inject_into_ssl()


def get_current_weather(city: str) -> CurrentWeather:
    """
    Retrieve the current weather for a city.

    Args:
        city: Name of the city.

    Returns:
        CurrentWeather domain model.
    """

    latitude, longitude, country = get_coordinates(city)

    response = requests.get(
        WEATHER_API,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data: dict[str, Any] = response.json()

    weather = data["current_weather"]

    return CurrentWeather(
        city=city,
        country=country,
        temperature=weather["temperature"],
        wind_speed=weather["windspeed"],
        wind_direction=weather["winddirection"],
        condition=WEATHER_CODES.get(
            weather["weathercode"],
            "Unknown",
        ),
        observation_time=weather["time"].replace("T", " "),
    )


def get_7_day_forecast(city: str) -> Forecast:
    """
    Retrieve the seven-day weather forecast.

    Args:
        city: Name of the city.

    Returns:
        Forecast domain model.
    """

    latitude, longitude, country = get_coordinates(city)

    response = requests.get(
        WEATHER_API,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                DAILY_FORECAST_FIELDS
            ),
            "forecast_days": 7,
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data: dict[str, Any] = response.json()

    daily = data["daily"]

    forecast_days: list[ForecastDay] = []

    for index in range(len(daily["time"])):

        forecast_days.append(

            ForecastDay(

                date=daily["time"][index],

                condition=WEATHER_CODES.get(
                    daily["weathercode"][index],
                    "Unknown",
                ),

                max_temperature=daily[
                    "temperature_2m_max"
                ][index],

                min_temperature=daily[
                    "temperature_2m_min"
                ][index],

                rain_probability=daily[
                    "precipitation_probability_max"
                ][index],

            )

        )

    return Forecast(
        city=city,
        country=country,
        forecast_days=forecast_days,
    )


def get_weather_multiple(
    cities: list[str],
) -> list[CurrentWeather]:
    """
    Retrieve current weather for multiple cities.

    Args:
        cities: List of city names.

    Returns:
        List of CurrentWeather objects.
    """

    return [
        get_current_weather(city)
        for city in cities
    ]