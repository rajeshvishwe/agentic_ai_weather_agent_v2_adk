"""
Validates the length of user input.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class LengthValidator(BaseValidator):
    """
    Validates user input length.

    Validation Rules
    ----------------
    1. Message must not be None.
    2. Message must not be empty after trimming whitespace.
    3. Message must not exceed the configured maximum length.
    """

    DEFAULT_MAX_LENGTH = 1000

    def __init__(
        self,
        max_length: int = DEFAULT_MAX_LENGTH,
    ) -> None:
        self._max_length = max_length

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate the length of the user input.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        if message is None:
            return ValidationResult.failure(
                error_code="EMPTY_INPUT",
                message="Message cannot be empty.",
                validator=self.__class__.__name__,
                category="Input Validation",
            )

        message = message.strip()

        if not message:
            return ValidationResult.failure(
                error_code="EMPTY_INPUT",
                message="Message cannot be empty.",
                validator=self.__class__.__name__,
                category="Input Validation",
            )

        if len(message) > self._max_length:
            return ValidationResult.failure(
                error_code="MESSAGE_TOO_LONG",
                message=(
                    f"Message exceeds the maximum allowed length "
                    f"of {self._max_length} characters."
                ),
                validator=self.__class__.__name__,
                category="Input Validation",
            )

        return ValidationResult.success()