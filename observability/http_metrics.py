"""
Prometheus HTTP metrics for the Weather Intelligence Agent.

This module provides FastAPI middleware instrumentation for:

- HTTP request count
- HTTP request latency
- HTTP server errors

Low-value infrastructure endpoints such as health checks and Prometheus
scraping are intentionally excluded to avoid polluting application metrics.

Metrics use bounded labels only:

- HTTP method
- FastAPI route template
- HTTP status code

Raw URLs, query parameters, session identifiers, prompts, and other
high-cardinality values are never used as metric labels.
"""

from __future__ import annotations

from time import perf_counter
from typing import Awaitable, Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "weather_agent_http_requests_total",
    "Total HTTP requests received by the Weather Intelligence Agent.",
    labelnames=(
        "method",
        "route",
        "status_code",
    ),
)

HTTP_ERRORS_TOTAL = Counter(
    "weather_agent_http_errors_total",
    "Total HTTP server errors returned by the Weather Intelligence Agent.",
    labelnames=(
        "method",
        "route",
        "status_code",
    ),
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "weather_agent_http_request_duration_seconds",
    "HTTP request duration for the Weather Intelligence Agent.",
    labelnames=(
        "method",
        "route",
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
        30.0,
        60.0,
    ),
)


EXCLUDED_PATHS = {
    "/health",
    "/metrics",
    "/metrics/",
}


def _get_route_template(
    request: Request,
) -> str:
    """
    Return the FastAPI route template for a request.

    Route templates are preferred over raw request paths because they avoid
    high-cardinality labels.

    For example:

        /approvals/123
        /approvals/456

    are both represented as:

        /approvals/{request_id}

    Args:
        request:
            Incoming FastAPI request.

    Returns:
        str:
            Route template or a safe fallback value.
    """

    route = request.scope.get(
        "route"
    )

    route_path = getattr(
        route,
        "path",
        None,
    )

    if isinstance(
        route_path,
        str,
    ):
        return route_path

    return "unmatched"


async def http_metrics_middleware(
    request: Request,
    call_next: Callable[
        [Request],
        Awaitable[Response],
    ],
) -> Response:
    """
    Record Prometheus HTTP metrics for a FastAPI request.

    Health and metrics endpoints are excluded because Kubernetes probes and
    Prometheus scraping would otherwise dominate the request statistics.

    Args:
        request:
            Incoming FastAPI request.

        call_next:
            Function used to invoke the next ASGI/FastAPI handler.

    Returns:
        Response:
            Application response.

    Raises:
        Exception:
            Re-raises any unhandled application exception after recording
            error and latency metrics.
    """

    if request.url.path in EXCLUDED_PATHS:
        return await call_next(
            request
        )

    start_time = perf_counter()

    method = request.method
    status_code = "500"

    try:
        response = await call_next(
            request
        )

        status_code = str(
            response.status_code
        )

        route = _get_route_template(
            request
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).inc()

        if response.status_code >= 500:
            HTTP_ERRORS_TOTAL.labels(
                method=method,
                route=route,
                status_code=status_code,
            ).inc()

        return response

    except Exception:
        route = _get_route_template(
            request
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).inc()

        HTTP_ERRORS_TOTAL.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).inc()

        raise

    finally:
        route = _get_route_template(
            request
        )

        duration = (
            perf_counter()
            - start_time
        )

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            route=route,
        ).observe(
            duration
        )