"""
Output-length validator.

This validator prevents unexpectedly large AI responses from leaving
the application boundary.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.config.output_policy import (
    MAX_OUTPUT_LENGTH,
)
from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class OutputLengthValidator(BaseValidator):
    """
    Enforce the maximum permitted generated-response length.

    The validator protects the API, UI, logs, and downstream consumers
    from unexpectedly large or runaway model responses.
    """

    def __init__(
        self,
        max_length: int = MAX_OUTPUT_LENGTH,
    ) -> None:
        """
        Initialise the validator.

        Args:
            max_length:
                Maximum permitted response length in characters.

        Raises:
            ValueError:
                If max_length is not a positive integer.
        """

        if max_length <= 0:
            raise ValueError("max_length must be greater than zero.")

        self._max_length = max_length

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate generated-response length.

        Args:
            message:
                Generated model response.

        Returns:
            ValidationResult:
                Success when the output is within the configured limit.
        """

        if not isinstance(message, str):
            return ValidationResult.failure(
                error_code="OUTPUT_INVALID_TYPE",
                message="Generated response must be textual.",
                validator=self.__class__.__name__,
                category="OUTPUT_LENGTH",
                severity=ValidationSeverity.ERROR,
            )

        if len(message) > self._max_length:
            return ValidationResult.failure(
                error_code="OUTPUT_TOO_LONG",
                message=(
                    "Generated response exceeds the maximum permitted "
                    "response length."
                ),
                validator=self.__class__.__name__,
                category="OUTPUT_LENGTH",
                severity=ValidationSeverity.WARNING,
            )

        return ValidationResult.success()