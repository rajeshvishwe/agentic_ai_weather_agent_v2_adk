"""
Application constants.
"""

# Open-Meteo APIs
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

# HTTP timeout
REQUEST_TIMEOUT = 10

# Weather code mapping
WEATHER_CODES = {
    0: "☀️ Clear Sky",
    1: "🌤 Mainly Clear",
    2: "⛅ Partly Cloudy",
    3: "☁️ Overcast",
    45: "🌫 Fog",
    48: "🌫 Depositing Rime Fog",
    51: "🌦 Light Drizzle",
    53: "🌦 Moderate Drizzle",
    55: "🌧 Heavy Drizzle",
    61: "🌦 Light Rain",
    63: "🌧 Moderate Rain",
    65: "🌧 Heavy Rain",
    71: "❄️ Light Snow",
    73: "❄️ Moderate Snow",
    75: "❄️ Heavy Snow",
    80: "🌦 Rain Showers",
    81: "🌧 Heavy Rain Showers",
    82: "🌧 Violent Rain Showers",
    95: "⛈ Thunderstorm",
    96: "⛈ Thunderstorm with Hail",
    99: "⛈ Severe Thunderstorm"
}

"""
Forecast fields requested from Open-Meteo.
"""

DAILY_FORECAST_FIELDS = [
    "weathercode",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_probability_max",
]