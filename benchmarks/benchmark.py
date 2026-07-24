"""
Weather Service Performance Benchmark.

This module compares three weather retrieval strategies:

1. Synchronous sequential execution.
2. Asynchronous sequential execution.
3. Asynchronous concurrent execution.

The benchmark demonstrates the performance characteristics
of asynchronous I/O for external API communication.

This module is intended for development and performance
analysis. It is not part of the runtime application path.
"""

import asyncio
import time
from dataclasses import dataclass

from weather_intelligence_agent_v2.models import (
    CurrentWeather,
)
from weather_intelligence_agent_v2.services.async_weather_service import (
    AsyncWeatherService,
)
from weather_intelligence_agent_v2.services.weather_service import (
    get_weather_multiple,
)


@dataclass(
    slots=True,
    frozen=True,
)
class BenchmarkResult:
    """
    Represents the result of one benchmark strategy.
    """

    name: str

    execution_time: float

    cities_processed: int

    requests_per_second: float


CITIES = [
    "Delhi",
    "Mumbai",
    "London",
    "Tokyo",
    "Dubai",
    "Singapore",
    "Sydney",
    "Paris",
    "Berlin",
    "New York",
]


def print_weather_results(
    results: list[CurrentWeather],
) -> None:
    """
    Print weather results.

    Args:
        results:
            CurrentWeather domain models.
    """

    for weather in results:
        print(
            f"{weather.city:12} "
            f"{weather.temperature:6.1f} °C "
            f"{weather.condition}"
        )


def create_benchmark_result(
    name: str,
    start_time: float,
    end_time: float,
    cities_processed: int,
) -> BenchmarkResult:
    """
    Create a benchmark result.

    Args:
        name:
            Benchmark strategy name.

        start_time:
            perf_counter start value.

        end_time:
            perf_counter end value.

        cities_processed:
            Number of cities processed.

    Returns:
        BenchmarkResult instance.
    """

    execution_time = (
        end_time - start_time
    )

    requests_per_second = (
        cities_processed
        / execution_time
        if execution_time > 0
        else 0.0
    )

    return BenchmarkResult(
        name=name,
        execution_time=execution_time,
        cities_processed=cities_processed,
        requests_per_second=requests_per_second,
    )


def benchmark_sync(
    cities: list[str],
) -> tuple[
    BenchmarkResult,
    list[CurrentWeather],
]:
    """
    Benchmark synchronous sequential retrieval.

    Args:
        cities:
            Cities to retrieve.

    Returns:
        Benchmark result and weather data.
    """

    start_time = time.perf_counter()

    results = get_weather_multiple(
        cities
    )

    end_time = time.perf_counter()

    benchmark_result = (
        create_benchmark_result(
            name="Synchronous Sequential",
            start_time=start_time,
            end_time=end_time,
            cities_processed=len(
                results
            ),
        )
    )

    return (
        benchmark_result,
        results,
    )


async def benchmark_async_sequential(
    cities: list[str],
) -> tuple[
    BenchmarkResult,
    list[CurrentWeather],
]:
    """
    Benchmark asynchronous sequential retrieval.

    Each asynchronous operation is awaited before
    starting the next city.

    Args:
        cities:
            Cities to retrieve.

    Returns:
        Benchmark result and weather data.
    """

    results: list[
        CurrentWeather
    ] = []

    start_time = time.perf_counter()

    async with AsyncWeatherService() as service:

        for city in cities:

            weather = (
                await service.get_current_weather(
                    city
                )
            )

            results.append(
                weather
            )

    end_time = time.perf_counter()

    benchmark_result = (
        create_benchmark_result(
            name="Asynchronous Sequential",
            start_time=start_time,
            end_time=end_time,
            cities_processed=len(
                results
            ),
        )
    )

    return (
        benchmark_result,
        results,
    )


async def benchmark_async_concurrent(
    cities: list[str],
) -> tuple[
    BenchmarkResult,
    list[CurrentWeather],
]:
    """
    Benchmark asynchronous concurrent retrieval.

    Independent city requests are executed concurrently
    using AsyncWeatherService.get_weather_multiple().

    Args:
        cities:
            Cities to retrieve.

    Returns:
        Benchmark result and weather data.
    """

    start_time = time.perf_counter()

    async with AsyncWeatherService(
        max_concurrency=10
    ) as service:

        results = (
            await service.get_weather_multiple(
                cities
            )
        )

    end_time = time.perf_counter()

    benchmark_result = (
        create_benchmark_result(
            name="Asynchronous Concurrent",
            start_time=start_time,
            end_time=end_time,
            cities_processed=len(
                results
            ),
        )
    )

    return (
        benchmark_result,
        results,
    )


def print_benchmark_result(
    result: BenchmarkResult,
) -> None:
    """
    Print one benchmark result.

    Args:
        result:
            BenchmarkResult instance.
    """

    print(
        f"{result.name:<28}"
        f"{result.execution_time:>10.2f} s"
        f"{result.requests_per_second:>12.2f} req/s"
    )


async def benchmark() -> None:
    """
    Execute the complete benchmark suite.
    """

    print(
        "\n"
        "=========================================="
    )

    print(
        "Weather Intelligence Performance Benchmark"
    )

    print(
        "=========================================="
    )

    print(
        f"\nCities Tested: {len(CITIES)}"
    )

    print(
        "\nRunning synchronous benchmark..."
    )

    (
        sync_result,
        sync_weather,
    ) = benchmark_sync(
        CITIES
    )

    print(
        "Running async sequential benchmark..."
    )

    (
        async_sequential_result,
        async_sequential_weather,
    ) = await benchmark_async_sequential(
        CITIES
    )

    print(
        "Running async concurrent benchmark..."
    )

    (
        async_concurrent_result,
        async_concurrent_weather,
    ) = await benchmark_async_concurrent(
        CITIES
    )

    print(
        "\n"
        "Weather Retrieved"
    )

    print(
        "------------------------------------------"
    )

    print_weather_results(
        async_concurrent_weather
    )

    print(
        "\n"
        "Performance Results"
    )

    print(
        "------------------------------------------"
    )

    print(
        f"{'Strategy':<28}"
        f"{'Time':>10}"
        f"{'Throughput':>12}"
    )

    print(
        "------------------------------------------"
        "------------"
    )

    print_benchmark_result(
        sync_result
    )

    print_benchmark_result(
        async_sequential_result
    )

    print_benchmark_result(
        async_concurrent_result
    )

    if (
        async_concurrent_result.execution_time
        > 0
    ):
        sync_speedup = (
            sync_result.execution_time
            / async_concurrent_result.execution_time
        )

        sequential_speedup = (
            async_sequential_result.execution_time
            / async_concurrent_result.execution_time
        )

        print(
            "\n"
            "Speedup"
        )

        print(
            "------------------------------------------"
        )

        print(
            "Concurrent vs Sync       : "
            f"{sync_speedup:.2f}x"
        )

        print(
            "Concurrent vs Async Seq. : "
            f"{sequential_speedup:.2f}x"
        )

    print(
        "\n"
        "Validation"
    )

    print(
        "------------------------------------------"
    )

    print(
        "Sync results             : "
        f"{len(sync_weather)}"
    )

    print(
        "Async sequential results : "
        f"{len(async_sequential_weather)}"
    )

    print(
        "Async concurrent results : "
        f"{len(async_concurrent_weather)}"
    )

    print(
        "\nBenchmark completed successfully."
    )


if __name__ == "__main__":
    asyncio.run(
        benchmark()
    )