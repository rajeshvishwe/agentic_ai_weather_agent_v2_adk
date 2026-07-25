"""
Validates unsupported control characters.
"""

from __future__ import annotations

import re

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class CharacterValidator(BaseValidator):
    """
    Validate that user input does not contain unsupported
    ASCII control characters.

    Allowed:
        - Printable characters
        - Newline
        - Tab
        - Carriage return

    Rejected:
        - Non-printable ASCII control characters
          (0x00–0x08, 0x0B, 0x0C, 0x0E–0x1F)
    """

    CONTROL_CHARACTER_PATTERN = re.compile(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]"
    )

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate that the message does not contain
        unsupported control characters.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        # Let LengthValidator handle None/empty inputs.
        if message is None:
            return ValidationResult.success()

        if self.CONTROL_CHARACTER_PATTERN.search(message):

            return ValidationResult.failure(
                error_code="INVALID_CHARACTERS",
                message=(
                    "Input contains unsupported "
                    "control characters."
                ),
                validator=self.__class__.__name__,
                category="Input Validation",
            )

        return ValidationResult.success()