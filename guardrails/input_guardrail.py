"""
Enterprise input guardrail.

Executes deterministic validators before Google ADK is invoked.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.character_validator import (
    CharacterValidator,
)
from weather_intelligence_agent_v2.guardrails.validators.contextual_weather_followup_validator import (
    ContextualWeatherFollowupValidator,
)
from weather_intelligence_agent_v2.guardrails.validators.length_validator import (
    LengthValidator,
)
from weather_intelligence_agent_v2.guardrails.validators.pipeline import (
    ValidationPipeline,
)
from weather_intelligence_agent_v2.guardrails.validators.prompt_injection_validator import (
    PromptInjectionValidator,
)
from weather_intelligence_agent_v2.guardrails.validators.weather_intent_validator import (
    WeatherIntentValidator,
)


class InputGuardrail:
    """
    Enterprise deterministic input validation.

    Standard validation order:

    1. Length validation
    2. Character validation
    3. Prompt injection validation
    4. Weather intent validation

    For an already-established weather conversation, the standard pipeline
    always runs first.

    Only when it fails specifically because the message lacks standalone
    weather-domain evidence do we run a second narrow contextual pipeline:

    1. Length validation
    2. Character validation
    3. Prompt injection validation
    4. Contextual weather follow-up validation

    This preserves security controls and prevents conversation context from
    becoming a general bypass around the weather-domain boundary.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialise the deterministic validation pipelines.
        """

        self._standard_pipeline = ValidationPipeline(
            validators=[
                LengthValidator(),
                CharacterValidator(),
                PromptInjectionValidator(),
                WeatherIntentValidator(),
            ]
        )

        self._contextual_pipeline = ValidationPipeline(
            validators=[
                LengthValidator(),
                CharacterValidator(),
                PromptInjectionValidator(),
                ContextualWeatherFollowupValidator(),
            ]
        )

    def validate(
        self,
        message: str,
        *,
        allow_contextual_followup: bool = False,
    ) -> ValidationResult:
        """
        Execute deterministic input validation.

        Args:
            message:
                User input.

            allow_contextual_followup:
                Whether a narrow contextual weather follow-up may be
                accepted if standard weather-intent validation fails.

                This flag must be enabled only for a session that has
                already completed a valid weather-agent turn.

        Returns:
            ValidationResult.
        """

        standard_result = (
            self._standard_pipeline.validate(
                message
            )
        )

        if standard_result.is_valid:
            return standard_result

        if not allow_contextual_followup:
            return standard_result

        if (
            standard_result.error_code
            != "OUTSIDE_WEATHER_DOMAIN"
        ):
            return standard_result

        return (
            self._contextual_pipeline.validate(
                message
            )
        )