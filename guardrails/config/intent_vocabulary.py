"""
Weather domain vocabulary.

This module contains configurable vocabularies used by the
WeatherIntentValidator.

Keeping vocabularies outside the validator allows the weather
planning domain to evolve without mixing vocabulary maintenance
with validation logic.
"""

from __future__ import annotations


# ------------------------------------------------------------------
# Core weather terminology
# ------------------------------------------------------------------

WEATHER_TERMS = {
    "weather",
    "forecast",
    "temperature",
    "humidity",
    "wind",
    "rain",
    "snow",
    "storm",
    "drizzle",
    "thunder",
    "lightning",
    "fog",
    "mist",
    "cloud",
    "cloudy",
    "clear",
    "sun",
    "sunny",
    "uv",
    "visibility",
    "pressure",
    "dew point",
    "air quality",
    "air pollution",
    "climate",
    "hot",
    "cold",
    "warm",
    "cool",
    "freezing",
    "outside",
    "feels like",
}


# ------------------------------------------------------------------
# Weather-dependent activities
# ------------------------------------------------------------------

WEATHER_ACTIONS = {
    "umbrella",
    "jacket",
    "coat",
    "raincoat",

    "trek",
    "trekking",

    "hike",
    "hiking",

    "camp",
    "camping",

    "travel",
    "trip",

    "drive",
    "driving",

    "cycle",
    "cycling",
    "bike",

    "walking",
    "walk",

    "run",
    "running",

    "picnic",
    "beach",

    "fishing",
    "swimming",
    "surfing",

    "flight",
    "fly",

    "safe",
    "outside",
}


# ------------------------------------------------------------------
# Time expressions
# ------------------------------------------------------------------

TIME_TERMS = {
    "today",
    "tomorrow",
    "tonight",

    "this morning",
    "this afternoon",
    "this evening",

    "this weekend",
    "weekend",

    "next week",
    "upcoming week",
    "coming week",
    "next 7 days",

    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


# ------------------------------------------------------------------
# Weather / planning / comparison question patterns
# ------------------------------------------------------------------

QUESTION_PATTERNS = {
    # Standard questions
    "will it",
    "is it",
    "how is",
    "how's",
    "can i",
    "should i",
    "do i need",
    "what is",
    "what's",

    # Day-selection planning
    "which day",
    "what day",
    "best day",

    # Weather comparison intent
    "compare",
    "comparison",
    "which is better",
    "which one is better",
}