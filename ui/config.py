"""
Configuration for the Streamlit user interface.
"""

import os
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UISettings:
    """
    Configuration used by the Streamlit frontend.

    Attributes:
        api_base_url:
            Base URL of the Weather Intelligence FastAPI backend.

        request_timeout_seconds:
            Maximum time the UI waits for an API response.
    """

    api_base_url: str = os.getenv(
        "WEATHER_API_BASE_URL",
        "http://127.0.0.1:8000",
    )

    request_timeout_seconds: float = float(
        os.getenv(
            "WEATHER_API_TIMEOUT_SECONDS",
            "30",
        )
    )


ui_settings = UISettings()