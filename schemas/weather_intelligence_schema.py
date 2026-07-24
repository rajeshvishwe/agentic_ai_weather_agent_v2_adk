"""
Weather intelligence API response schema.
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class WeatherIntelligenceResponse(BaseModel):
    """
    API response representation of weather intelligence.

    This schema maps the WeatherIntelligenceResult
    domain model into an API-safe response model.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    risk_level: str

    recommendations: list[str]