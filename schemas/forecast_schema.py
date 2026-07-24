"""
Forecast API response schemas.
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class ForecastDayResponse(BaseModel):
    """
    Represents one forecast day.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    date: str

    condition: str

    max_temperature: float

    min_temperature: float

    rain_probability: int


class ForecastResponse(BaseModel):
    """
    Seven-day forecast.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    city: str

    country: str

    forecast_days: list[
        ForecastDayResponse
    ]