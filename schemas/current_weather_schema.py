"""
Current Weather API response schema.
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class CurrentWeatherResponse(BaseModel):
    """
    Current weather returned by the REST API.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    city: str

    country: str

    temperature: float

    wind_speed: float

    wind_direction: float

    condition: str

    observation_time: str