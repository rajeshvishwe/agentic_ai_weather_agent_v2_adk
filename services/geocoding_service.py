"""
Geocoding Service

Converts a city name into latitude and longitude.
"""

import requests
import truststore

from weather_intelligence_agent_v2.config.constants import (
    GEOCODING_API,
    REQUEST_TIMEOUT,
)
from ..config.city_resolver import resolve_city

# Enable Windows certificate store (helps on corporate VPNs)
truststore.inject_into_ssl()


def get_coordinates(city: str) -> tuple[float, float, str]:
    """
    Convert a city name into latitude, longitude and country.

    Args:
        city: City name

    Returns:
        (latitude, longitude, country)

    Raises:
        ValueError if the city is not found.
    """

    # Resolve aliases before calling the API
    city = resolve_city(city)

    response = requests.get(
        GEOCODING_API,
        params={
            "name": city,
            "count": 1,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data:
        raise ValueError(f"City '{city}' not found.")

    location = data["results"][0]

    return (
        location["latitude"],
        location["longitude"],
        location.get("country", "Unknown"),
    )