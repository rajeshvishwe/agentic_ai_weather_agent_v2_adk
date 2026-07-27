"""
Incremental Streamlit Weather Dashboard.

This version renders:

1. Current Weather
2. 7-Day Temperature Forecast
3. Daily Forecast table
4. Rain Probability chart
5. Weather Analytics
6. AI Weather Intelligence

The dashboard remains presentation-only and uses data returned by
the existing FastAPI backend.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def render_current_weather(
    current_weather: dict[str, Any],
) -> None:
    """
    Render current weather returned by the FastAPI backend.

    Args:
        current_weather:
            Current weather section from the weather-plan response.
    """

    st.subheader(
        "🌤️ Current Weather"
    )

    if not current_weather:

        st.info(
            "Current weather data is not available."
        )

        return

    city = current_weather.get(
        "city",
        "Unknown",
    )

    country = current_weather.get(
        "country",
        "",
    )

    location = (
        f"{city}, {country}"
        if country
        else city
    )

    st.caption(
        location
    )

    temperature = current_weather.get(
        "temperature"
    )

    condition = current_weather.get(
        "condition",
        "N/A",
    )

    wind_speed = current_weather.get(
        "wind_speed"
    )

    wind_direction = current_weather.get(
        "wind_direction"
    )

    columns = st.columns(
        4
    )

    columns[0].metric(
        "Temperature",
        (
            f"{temperature} °C"
            if temperature is not None
            else "N/A"
        ),
    )

    columns[1].metric(
        "Condition",
        str(condition),
    )

    columns[2].metric(
        "Wind Speed",
        (
            f"{wind_speed} m/s"
            if wind_speed is not None
            else "N/A"
        ),
    )

    columns[3].metric(
        "Wind Direction",
        (
            f"{wind_direction}°"
            if wind_direction is not None
            else "N/A"
        ),
    )

    observation_time = current_weather.get(
        "observation_time"
    )

    if observation_time:

        st.caption(
            f"Observed at: {observation_time}"
        )


def build_forecast_dataframe(
    forecast: dict[str, Any],
) -> pd.DataFrame:
    """
    Convert backend forecast days into a DataFrame.

    Expected backend structure:

    forecast:
        forecast_days:
            - date
            - max_temperature
            - min_temperature
            - condition
            - rain_probability

    Args:
        forecast:
            Forecast section returned by FastAPI.

    Returns:
        Forecast DataFrame.
    """

    forecast_days = forecast.get(
        "forecast_days",
        [],
    )

    if not forecast_days:

        return pd.DataFrame()

    dataframe = pd.DataFrame(
        forecast_days
    )

    if "date" in dataframe.columns:

        dataframe["date"] = pd.to_datetime(
            dataframe["date"],
            errors="coerce",
        )

    return dataframe


def render_temperature_forecast(
    forecast: dict[str, Any],
) -> None:
    """
    Render seven-day maximum/minimum temperature forecast.

    Args:
        forecast:
            Forecast section returned by FastAPI.
    """

    st.subheader(
        "📈 7-Day Temperature Forecast"
    )

    dataframe = build_forecast_dataframe(
        forecast
    )

    if dataframe.empty:

        st.info(
            "7-day forecast data is not available."
        )

        return

    required_columns = {
        "date",
        "max_temperature",
        "min_temperature",
    }

    if not required_columns.issubset(
        dataframe.columns
    ):

        st.info(
            "Temperature forecast data is incomplete."
        )

        return

    chart_dataframe = (
        dataframe[
            [
                "date",
                "max_temperature",
                "min_temperature",
            ]
        ]
        .dropna(
            subset=[
                "date"
            ]
        )
        .set_index(
            "date"
        )
        .rename(
            columns={
                "max_temperature": (
                    "Maximum Temperature"
                ),
                "min_temperature": (
                    "Minimum Temperature"
                ),
            }
        )
    )

    if chart_dataframe.empty:

        st.info(
            "Temperature forecast data is not available."
        )

        return

    st.line_chart(
        chart_dataframe,
        use_container_width=True,
    )


def render_daily_forecast_table(
    forecast: dict[str, Any],
) -> None:
    """
    Render detailed seven-day forecast data as a table.

    Args:
        forecast:
            Forecast section returned by FastAPI.
    """

    st.subheader(
        "📅 Daily Forecast"
    )

    dataframe = build_forecast_dataframe(
        forecast
    )

    if dataframe.empty:

        st.info(
            "Daily forecast data is not available."
        )

        return

    required_columns = [
        "date",
        "condition",
        "max_temperature",
        "min_temperature",
        "rain_probability",
    ]

    available_columns = [
        column
        for column in required_columns
        if column in dataframe.columns
    ]

    if not available_columns:

        st.info(
            "Daily forecast data is incomplete."
        )

        return

    table_dataframe = (
        dataframe[
            available_columns
        ].copy()
    )

    if "date" in table_dataframe.columns:

        table_dataframe["date"] = (
            table_dataframe["date"]
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

    table_dataframe = (
        table_dataframe.rename(
            columns={
                "date": "Date",
                "condition": "Condition",
                "max_temperature": (
                    "Max Temp (°C)"
                ),
                "min_temperature": (
                    "Min Temp (°C)"
                ),
                "rain_probability": (
                    "Rain Probability (%)"
                ),
            }
        )
    )

    st.dataframe(
        table_dataframe,
        use_container_width=True,
        hide_index=True,
    )


def render_rain_probability(
    forecast: dict[str, Any],
) -> None:
    """
    Render seven-day rain probability chart.

    Args:
        forecast:
            Forecast section returned by FastAPI.
    """

    st.subheader(
        "🌧️ Rain Probability"
    )

    dataframe = build_forecast_dataframe(
        forecast
    )

    if dataframe.empty:

        st.info(
            "Rain probability data is not available."
        )

        return

    required_columns = {
        "date",
        "rain_probability",
    }

    if not required_columns.issubset(
        dataframe.columns
    ):

        st.info(
            "Rain probability data is incomplete."
        )

        return

    rain_dataframe = (
        dataframe[
            [
                "date",
                "rain_probability",
            ]
        ]
        .dropna(
            subset=[
                "date"
            ]
        )
        .set_index(
            "date"
        )
        .rename(
            columns={
                "rain_probability": (
                    "Rain Probability (%)"
                ),
            }
        )
    )

    if rain_dataframe.empty:

        st.info(
            "Rain probability data is not available."
        )

        return

    st.bar_chart(
        rain_dataframe,
        use_container_width=True,
    )


def render_weather_analytics(
    analytics: dict[str, Any],
) -> None:
    """
    Render weather analytics returned by the backend.

    Current backend analytics expose the rainiest day.

    Streamlit intentionally does not calculate additional
    analytics locally.

    Args:
        analytics:
            Analytics section returned by FastAPI.
    """

    st.subheader(
        "📊 Weather Analytics"
    )

    if not analytics:

        st.info(
            "Weather analytics are not available."
        )

        return

    rainiest_day = analytics.get(
        "rainiest_day"
    )

    if not isinstance(
        rainiest_day,
        dict,
    ):

        st.info(
            "Rainiest-day analytics are not available."
        )

        return

    date = rainiest_day.get(
        "date",
        "N/A",
    )

    condition = rainiest_day.get(
        "condition",
        "N/A",
    )

    rain_probability = rainiest_day.get(
        "rain_probability"
    )

    max_temperature = rainiest_day.get(
        "max_temperature"
    )

    min_temperature = rainiest_day.get(
        "min_temperature"
    )

    first_row = st.columns(
        3
    )

    first_row[0].metric(
        "Rainiest Date",
        str(date),
    )

    first_row[1].metric(
        "Rain Probability",
        (
            f"{rain_probability}%"
            if rain_probability is not None
            else "N/A"
        ),
    )

    first_row[2].metric(
        "Condition",
        str(condition),
    )

    second_row = st.columns(
        2
    )

    second_row[0].metric(
        "Maximum Temperature",
        (
            f"{max_temperature} °C"
            if max_temperature is not None
            else "N/A"
        ),
    )

    second_row[1].metric(
        "Minimum Temperature",
        (
            f"{min_temperature} °C"
            if min_temperature is not None
            else "N/A"
        ),
    )


def render_ai_weather_intelligence(
    intelligence: dict[str, Any],
) -> None:
    """
    Render backend-generated AI Weather Intelligence.

    Args:
        intelligence:
            Intelligence section returned by FastAPI.
    """

    st.subheader(
        "🧠 AI Weather Intelligence"
    )

    if not intelligence:

        st.info(
            "AI weather intelligence is not available."
        )

        return

    risk_level = intelligence.get(
        "risk_level",
        "Unknown",
    )

    normalized_risk = str(
        risk_level
    ).strip().lower()

    if normalized_risk == "low":

        st.success(
            f"Risk Level: {risk_level}"
        )

    elif normalized_risk in {
        "medium",
        "moderate",
    }:

        st.warning(
            f"Risk Level: {risk_level}"
        )

    elif normalized_risk == "high":

        st.error(
            f"Risk Level: {risk_level}"
        )

    else:

        st.info(
            f"Risk Level: {risk_level}"
        )

    recommendations = intelligence.get(
        "recommendations",
        [],
    )

    if not recommendations:

        st.info(
            "No recommendations are available."
        )

        return

    st.markdown(
        "#### Recommendations"
    )

    for recommendation in recommendations:

        st.markdown(
            f"- {recommendation}"
        )


def render_weather_dashboard(
    weather_plan: dict[str, Any],
) -> None:
    """
    Render the complete structured weather dashboard.

    Enabled sections:

    - Current Weather
    - 7-Day Temperature Forecast
    - Daily Forecast table
    - Rain Probability chart
    - Weather Analytics
    - AI Weather Intelligence

    Args:
        weather_plan:
            Complete weather-plan response returned by FastAPI.
    """

    if not weather_plan:

        st.warning(
            "Weather data is not available."
        )

        return

    current_weather = weather_plan.get(
        "current_weather",
        {},
    )

    forecast = weather_plan.get(
        "forecast",
        {},
    )

    analytics = weather_plan.get(
        "analytics",
        {},
    )

    intelligence = weather_plan.get(
        "intelligence",
        {},
    )

    render_current_weather(
        current_weather
    )

    st.divider()

    render_temperature_forecast(
        forecast
    )

    st.divider()

    render_daily_forecast_table(
        forecast
    )

    st.divider()

    render_rain_probability(
        forecast
    )

    st.divider()

    render_weather_analytics(
        analytics
    )

    st.divider()

    render_ai_weather_intelligence(
        intelligence
    )