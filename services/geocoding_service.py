"""
Geocoding service.

This module converts user-entered locations into geographical coordinates
using the Open-Meteo Geocoding API.

It also exposes a lightweight cached city/place validation function used by
the deterministic weather-intent guardrail.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import requests
import truststore

from weather_intelligence_agent_v2.config.city_resolver import (
    resolve_city,
)
from weather_intelligence_agent_v2.config.constants import (
    GEOCODING_API,
    REQUEST_TIMEOUT,
)


# Enable the operating-system certificate store.
# Useful on managed corporate devices and VPN environments.
truststore.inject_into_ssl()


# Guardrail validation should not wait for the complete weather
# service timeout.
LOCATION_VALIDATION_TIMEOUT_SECONDS = min(
    3,
    REQUEST_TIMEOUT,
)


# GeoNames populated-place feature codes returned through
# Open-Meteo begin with PPL.
POPULATED_PLACE_FEATURE_PREFIX = "PPL"


def _normalize_location_name(
    location_name: str,
) -> str:
    """
    Normalize user-entered location before geocoding.

    Examples:

        BLR -> Bangalore
        DEL -> Delhi
        NYC -> New York

    Args:
        location_name:
            User-entered location name or alias.

    Returns:
        Normalized location name.
    """

    if not isinstance(
        location_name,
        str,
    ):
        return ""

    normalized = location_name.strip()

    if not normalized:
        return ""

    return resolve_city(
        normalized
    )


def _search_open_meteo(
    location_name: str,
    *,
    count: int,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    """
    Search Open-Meteo geocoding.

    Args:
        location_name:
            Location query.

        count:
            Maximum results.

        timeout_seconds:
            HTTP timeout.

    Returns:
        List of geocoding results.

    Raises:
        requests.RequestException:
            If the geocoding request fails.
    """

    normalized_location = (
        _normalize_location_name(
            location_name
        )
    )

    if len(normalized_location) < 2:
        return []

    response = requests.get(
        GEOCODING_API,
        params={
            "name": normalized_location,
            "count": count,
            "language": "en",
            "format": "json",
        },
        timeout=timeout_seconds,
    )

    response.raise_for_status()

    payload = response.json()

    results = payload.get(
        "results",
        [],
    )

    if not isinstance(
        results,
        list,
    ):
        return []

    return [
        result
        for result in results
        if isinstance(
            result,
            dict,
        )
    ]


def search_location(
    location_name: str,
) -> dict[str, Any] | None:
    """
    Resolve a location to the best Open-Meteo result.

    Used by the normal weather-service path where full
    geocoding information is required.

    Args:
        location_name:
            City/place name or local alias.

    Returns:
        Best matching location or None.
    """

    results = _search_open_meteo(
        location_name,
        count=1,
        timeout_seconds=REQUEST_TIMEOUT,
    )

    if not results:
        return None

    return results[0]


@lru_cache(
    maxsize=512
)
def _is_valid_city_cached(
    normalized_location_name: str,
) -> bool:
    """
    Cached global populated-place validation.

    Network errors fail closed instead of raising an exception.
    """

    try:

        results = _search_open_meteo(
            normalized_location_name,
            count=5,
            timeout_seconds=(
                LOCATION_VALIDATION_TIMEOUT_SECONDS
            ),
        )

    except (
        requests.RequestException,
        ValueError,
        TypeError,
    ):

        return False

    for result in results:

        feature_code = str(
            result.get(
                "feature_code",
                "",
            )
        ).upper()

        if feature_code.startswith(
            POPULATED_PLACE_FEATURE_PREFIX
        ):

            return True

    return False


def is_valid_city(
    location_name: str,
) -> bool:
    """
    Determine whether a location is a real populated place.

    Hybrid resolution:

    1. Resolve local aliases.
    2. Query Open-Meteo for normal global place names.
    3. Cache validation results.

    Args:
        location_name:
            Candidate location.

    Returns:
        True when the location resolves to a populated place.
    """

    normalized = (
        _normalize_location_name(
            location_name
        )
    )

    if len(normalized) < 2:
        return False

    return _is_valid_city_cached(
        normalized.lower()
    )


def clear_location_validation_cache() -> None:
    """
    Clear cached geocoding validation.

    Primarily useful for tests and development.
    """

    _is_valid_city_cached.cache_clear()


def get_coordinates(
    city: str,
) -> tuple[float, float, str]:
    """
    Convert city/place name into coordinates and country.

    Args:
        city:
            City/place name or alias.

    Returns:
        Tuple containing:

        latitude,
        longitude,
        country

    Raises:
        ValueError:
            If the location cannot be found.

        requests.RequestException:
            If the geocoding service fails.
    """

    resolved_location = (
        search_location(
            city
        )
    )

    normalized_city = (
        _normalize_location_name(
            city
        )
    )

    if resolved_location is None:

        raise ValueError(
            f"City '{normalized_city}' not found."
        )

    return (
        float(
            resolved_location[
                "latitude"
            ]
        ),
        float(
            resolved_location[
                "longitude"
            ]
        ),
        str(
            resolved_location.get(
                "country",
                "Unknown",
            )
        ),
    )