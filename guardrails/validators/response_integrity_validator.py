"""
Response integrity validator for generated model output.

The validator ensures that a generated response exists, is textual,
and contains meaningful non-whitespace content before it is allowed
to leave the application boundary.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class ResponseIntegrityValidator(BaseValidator):
    """
    Validate the basic structural integrity of generated output.

    This validator rejects responses that are:

    * None
    * not strings
    * empty strings
    * whitespace-only strings

    More specialized security checks are intentionally delegated to
    other validators to preserve single-responsibility design.
    """

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate generated response integrity.

        Args:
            message:
                Generated response returned by the AI orchestration layer.

        Returns:
            ValidationResult:
                Success when the response contains valid textual content.
                Otherwise, a deterministic validation failure.
        """

        if message is None:
            return ValidationResult.failure(
                error_code="OUTPUT_MISSING",
                message="Generated response is missing.",
                validator=self.__class__.__name__,
                category="OUTPUT_INTEGRITY",
                severity=ValidationSeverity.ERROR,
            )

        if not isinstance(message, str):
            return ValidationResult.failure(
                error_code="OUTPUT_INVALID_TYPE",
                message="Generated response must be textual.",
                validator=self.__class__.__name__,
                category="OUTPUT_INTEGRITY",
                severity=ValidationSeverity.ERROR,
            )

        if not message.strip():
            return ValidationResult.failure(
                error_code="OUTPUT_EMPTY",
                message="Generated response is empty.",
                validator=self.__class__.__name__,
                category="OUTPUT_INTEGRITY",
                severity=ValidationSeverity.ERROR,
            )

        return ValidationResult.success()