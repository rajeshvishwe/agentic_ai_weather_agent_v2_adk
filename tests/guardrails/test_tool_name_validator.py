"""
Unit tests for the Phase 9.4 tool-name security validator.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.validators.tool_name_validator import (
    ToolNameValidator,
)


def test_current_weather_tool_is_allowed() -> None:
    """
    Current-weather lookup must be authorized.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "get_current_weather"
    )

    assert result.is_valid is True


def test_forecast_tool_is_allowed() -> None:
    """
    Forecast lookup must be authorized.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "get_forecast"
    )

    assert result.is_valid is True


def test_weather_analysis_tool_is_allowed() -> None:
    """
    Weather-analysis tool must be authorized.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "analyze_weather"
    )

    assert result.is_valid is True


def test_weather_intelligence_tool_is_allowed() -> None:
    """
    Weather-intelligence tool must be authorized.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "get_weather_intelligence"
    )

    assert result.is_valid is True


def test_weather_plan_tool_is_allowed() -> None:
    """
    Weather-planning tool must be authorized.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "get_weather_plan"
    )

    assert result.is_valid is True


def test_unknown_tool_is_blocked() -> None:
    """
    Tools outside the explicit allow-list must be rejected.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "unknown_tool"
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_NOT_ALLOWED"


def test_shell_execution_tool_is_blocked() -> None:
    """
    An unauthorized shell-execution tool must be rejected.
    """

    validator = ToolNameValidator()

    result = validator.validate(
        "execute_shell_command"
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_NOT_ALLOWED"


def test_empty_tool_name_is_blocked() -> None:
    """
    Empty tool names must be rejected.
    """

    validator = ToolNameValidator()

    result = validator.validate("")

    assert result.is_valid is False
    assert result.error_code == "TOOL_NAME_EMPTY"


def test_whitespace_tool_name_is_blocked() -> None:
    """
    Whitespace-only tool names must be rejected.
    """

    validator = ToolNameValidator()

    result = validator.validate("   ")

    assert result.is_valid is False
    assert result.error_code == "TOOL_NAME_EMPTY"


def test_non_string_tool_name_is_blocked() -> None:
    """
    Non-string tool identifiers must be rejected.
    """

    validator = ToolNameValidator()

    result = validator.validate(123)

    assert result.is_valid is False
    assert result.error_code == "TOOL_INVALID_NAME_TYPE"