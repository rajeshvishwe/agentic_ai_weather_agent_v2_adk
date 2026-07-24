"""
FastAPI application.

This module configures the Weather Intelligence API and manages
application-scoped resources through the FastAPI lifespan mechanism.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from weather_intelligence_agent_v2.api.routes import (
    router,
)
from weather_intelligence_agent_v2.config.constants import (
    REQUEST_TIMEOUT,
)
from weather_intelligence_agent_v2.core.settings import (
    settings,
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

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env"
)

@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage application-scoped resources.

    Startup:
    - Create shared aiohttp ClientSession.
    - Create AsyncWeatherService.
    - Create AsyncWeatherPlanningService.
    - Create WeatherChatService and ADK runtime.

    Shutdown:
    - Release application references.
    - Close shared aiohttp ClientSession.
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

app.include_router(
    router
)


@app.get(
    "/health",
    tags=["Health"],
)
def health() -> dict[str, str]:
    """
    Return application health information.
    """

    return {
        "status": "UP",
        "application": settings.app_name,
        "version": settings.version,
    }