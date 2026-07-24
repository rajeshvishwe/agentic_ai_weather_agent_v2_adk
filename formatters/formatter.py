"""
Formatter Module

Converts weather data into a nicely formatted Markdown response.
"""


def format_current_weather(weather: dict) -> str:
    """
    Format current weather information.

    Args:
        weather: Weather dictionary returned by Weather Service

    Returns:
        Markdown formatted weather report.
    """

    return f"""
# 🌦 Weather Report

📍 **City:** {weather["city"]}, {weather["country"]}

☀️ **Condition:** {weather["condition"]}

🌡 **Temperature:** {weather["temperature"]} °C

💨 **Wind Speed:** {weather["wind_speed"]} km/h

🧭 **Wind Direction:** {weather["wind_direction"]}°

🕒 **Observation Time:** {weather["time"]}
"""

from datetime import datetime


def format_7_day_forecast(data: dict) -> str:
    """
    Format the 7-day weather forecast.

    Args:
        data: Forecast dictionary returned by Weather Service.

    Returns:
        Markdown formatted forecast.
    """

    lines = []

    lines.append("# 🌤 7-Day Weather Forecast\n")

    lines.append(f"📍 **City:** {data['city']}, {data['country']}\n")

    lines.append("---\n")

    for day in data["forecast"]:

        weekday = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).strftime("%A")

        lines.append(f"## 📅 {weekday} ({day['date']})")

        lines.append(f"- ☀️ **Condition:** {day['condition']}")

        lines.append(
            f"- 🌡 **Maximum Temperature:** {day['max_temp']} °C"
        )

        lines.append(
            f"- ❄ **Minimum Temperature:** {day['min_temp']} °C"
        )

        lines.append(
            f"- 🌧 **Rain Probability:** {day['rain_probability']} %"
        )

        lines.append("")

    return "\n".join(lines)

def format_multi_city_weather(weather_list: list[dict]) -> str:
    """
    Format weather information for multiple cities.

    Args:
        weather_list: List of weather dictionaries.

    Returns:
        Markdown formatted report.
    """

    if not weather_list:
        return "No weather information available."

    lines = []

    lines.append("# 🌍 Multi-City Weather Report\n")

    lines.append("| City | Country | Temp | Condition | Wind |")
    lines.append("|------|---------|------|-----------|------|")

    for weather in weather_list:

        lines.append(
            f"| {weather['city']} | "
            f"{weather['country']} | "
            f"{weather['temperature']}°C | "
            f"{weather['condition']} | "
            f"{weather['wind_speed']} km/h |"
        )

    lines.append("\n---\n")

    hottest = max(weather_list, key=lambda x: x["temperature"])
    coolest = min(weather_list, key=lambda x: x["temperature"])
    windiest = max(weather_list, key=lambda x: x["wind_speed"])

    lines.append("## 🔥 Hottest City")
    lines.append(
        f"**{hottest['city']}** ({hottest['temperature']}°C)\n"
    )

    lines.append("## ❄ Coolest City")
    lines.append(
        f"**{coolest['city']}** ({coolest['temperature']}°C)\n"
    )

    lines.append("## 💨 Highest Wind Speed")
    lines.append(
        f"**{windiest['city']}** ({windiest['wind_speed']} km/h)"
    )

    return "\n".join(lines)