"""
Security policy for Google ADK tool execution.

This module defines the explicit allow-list of tools that the
Weather Intelligence Agent is permitted to execute.

Tool authorization follows a deny-by-default security model.
Any tool that is not explicitly listed here must be rejected.
"""

from __future__ import annotations


ALLOWED_TOOLS: frozenset[str] = frozenset(
    {
        "get_current_weather",
        "get_forecast",
        "analyze_weather",
        "get_weather_intelligence",
        "get_weather_plan",
    }
)