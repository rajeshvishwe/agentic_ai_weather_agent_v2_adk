"""
Weather API request schemas.
"""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class WeatherPlanningRequest(BaseModel):
    """
    Request body for weather planning.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name"
    )