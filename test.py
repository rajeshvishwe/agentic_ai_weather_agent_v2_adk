"""
Phase 5.1 Test Script

Tests:
1. Current Weather API
2. 7-Day Forecast API
3. Multi-city Weather
"""
from weather_intelligence_agent_v2.analytics import (
    WeatherAnalytics,
)

from weather_intelligence_agent_v2.analytics.insight_engine import (
    InsightEngine,
)

from weather_intelligence_agent_v2.analytics.weather_intelligence import (
    WeatherIntelligence,
)

from weather_intelligence_agent_v2.analytics import (
    WeatherAnalytics,
    ForecastAnalytics,
)

from weather_intelligence_agent_v2.services import (
    get_current_weather,
    get_7_day_forecast,
    get_weather_multiple,
)


def print_separator(title: str) -> None:
    """Print a formatted section header."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_current_weather() -> None:
    """Test current weather API."""

    print_separator("CURRENT WEATHER")

    weather = get_current_weather("Delhi")

    print(f"City            : {weather.city}")
    print(f"Country         : {weather.country}")
    print(f"Temperature     : {weather.temperature} °C")
    print(f"Wind Speed      : {weather.wind_speed} km/h")
    print(f"Wind Direction  : {weather.wind_direction}°")
    print(f"Condition       : {weather.condition}")
    print(f"Observation Time: {weather.observation_time}")


def test_forecast() -> None:
    """
    Test the 7-day forecast API.
    """

    print_separator("7-DAY FORECAST")

    forecast = get_7_day_forecast("Delhi")

    print(f"City    : {forecast.city}")
    print(f"Country : {forecast.country}")
    print()

    for day in forecast.forecast_days:

        print(
            f"{day.date} | "
            f"{day.condition:<28} | "
            f"Max {day.max_temperature:>5.1f}°C | "
            f"Min {day.min_temperature:>5.1f}°C | "
            f"Rain {day.rain_probability:>3}%"
        )

def test_multi_city() -> None:
    """Test multiple city weather."""

    print_separator("MULTI-CITY WEATHER")

    cities = [
        "Delhi",
        "Mumbai",
        "London",
        "Tokyo",
        "Dubai",
    ]

    weather_list = get_weather_multiple(cities)

    print(
        f"{'City':<12}"
        f"{'Country':<30}"
        f"{'Temp(°C)':<12}"
        f"{'Wind(km/h)':<15}"
        f"{'Condition'}"
    )

    print("-" * 95)

    for weather in weather_list:

        print(
            f"{weather.city:<12}"
            f"{weather.country:<30}"
            f"{weather.temperature:<12.1f}"
            f"{weather.wind_speed:<15.1f}"
            f"{weather.condition}"
        )


def main() -> None:
    """Run all tests."""

    print_separator("WEATHER INTELLIGENCE AGENT V2")

    test_current_weather()

    test_forecast()

    test_multi_city()

    print_separator("ALL TESTS COMPLETED")

def test_weather_analytics() -> None:
    """
    Test the Weather Analytics Engine.
    """

    print_separator("WEATHER ANALYTICS")

    cities = [
        "Delhi",
        "Mumbai",
        "London",
        "Tokyo",
        "Dubai",
    ]

    weather_list = get_weather_multiple(cities)

    summary = WeatherAnalytics.generate_summary(
        weather_list
    )

    print(
        f"Average Temperature : "
        f"{summary.average_temperature:.1f} °C"
    )

    print(
        f"Hottest City        : "
        f"{summary.hottest_city.city} "
        f"({summary.hottest_city.temperature:.1f} °C)"
    )

    print(
        f"Coolest City        : "
        f"{summary.coolest_city.city} "
        f"({summary.coolest_city.temperature:.1f} °C)"
    )

    print(
        f"Highest Wind Speed  : "
        f"{summary.highest_wind_city.city} "
        f"({summary.highest_wind_city.wind_speed:.1f} km/h)"
    )

    print(
        f"Temperature Spread  : "
        f"{summary.temperature_spread:.1f} °C"
    )

def test_forecast_analytics() -> None:
    """
    Test forecast analytics.
    """

    print_separator("FORECAST ANALYTICS")

    forecast = get_7_day_forecast("Delhi")

    rainiest = ForecastAnalytics.rainiest_day(
        forecast
    )

    print(
        f"Highest Rain Probability : "
        f"{ForecastAnalytics.highest_rain_probability(forecast)}%"
    )

    print(
        f"Rainiest Day             : "
        f"{rainiest.date}"
    )

    print(
        f"Condition                : "
        f"{rainiest.condition}"
    )

    print(
        f"Maximum Temperature      : "
        f"{rainiest.max_temperature:.1f} °C"
    )

    print(
        f"Minimum Temperature      : "
        f"{rainiest.min_temperature:.1f} °C"
    )

def test_ai_insights() -> None:

    print_separator("AI WEATHER INSIGHTS")

    cities = [
        "Delhi",
        "Mumbai",
        "London",
        "Tokyo",
        "Dubai",
    ]

    weather = get_weather_multiple(cities)

    forecast = get_7_day_forecast("Delhi")

    rainiest = ForecastAnalytics.rainiest_day(
        forecast,
    )

    insights = InsightEngine.build_summary(
        weather,
        rainiest,
    )

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(f"{index}. {insight}")

def test_weather_intelligence():

    print_separator(
        "ADVANCED WEATHER INTELLIGENCE"
    )

    cities = [
        "Delhi",
        "Mumbai",
        "London",
        "Tokyo",
        "Dubai",
    ]

    weather = get_weather_multiple(cities)

    forecast = get_7_day_forecast(
        "Delhi"
    )

    rainiest = ForecastAnalytics.rainiest_day(
        forecast
    )

    report = WeatherIntelligence.generate_report(
        weather,
        rainiest,
    )

    for line in report:

        print(line)

if __name__ == "__main__":
    main()
    test_current_weather()

    test_forecast()

    test_multi_city()

    test_weather_analytics()

    test_forecast_analytics()

    test_ai_insights()

    test_weather_intelligence()

    print_separator("ALL TESTS COMPLETED")