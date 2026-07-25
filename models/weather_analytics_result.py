"""
File:
weather_intelligence_agent_v2/models/weather_analytics_result.py

Phase:
6.9 – Structured Outputs

Purpose:
Structured analytics result model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WeatherAnalyticsResult:
    """
    Structured weather analytics.
    """

    rainiest_day: str