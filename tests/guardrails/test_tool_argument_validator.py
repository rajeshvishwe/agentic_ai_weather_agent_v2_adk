"""
Unit tests for Phase 9.4 tool argument validation.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.validators.tool_argument_validator import (
    ToolArgumentValidator,
)


def test_valid_current_weather_arguments_pass() -> None:
    """Valid current-weather arguments must pass."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is True


def test_valid_forecast_arguments_pass() -> None:
    """Valid forecast arguments must pass."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_forecast",
        {
            "city": "Mumbai",
        },
    )

    assert result.is_valid is True


def test_valid_weather_plan_arguments_pass() -> None:
    """Valid weather-planning arguments must pass."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_weather_plan",
        {
            "city": "London",
        },
    )

    assert result.is_valid is True


def test_valid_weather_intelligence_arguments_pass() -> None:
    """Valid weather-intelligence arguments must pass."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_weather_intelligence",
        {
            "city": "Tokyo",
        },
    )

    assert result.is_valid is True


def test_valid_multi_city_analysis_arguments_pass() -> None:
    """Valid multi-city analytics arguments must pass."""

    validator = ToolArgumentValidator()

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


def test_missing_city_is_blocked() -> None:
    """Required city argument must not be omitted."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {},
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_REQUIRED"


def test_empty_city_is_blocked() -> None:
    """Empty city values must be rejected."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": "",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_EMPTY"


def test_whitespace_city_is_blocked() -> None:
    """Whitespace-only city values must be rejected."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": "     ",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_EMPTY"


def test_non_string_city_is_blocked() -> None:
    """Non-text city arguments must be rejected."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": 123,
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_INVALID_TYPE"


def test_excessively_long_city_is_blocked() -> None:
    """Excessively long city arguments must be rejected."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": "A" * 101,
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_TOO_LONG"


def test_unexpected_argument_is_blocked() -> None:
    """Unexpected parameters must fail validation."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        {
            "city": "Delhi",
            "command": "delete_database",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_UNEXPECTED"


def test_unknown_tool_policy_is_blocked() -> None:
    """Tools without argument policies must fail closed."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "unknown_tool",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_POLICY_NOT_FOUND"


def test_non_mapping_arguments_are_blocked() -> None:
    """Tool arguments must be mapping objects."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "get_current_weather",
        "Delhi",
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENTS_INVALID_TYPE"


def test_analyze_weather_requires_cities() -> None:
    """Analytics tool must require the plural cities argument."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "analyze_weather",
        {
            "city": "Delhi",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_ARGUMENT_REQUIRED"


def test_analyze_weather_empty_cities_is_blocked() -> None:
    """An empty city collection must be rejected."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "analyze_weather",
        {
            "cities": [],
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITIES_EMPTY"


def test_analyze_weather_non_list_is_blocked() -> None:
    """Analytics cities must be supplied as a list."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "analyze_weather",
        {
            "cities": "Delhi",
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITIES_INVALID_TYPE"


def test_analyze_weather_invalid_city_is_blocked() -> None:
    """Every city inside a multi-city request must be valid."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "analyze_weather",
        {
            "cities": [
                "Delhi",
                "",
            ],
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_CITY_EMPTY"


def test_analyze_weather_too_many_cities_is_blocked() -> None:
    """Analytics requests must respect the city-count limit."""

    validator = ToolArgumentValidator()

    result = validator.validate(
        "analyze_weather",
        {
            "cities": [
                f"City-{index}"
                for index in range(11)
            ],
        },
    )

    assert result.is_valid is False
    assert result.error_code == "TOOL_TOO_MANY_CITIES"