"""
Unit tests for the Google ADK tool guardrail callback.

These tests validate the behavior of the Phase 9.4 pre-execution
security callback without calling Gemini or real weather APIs.
"""

from __future__ import annotations

from dataclasses import dataclass

from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    weather_before_tool_callback,
)


@dataclass
class FakeTool:
    """
    Minimal ADK-compatible tool test double.

    Attributes:
        name:
            Tool identifier exposed to the callback.
    """

    name: str


class FakeToolContext:
    """
    Minimal test double for Google ADK ToolContext.
    """


def test_allowed_current_weather_tool_executes() -> None:
    """
    A valid current-weather request must be allowed.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is None


def test_allowed_forecast_tool_executes() -> None:
    """
    A valid forecast request must be allowed.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_forecast"
        ),
        args={
            "city": "Mumbai",
        },
        tool_context=FakeToolContext(),
    )

    assert result is None


def test_valid_multi_city_analysis_executes() -> None:
    """
    Valid multi-city analytics must be allowed.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="analyze_weather"
        ),
        args={
            "cities": [
                "Delhi",
                "Mumbai",
            ],
        },
        tool_context=FakeToolContext(),
    )

    assert result is None


def test_unknown_tool_is_blocked() -> None:
    """
    Unauthorized tool execution must be blocked.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="execute_shell_command"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_NOT_ALLOWED"


def test_missing_city_is_blocked() -> None:
    """
    Missing required tool arguments must block execution.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={},
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_ARGUMENT_REQUIRED"


def test_empty_city_is_blocked() -> None:
    """
    Empty city arguments must block execution.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["error_code"] == "TOOL_CITY_EMPTY"


def test_unexpected_argument_is_blocked() -> None:
    """
    Unexpected tool arguments must block execution.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
            "command": "delete_database",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_ARGUMENT_UNEXPECTED"


def test_too_many_analysis_cities_are_blocked() -> None:
    """
    Excessive multi-city requests must be blocked.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="analyze_weather"
        ),
        args={
            "cities": [
                f"City-{index}"
                for index in range(11)
            ],
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["error_code"] == "TOOL_TOO_MANY_CITIES"