"""
Enterprise input guardrail.

Executes deterministic validators before
Google ADK is invoked.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.character_validator import (
    CharacterValidator,
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

    Validation order:

    1. Length validation
    2. Character validation
    3. Prompt injection validation
    4. Weather intent validation
    """

    def __init__(self) -> None:
        """Initialise the deterministic validation pipeline."""

        self._pipeline = ValidationPipeline(
            validators=[
                LengthValidator(),
                CharacterValidator(),

                # Security validation must run before
                # business/domain validation.
                PromptInjectionValidator(),

                WeatherIntentValidator(),
            ]
        )

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Execute the validation pipeline.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        return self._pipeline.validate(message)