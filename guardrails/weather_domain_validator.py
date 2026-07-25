"""
Deterministic weather-domain validation.
"""

from __future__ import annotations

import re

WEATHER_KEYWORDS = {
    "weather",
    "temperature",
    "forecast",
    "rain",
    "snow",
    "wind",
    "humidity",
    "storm",
    "sunny",
    "cloud",
    "climate",
    "heat",
    "cold",
    "uv",
    "visibility",
    "today",
    "tomorrow",
}


class WeatherDomainValidator:
    """
    Detect whether a query belongs to the weather domain.
    """

    _TOKEN_PATTERN = re.compile(r"[a-zA-Z]+")

    def is_weather_query(
        self,
        text: str,
    ) -> bool:

        tokens = {
            token.lower()
            for token in self._TOKEN_PATTERN.findall(text)
        }

        return bool(tokens & WEATHER_KEYWORDS)