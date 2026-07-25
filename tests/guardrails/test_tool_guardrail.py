"""
Unit tests for the Phase 9.4 ToolGuardrail orchestrator.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.tool_guardrail import (
    ToolGuardrail,
)


def test_valid_current_weather_request_passes() -> None:
    """Authorized tool with valid arguments must pass."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_current_weather",
        arguments={
            "city": "Delhi",
        },
    )

    assert result.is_valid is True


def test_valid_forecast_request_passes() -> None:
    """Authorized forecast request must pass."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_forecast",
        arguments={
            "city": "Mumbai",
        },
    )

    assert result.is_valid is True


def test_unknown_tool_is_blocked() -> None:
    """Unauthorized tools must fail before execution."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="execute_shell_command",
        arguments={
            "city": "Delhi",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_NOT_ALLOWED"


def test_missing_city_is_blocked() -> None:
    """Approved tools still require valid arguments."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_current_weather",
        arguments={},
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_REQUIRED"


def test_empty_city_is_blocked() -> None:
    """Empty city argument must be rejected."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_current_weather",
        arguments={
            "city": "",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_EMPTY"


def test_invalid_city_type_is_blocked() -> None:
    """Non-text city arguments must be rejected."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_current_weather",
        arguments={
            "city": 123,
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_INVALID_TYPE"


def test_unexpected_argument_is_blocked() -> None:
    """Unexpected tool parameters must be rejected."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_current_weather",
        arguments={
            "city": "Delhi",
            "command": "rm -rf /",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_UNEXPECTED"


def test_weather_plan_request_passes() -> None:
    """Weather planning request with valid arguments must pass."""

    guardrail = ToolGuardrail()

    result = guardrail.validate(
        tool_name="get_weather_plan",
        arguments={
            "city": "Tokyo",
        },
    )

    assert result.is_valid is True