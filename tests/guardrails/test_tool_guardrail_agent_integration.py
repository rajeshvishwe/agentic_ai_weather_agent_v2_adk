"""
Integration tests for Phase 9.4 ADK tool guardrails.

These tests verify that the Weather Intelligence root agent is configured
with the deterministic before-tool security callback and that the callback
enforces the expected tool authorization behavior.

No Gemini API or external weather API calls are made.
"""

from __future__ import annotations

from dataclasses import dataclass

from weather_intelligence_agent_v2.agent import root_agent
from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    weather_before_tool_callback,
)


@dataclass
class FakeTool:
    """
    Minimal tool test double.

    Attributes:
        name:
            Tool name presented to the ADK callback.
    """

    name: str


class FakeToolContext:
    """
    Minimal ToolContext-compatible test double.
    """


def test_root_agent_has_before_tool_callback() -> None:
    """
    Root agent must expose a before-tool callback.
    """

    assert root_agent.before_tool_callback is not None


def test_root_agent_uses_weather_tool_guardrail_callback() -> None:
    """
    Root agent must use the expected Phase 9.4 callback.
    """

    assert (
        root_agent.before_tool_callback
        is weather_before_tool_callback
    )


def test_current_weather_execution_is_allowed() -> None:
    """
    Valid current-weather tool execution must be allowed.
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


def test_forecast_execution_is_allowed() -> None:
    """
    Valid forecast execution must be allowed.
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


def test_multi_city_analysis_is_allowed() -> None:
    """
    Valid multi-city weather analysis must be allowed.
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


def test_unknown_tool_is_blocked_before_execution() -> None:
    """
    Unknown tools must be rejected before execution.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="delete_database"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_NOT_ALLOWED"


def test_invalid_tool_arguments_are_blocked_before_execution() -> None:
    """
    Invalid arguments must prevent approved tools from executing.
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
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_CITY_EMPTY"


def test_unexpected_tool_arguments_are_blocked() -> None:
    """
    Unexpected parameters must prevent tool execution.
    """

    result = weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
            "command": "unsafe-operation",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_ARGUMENT_UNEXPECTED"