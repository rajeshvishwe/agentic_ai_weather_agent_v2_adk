"""
Reusable dashboard components for weather intelligence presentation.

This module contains Streamlit presentation logic only.

It must not:

- instantiate backend application services
- call Open-Meteo directly
- perform domain analytics
- perform weather intelligence calculations

All business data must arrive through the FastAPI API contract.
"""

from typing import Any

import pandas as pd
import streamlit as st


def _format_value(
    value: Any,
    suffix: str = "",
) -> str:
    """
    Format an API value for dashboard presentation.

    Args:
        value:
            Value returned by the API.

        suffix:
            Optional display suffix.

    Returns:
        Human-readable display value.
    """

    if value is None:
        return "N/A"

    return f"{value}{suffix}"


def render_current_weather(
    current_weather: dict[str, Any],
) -> None:
    """
    Render current weather as dashboard metric cards.

    Args:
        current_weather:
            Current weather section returned by FastAPI.
    """

    st.subheader("🌤️ Current Weather")

    city = current_weather.get(
        "city",
        "Unknown",
    )

    country = current_weather.get(
        "country",
        "",
    )

    if country:
        st.caption(
            f"{city}, {country}"
        )
    else:
        st.caption(city)

    columns = st.columns(4)

    columns[0].metric(
        label="Temperature",
        value=_format_value(
            current_weather.get("temperature"),
            " °C",
        ),
    )

    columns[1].metric(
        label="Condition",
        value=_format_value(
            current_weather.get("condition")
        ),
    )

    columns[2].metric(
        label="Wind Speed",
        value=_format_value(
            current_weather.get("wind_speed"),
            " km/h",
        ),
    )

    columns[3].metric(
        label="Weather Code",
        value=_format_value(
            current_weather.get("weather_code")
        ),
    )


def _build_forecast_dataframe(
    forecast: dict[str, Any],
) -> pd.DataFrame:
    """
    Convert forecast API data into a DataFrame.

    Args:
        forecast:
            Forecast section returned by FastAPI.

    Returns:
        Forecast DataFrame suitable for visualization.
    """

    forecast_days = forecast.get(
        "days",
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


def render_forecast_chart(
    forecast: dict[str, Any],
) -> None:
    """
    Render the seven-day temperature forecast chart.

    Args:
        forecast:
            Forecast section returned by FastAPI.
    """

    st.subheader(
        "📈 7-Day Temperature Forecast"
    )

    dataframe = _build_forecast_dataframe(
        forecast
    )

    if dataframe.empty:
        st.info(
            "Forecast data is not available."
        )
        return

    temperature_columns = [
        column
        for column in (
            "temperature_max",
            "temperature_min",
        )
        if column in dataframe.columns
    ]

    if (
        "date" not in dataframe.columns
        or not temperature_columns
    ):
        st.info(
            "Temperature trend data is not available."
        )
        return

    chart_dataframe = (
        dataframe[
            ["date", *temperature_columns]
        ]
        .dropna(
            subset=["date"]
        )
        .set_index("date")
    )

    chart_dataframe = chart_dataframe.rename(
        columns={
            "temperature_max": "Maximum Temperature",
            "temperature_min": "Minimum Temperature",
        }
    )

    st.line_chart(
        chart_dataframe,
        use_container_width=True,
    )


def render_forecast_table(
    forecast: dict[str, Any],
) -> None:
    """
    Render detailed daily forecast information.

    Args:
        forecast:
            Forecast section returned by FastAPI.
    """

    st.subheader(
        "📅 Daily Forecast"
    )

    dataframe = _build_forecast_dataframe(
        forecast
    )

    if dataframe.empty:
        st.info(
            "Detailed forecast data is not available."
        )
        return

    display_dataframe = dataframe.copy()

    if "date" in display_dataframe.columns:
        display_dataframe["date"] = (
            display_dataframe["date"]
            .dt.strftime("%Y-%m-%d")
        )

    column_labels = {
        "date": "Date",
        "temperature_max": "Max Temp (°C)",
        "temperature_min": "Min Temp (°C)",
        "precipitation": "Precipitation",
        "weather_code": "Weather Code",
        "condition": "Condition",
    }

    display_dataframe = (
        display_dataframe.rename(
            columns=column_labels
        )
    )

    st.dataframe(
        display_dataframe,
        use_container_width=True,
        hide_index=True,
    )


def render_analytics(
    analytics: dict[str, Any],
) -> None:
    """
    Render weather analytics.

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

    average_temperature = (
        analytics.get(
            "average_temperature"
        )
    )

    maximum_temperature = (
        analytics.get(
            "maximum_temperature"
        )
    )

    minimum_temperature = (
        analytics.get(
            "minimum_temperature"
        )
    )

    metrics = st.columns(3)

    metrics[0].metric(
        "Average Temperature",
        _format_value(
            average_temperature,
            " °C",
        ),
    )

    metrics[1].metric(
        "Maximum Temperature",
        _format_value(
            maximum_temperature,
            " °C",
        ),
    )

    metrics[2].metric(
        "Minimum Temperature",
        _format_value(
            minimum_temperature,
            " °C",
        ),
    )

    rainiest_day = analytics.get(
        "rainiest_day"
    )

    if rainiest_day:
        st.markdown(
            "**Rainiest Day**"
        )

        if isinstance(
            rainiest_day,
            dict,
        ):
            rain_date = rainiest_day.get(
                "date",
                "Unknown",
            )

            precipitation = (
                rainiest_day.get(
                    "precipitation",
                    "N/A",
                )
            )

            st.write(
                f"{rain_date} — "
                f"Precipitation: "
                f"{precipitation}"
            )

        else:
            st.write(
                str(rainiest_day)
            )

    temperature_trend = (
        analytics.get(
            "temperature_trend"
        )
    )

    if temperature_trend:
        st.markdown(
            "**Temperature Trend**"
        )

        st.write(
            temperature_trend
        )


def render_intelligence(
    intelligence: dict[str, Any],
) -> None:
    """
    Render AI weather intelligence.

    Args:
        intelligence:
            Intelligence section returned by FastAPI.
    """

    st.subheader(
        "🧠 AI Weather Intelligence"
    )

    if not intelligence:
        st.info(
            "Weather intelligence is not available."
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

    recommendations = (
        intelligence.get(
            "recommendations",
            [],
        )
    )

    st.markdown(
        "**Recommendations**"
    )

    if recommendations:
        for recommendation in recommendations:
            st.markdown(
                f"- {recommendation}"
            )

    else:
        st.info(
            "No weather recommendations available."
        )


def render_weather_dashboard(
    weather_plan: dict[str, Any],
) -> None:
    """
    Render the complete production weather dashboard.

    Args:
        weather_plan:
            Complete weather planning response returned
            by the FastAPI backend.
    """

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

    render_forecast_chart(
        forecast
    )

    st.divider()

    render_forecast_table(
        forecast
    )

    st.divider()

    dashboard_columns = st.columns(2)

    with dashboard_columns[0]:
        render_analytics(
            analytics
        )

    with dashboard_columns[1]:
        render_intelligence(
            intelligence
        )

    st.divider()

    with st.expander(
        "🔍 View Complete API Response"
    ):
        st.json(
            weather_plan
        )