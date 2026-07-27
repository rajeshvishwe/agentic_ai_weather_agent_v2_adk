"""
Common location aliases.

This map intentionally contains only abbreviations, alternate spellings,
and a small number of commonly used canonical names.

Normal world-city discovery is handled dynamically through the Open-Meteo
geocoding service. The alias map is therefore not intended to become a
complete list of cities.
"""

CITY_ALIASES = {
    # India
    "blr": "Bangalore",
    "b'lore": "Bangalore",
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",

    "bom": "Mumbai",
    "mumbai": "Mumbai",

    "del": "Delhi",
    "delhi": "Delhi",

    "hyd": "Hyderabad",

    "che": "Chennai",
    "madras": "Chennai",

    "cal": "Kolkata",
    "calcutta": "Kolkata",

    "pune": "Pune",

    # Existing guardrail additions
    "jaipur": "Jaipur",
    "manali": "Manali",

    # USA
    "nyc": "New York",
    "new york city": "New York",

    "la": "Los Angeles",
    "sf": "San Francisco",
    "dc": "Washington",

    # UK
    "ldn": "London",

    # UAE
    "dxb": "Dubai",

    # Japan
    "tokyo": "Tokyo",
}