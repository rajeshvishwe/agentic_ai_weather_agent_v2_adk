"""
API schemas for conversational weather intelligence.
"""

from pydantic import BaseModel
from pydantic import Field


class WeatherChatRequest(BaseModel):
    """
    Request sent to the conversational weather agent.
    """

    session_id: str = Field(
        min_length=1,
        description="Unique conversation session identifier.",
    )

    message: str = Field(
        min_length=1,
        description="User message sent to the weather agent.",
    )


class WeatherChatResponse(BaseModel):
    """
    Response returned by the conversational weather agent.
    """

    session_id: str

    response: str