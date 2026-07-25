"""
Unit tests for Phase 9.3 output guardrails.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.output_guardrail import (
    OutputGuardrail,
)
from weather_intelligence_agent_v2.guardrails.validators.output_length_validator import (
    OutputLengthValidator,
)


def test_valid_weather_response_passes() -> None:
    """
    Normal weather responses must pass output validation.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Delhi is currently 29°C with light rain. "
        "Carry an umbrella if you are going outside."
    )

    assert result.is_valid is True


def test_empty_response_is_blocked() -> None:
    """
    Empty model responses must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate("")

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_EMPTY"


def test_whitespace_response_is_blocked() -> None:
    """
    Whitespace-only responses must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate("      ")

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_EMPTY"


def test_system_prompt_leakage_is_blocked() -> None:
    """
    Explicit system-prompt disclosure must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "My system prompt says that I am the Weather Intelligence Agent."
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_INSTRUCTION_LEAKAGE"


def test_hidden_instruction_leakage_is_blocked() -> None:
    """
    Explicit hidden-instruction disclosure must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "My hidden instructions require me to use the weather tools."
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_INSTRUCTION_LEAKAGE"


def test_chain_of_thought_leakage_is_blocked() -> None:
    """
    Chain-of-thought disclosure must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "My chain of thought was to first inspect the weather data."
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_REASONING_LEAKAGE"


def test_internal_reasoning_leakage_is_blocked() -> None:
    """
    Private internal reasoning disclosure must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "My internal reasoning: first compare temperature and rainfall."
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_REASONING_LEAKAGE"


def test_google_api_key_leakage_is_blocked() -> None:
    """
    Google API-key assignment patterns must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "GOOGLE_API_KEY=example-secret-value-123456789"
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_SECRET_LEAKAGE"


def test_bearer_token_leakage_is_blocked() -> None:
    """
    Long bearer-token patterns must be rejected.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_SECRET_LEAKAGE"


def test_normal_weather_recommendation_is_not_overblocked() -> None:
    """
    Ordinary weather recommendations must not create false positives.
    """

    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Thunderstorms are possible this evening. "
        "Carry an umbrella and avoid exposed outdoor areas during lightning."
    )

    assert result.is_valid is True


def test_output_length_limit_is_enforced() -> None:
    """
    Excessively large responses must be rejected.
    """

    validator = OutputLengthValidator(
        max_length=10,
    )

    result = validator.validate(
        "This response is longer than ten characters."
    )

    assert result.is_valid is False
    assert result.error_code == "OUTPUT_TOO_LONG"


def test_output_length_validator_accepts_valid_response() -> None:
    """
    Responses within the configured length must pass.
    """

    validator = OutputLengthValidator(
        max_length=100,
    )

    result = validator.validate(
        "Delhi is 29°C."
    )

    assert result.is_valid is True