"""
File:
weather_intelligence_agent_v2/models/weather_intelligence_result.py

Phase:
6.9 – Structured Outputs

Purpose:
Structured weather intelligence model.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WeatherIntelligenceResult:
    """
    AI-generated weather intelligence.
    """

    risk_level: str

    recommendations: list[str]