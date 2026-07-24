"""
Phase 7.4 Async Architecture Integration Tests.

This module validates the asynchronous weather architecture.

Tests:
1. Current weather retrieval.
2. Seven-day forecast retrieval.
3. Concurrent multi-city weather retrieval.
4. Async weather planning orchestration.

These tests make real calls to the external Open-Meteo APIs
and are intended as integration tests.
"""

import asyncio

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
    Forecast,
)
from weather_intelligence_agent_v2.models.weather_planning import (
    WeatherPlanning,
)
from weather_intelligence_agent_v2.services.async_weather_planning_service import (
    AsyncWeatherPlanningService,
)
from weather_intelligence_agent_v2.services.async_weather_service import (
    AsyncWeatherService,
)


TEST_CITY = "Delhi"

TEST_CITIES = [
    "Delhi",
    "Mumbai",
    "London",
    "Tokyo",
]


async def test_current_weather(
    service: AsyncWeatherService,
) -> None:
    """
    Test asynchronous current weather retrieval.

    Args:
        service:
            Async weather service instance.
    """

    print(
        "\n"
        "=========================================="
    )
    print(
        "TEST 1: Async Current Weather"
    )
    print(
        "=========================================="
    )

    weather = await service.get_current_weather(
        TEST_CITY
    )

    assert isinstance(
        weather,
        CurrentWeather,
    )

    assert weather.city == TEST_CITY

    print(
        f"City              : {weather.city}"
    )
    print(
        f"Country           : {weather.country}"
    )
    print(
        f"Temperature       : {weather.temperature} °C"
    )
    print(
        f"Condition         : {weather.condition}"
    )
    print(
        f"Wind Speed        : {weather.wind_speed} km/h"
    )
    print(
        f"Wind Direction    : {weather.wind_direction}°"
    )
    print(
        f"Observation Time  : {weather.observation_time}"
    )

    print(
        "\nTEST 1 PASSED"
    )


async def test_forecast(
    service: AsyncWeatherService,
) -> None:
    """
    Test asynchronous seven-day forecast retrieval.

    Args:
        service:
            Async weather service instance.
    """

    print(
        "\n"
        "=========================================="
    )
    print(
        "TEST 2: Async 7-Day Forecast"
    )
    print(
        "=========================================="
    )

    forecast = await service.get_7_day_forecast(
        TEST_CITY
    )

    assert isinstance(
        forecast,
        Forecast,
    )

    assert forecast.city == TEST_CITY

    assert len(
        forecast.forecast_days
    ) == 7

    print(
        f"City    : {forecast.city}"
    )
    print(
        f"Country : {forecast.country}"
    )

    print(
        "\n7-Day Forecast:"
    )

    for day in forecast.forecast_days:

        print(
            f"{day.date} | "
            f"{day.condition} | "
            f"Min: {day.min_temperature} °C | "
            f"Max: {day.max_temperature} °C | "
            f"Rain: {day.rain_probability}%"
        )

    print(
        "\nTEST 2 PASSED"
    )


async def test_multi_city_weather(
    service: AsyncWeatherService,
) -> None:
    """
    Test concurrent multi-city weather retrieval.

    Args:
        service:
            Async weather service instance.
    """

    print(
        "\n"
        "=========================================="
    )
    print(
        "TEST 3: Concurrent Multi-City Weather"
    )
    print(
        "=========================================="
    )

    results = await service.get_weather_multiple(
        TEST_CITIES
    )

    assert len(results) == len(
        TEST_CITIES
    )

    assert all(
        isinstance(
            weather,
            CurrentWeather,
        )
        for weather in results
    )

    print(
        f"\nCities Requested : {len(TEST_CITIES)}"
    )

    print(
        f"Cities Returned  : {len(results)}"
    )

    print(
        "\nWeather Results:"
    )

    for weather in results:

        print(
            f"{weather.city:12} | "
            f"{weather.temperature:6.1f} °C | "
            f"{weather.condition}"
        )

    returned_cities = [
        weather.city
        for weather in results
    ]

    assert returned_cities == TEST_CITIES

    print(
        "\nResult order validated."
    )

    print(
        "All results are CurrentWeather domain models."
    )

    print(
        "\nTEST 3 PASSED"
    )


async def test_async_weather_planning(
    service: AsyncWeatherService,
) -> None:
    """
    Test asynchronous weather planning orchestration.

    Args:
        service:
            Async weather service instance.
    """

    print(
        "\n"
        "=========================================="
    )
    print(
        "TEST 4: Async Weather Planning"
    )
    print(
        "=========================================="
    )

    planning_service = (
        AsyncWeatherPlanningService(
            weather_service=service
        )
    )

    plan = (
        await planning_service.build_weather_plan(
            TEST_CITY
        )
    )

    assert isinstance(
        plan,
        WeatherPlanning,
    )

    assert plan.city == TEST_CITY

    assert isinstance(
        plan.current_weather,
        CurrentWeather,
    )

    assert isinstance(
        plan.forecast,
        Forecast,
    )

    print(
        f"City       : {plan.city}"
    )

    print(
        "Temperature: "
        f"{plan.current_weather.temperature} °C"
    )

    print(
        "Condition  : "
        f"{plan.current_weather.condition}"
    )

    print(
        "Forecast Days: "
        f"{len(plan.forecast.forecast_days)}"
    )

    print(
        "\nAnalytics:"
    )

    print(
        plan.analytics
    )

    print(
        "\nIntelligence:"
    )

    print(
        plan.intelligence
    )

    print(
        "\nTEST 4 PASSED"
    )


async def run_tests() -> None:
    """
    Execute all Phase 7.4 async integration tests.
    """

    print(
        "\n"
        "=========================================="
    )

    print(
        "PHASE 7.4 ASYNC INTEGRATION TESTS"
    )

    print(
        "=========================================="
    )

    async with AsyncWeatherService(
        max_concurrency=5
    ) as service:

        await test_current_weather(
            service
        )

        await test_forecast(
            service
        )

        await test_multi_city_weather(
            service
        )

        await test_async_weather_planning(
            service
        )

    print(
        "\n"
        "=========================================="
    )

    print(
        "ALL PHASE 7.4 TESTS PASSED"
    )

    print(
        "=========================================="
    )


if __name__ == "__main__":

    asyncio.run(
        run_tests()
    )