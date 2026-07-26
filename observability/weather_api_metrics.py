"""
Prometheus metrics for external weather API calls.

This module exposes low-cardinality metrics for:

- weather API request count
- weather API request latency
- weather API failures

Only stable logical endpoint names are used as labels.
Raw URLs, cities, coordinates, query parameters, and user data are
deliberately excluded.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram


WEATHER_API_REQUESTS_TOTAL = Counter(
    "weather_agent_weather_api_requests_total",
    "Total requests made to external weather APIs.",
    labelnames=(
        "endpoint",
    ),
)


WEATHER_API_FAILURES_TOTAL = Counter(
    "weather_agent_weather_api_failures_total",
    "Total failed requests to external weather APIs.",
    labelnames=(
        "endpoint",
    ),
)


WEATHER_API_DURATION_SECONDS = Histogram(
    "weather_agent_weather_api_duration_seconds",
    "External weather API request duration in seconds.",
    labelnames=(
        "endpoint",
    ),
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        20.0,
    ),
)