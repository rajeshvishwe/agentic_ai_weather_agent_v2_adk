"""
FastAPI application.

This module configures the Weather Intelligence API and manages
application-scoped resources through the FastAPI lifespan mechanism.

The application exposes:

- weather intelligence APIs
- conversational weather APIs
- Human-in-the-Loop approval APIs
- Prometheus metrics
- OpenTelemetry HTTP tracing
- Prometheus HTTP request metrics
- health endpoint
"""

from __future__ import annotations

import truststore

truststore.inject_into_ssl()

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI
from opentelemetry.instrumentation.aiohttp_client import (
    AioHttpClientInstrumentor,
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)
from prometheus_client import make_asgi_app

from weather_intelligence_agent_v2.api.approval_routes import (
    router as approval_router,
)
from weather_intelligence_agent_v2.api.routes import (
    router as weather_router,
)
from weather_intelligence_agent_v2.config.constants import (
    REQUEST_TIMEOUT,
)
from weather_intelligence_agent_v2.core.settings import (
    settings,
)
from weather_intelligence_agent_v2.observability.http_metrics import (
    http_metrics_middleware,
)
from weather_intelligence_agent_v2.observability.logging import (
    configure_log_correlation,
)
from weather_intelligence_agent_v2.observability.tracing import (
    configure_tracing,
)
from weather_intelligence_agent_v2.services.async_weather_planning_service import (
    AsyncWeatherPlanningService,
)
from weather_intelligence_agent_v2.services.async_weather_service import (
    AsyncWeatherService,
)
from weather_intelligence_agent_v2.services.weather_chat_service import (
    WeatherChatService,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env"
)


# ------------------------------------------------------------
# OpenTelemetry bootstrap
# ------------------------------------------------------------

configure_tracing()

configure_log_correlation()

AioHttpClientInstrumentor().instrument()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage application-scoped resources.

    Startup responsibilities:

    - Create shared aiohttp ClientSession.
    - Create AsyncWeatherService.
    - Create AsyncWeatherPlanningService.
    - Create WeatherChatService and Google ADK runtime.

    Shutdown responsibilities:

    - Release application references.
    - Close the shared aiohttp ClientSession.

    Args:
        app:
            FastAPI application instance.

    Yields:
        None:
            Control to FastAPI while application resources are active.
    """

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        weather_service = AsyncWeatherService(
            session=session,
        )

        planning_service = (
            AsyncWeatherPlanningService(
                weather_service=weather_service,
            )
        )

        chat_service = WeatherChatService()

        app.state.async_weather_service = (
            weather_service
        )

        app.state.async_weather_planning_service = (
            planning_service
        )

        app.state.weather_chat_service = (
            chat_service
        )

        yield

    app.state.async_weather_service = None
    app.state.async_weather_planning_service = None
    app.state.weather_chat_service = None


app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)


# ------------------------------------------------------------
# Phase 11.16 — Prometheus HTTP Metrics
# ------------------------------------------------------------

app.middleware(
    "http"
)(
    http_metrics_middleware
)


# ------------------------------------------------------------
# Weather Intelligence API
# ------------------------------------------------------------

app.include_router(
    weather_router
)


# ------------------------------------------------------------
# Phase 9.5 — HITL Approval API
# ------------------------------------------------------------

app.include_router(
    approval_router
)


# ------------------------------------------------------------
# Phase 11.3 — Prometheus Metrics
# ------------------------------------------------------------

metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)


@app.get(
    "/health",
    tags=["Health"],
)
def health() -> dict[str, str]:
    """
    Return application health information.

    Returns:
        dict[str, str]:
            Application health metadata.
    """

    return {
        "status": "UP",
        "application": settings.app_name,
        "version": settings.version,
    }


# ------------------------------------------------------------
# Phase 11.10 — FastAPI OpenTelemetry Tracing
# ------------------------------------------------------------

FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls="health,metrics",
)