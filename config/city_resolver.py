"""
Resolve user-entered city names.
"""

from weather_intelligence_agent_v2.config.city_aliases import CITY_ALIASES

def resolve_city(city: str) -> str:
    """
    Convert aliases into standard city names.
    """

    normalized = city.strip().lower()

    return CITY_ALIASES.get(normalized, city.title())