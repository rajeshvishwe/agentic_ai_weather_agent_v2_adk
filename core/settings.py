"""
Application settings.

Central location for application configuration.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Settings:
    """
    Application configuration.
    """

    app_name: str = "Weather Intelligence Agent"

    version: str = "1.0.0"

    description: str = (
        "Production AI Weather Intelligence Platform"
    )


settings = Settings()