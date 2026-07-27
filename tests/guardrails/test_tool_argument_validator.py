"""
Unit tests for deterministic tool argument validation.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.validators.tool_argument_validator import (
    ToolArgumentValidator,
)


def test_valid_current_weather_arguments_pass() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is True


def test_valid_forecast_arguments_pass() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_forecast",
        {
            "city": "Mumbai",
        },
    )

    assert result.is_valid is True


def test_valid_weather_plan_arguments_pass() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_weather_plan",
        {
            "city": "London",
        },
    )

    assert result.is_valid is True


def test_valid_weather_intelligence_arguments_pass() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_weather_intelligence",
        {
            "city": "Tokyo",
        },
    )

    assert result.is_valid is True


def test_valid_multi_city_analysis_arguments_pass() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "analyze_weather",
        {
            "cities": [
                "Delhi",
                "Mumbai",
                "London",
            ],
        },
    )

    assert result.is_valid is True


def test_valid_weather_reminder_arguments_pass() -> None:
    """
    Valid weather reminder arguments must pass.
    """

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "reminder_time": (
                "tomorrow morning"
            ),
            "message": (
                "Check Delhi weather."
            ),
        },
    )

    assert result.is_valid is True


def test_weather_reminder_requires_city() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "reminder_time": (
                "tomorrow morning"
            ),
            "message": (
                "Check the weather."
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_REQUIRED"
    )


def test_weather_reminder_requires_time() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "message": (
                "Check Delhi weather."
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_REQUIRED"
    )


def test_weather_reminder_requires_message() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "reminder_time": (
                "tomorrow morning"
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_REQUIRED"
    )


def test_empty_reminder_time_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "reminder_time": " ",
            "message": (
                "Check Delhi weather."
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_REMINDER_TIME_EMPTY"
    )


def test_empty_reminder_message_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "reminder_time": (
                "tomorrow morning"
            ),
            "message": " ",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_REMINDER_MESSAGE_EMPTY"
    )


def test_unexpected_reminder_argument_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "create_weather_reminder",
        {
            "city": "Delhi",
            "reminder_time": (
                "tomorrow morning"
            ),
            "message": (
                "Check Delhi weather."
            ),
            "shell_command": (
                "rm -rf /"
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_UNEXPECTED"
    )


def test_missing_city_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {},
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_REQUIRED"
    )


def test_empty_city_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": "",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITY_EMPTY"
    )


def test_whitespace_city_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": "     ",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITY_EMPTY"
    )


def test_non_string_city_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": 123,
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITY_INVALID_TYPE"
    )


def test_excessively_long_city_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": (
                "A" * 101
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITY_TOO_LONG"
    )


def test_unexpected_argument_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        {
            "city": "Delhi",
            "command": (
                "delete_database"
            ),
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_UNEXPECTED"
    )


def test_unknown_tool_policy_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "unknown_tool",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_POLICY_NOT_FOUND"
    )


def test_non_mapping_arguments_are_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "get_current_weather",
        "Delhi",
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENTS_INVALID_TYPE"
    )


def test_analyze_weather_requires_cities() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "analyze_weather",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_ARGUMENT_REQUIRED"
    )


def test_analyze_weather_empty_cities_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "analyze_weather",
        {
            "cities": [],
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITIES_EMPTY"
    )


def test_analyze_weather_non_list_is_blocked() -> None:

    validator = (
        ToolArgumentValidator()
    )

    result = validator.validate(
        "analyze_weather",
        {
            "cities": "Delhi",
        },
    )

    assert result.is_valid is False

    assert (
        result.error_code
        == "TOOL_CITIES_INVALID_TYPE"
    )