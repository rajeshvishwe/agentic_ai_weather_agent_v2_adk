"""
Weather API routes.
"""

from fastapi import APIRouter
from fastapi import Depends

from weather_intelligence_agent_v2.core.dependencies import (
    get_async_weather_planning_service,
    get_weather_chat_service,
)
from weather_intelligence_agent_v2.schemas.mapper import (
    WeatherPlanningMapper,
)
from weather_intelligence_agent_v2.schemas.weather_chat_schema import (
    WeatherChatRequest,
    WeatherChatResponse,
)
from weather_intelligence_agent_v2.schemas.weather_planning_schema import (
    WeatherPlanningResponse,
)
from weather_intelligence_agent_v2.schemas.weather_request_schema import (
    WeatherPlanningRequest,
)
from weather_intelligence_agent_v2.services.async_weather_planning_service import (
    AsyncWeatherPlanningService,
)
from weather_intelligence_agent_v2.services.weather_chat_service import (
    WeatherChatService,
)


router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


@router.get(
    "/plan/{city}",
    response_model=WeatherPlanningResponse,
)
async def get_weather_plan(
    city: str,
    planning_service: AsyncWeatherPlanningService = Depends(
        get_async_weather_planning_service,
    ),
) -> WeatherPlanningResponse:
    """
    Generate a weather planning report.
    """

    planning = await planning_service.build_weather_plan(
        city
    )

    return WeatherPlanningMapper.to_response(
        planning
    )


@router.post(
    "/plan",
    response_model=WeatherPlanningResponse,
)
async def create_weather_plan(
    request: WeatherPlanningRequest,
    planning_service: AsyncWeatherPlanningService = Depends(
        get_async_weather_planning_service,
    ),
) -> WeatherPlanningResponse:
    """
    Generate a weather planning report from a JSON request.
    """

    planning = await planning_service.build_weather_plan(
        request.city
    )

    return WeatherPlanningMapper.to_response(
        planning
    )


@router.post(
    "/chat",
    response_model=WeatherChatResponse,
)
async def weather_chat(
    request: WeatherChatRequest,
    chat_service: WeatherChatService = Depends(
        get_weather_chat_service,
    ),
) -> WeatherChatResponse:
    """
    Send a conversational request to the weather agent.
    """

    response = await chat_service.chat(
        session_id=request.session_id,
        message=request.message,
    )

    return WeatherChatResponse(
        session_id=request.session_id,
        response=response,
    )