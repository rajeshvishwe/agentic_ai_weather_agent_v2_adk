"""
Deterministic generated-output leakage validator.

The validator detects explicit disclosure patterns involving internal
instructions, private reasoning, and common credential formats.

It intentionally uses deterministic regular expressions instead of
another LLM so that security decisions remain predictable and auditable.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from re import Pattern

from weather_intelligence_agent_v2.guardrails.config.output_policy import (
    INSTRUCTION_LEAKAGE_PATTERNS,
    REASONING_LEAKAGE_PATTERNS,
    SECRET_LEAKAGE_PATTERNS,
)
from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class LeakageValidator(BaseValidator):
    """
    Detect potentially sensitive information in generated responses.

    Three categories are currently protected:

    1. Internal/system instruction disclosure
    2. Chain-of-thought or private reasoning disclosure
    3. Credential or secret disclosure
    """

    def __init__(self) -> None:
        """
        Compile deterministic leakage-detection expressions.
        """

        self._instruction_patterns = self._compile_patterns(
            INSTRUCTION_LEAKAGE_PATTERNS
        )

        self._reasoning_patterns = self._compile_patterns(
            REASONING_LEAKAGE_PATTERNS
        )

        self._secret_patterns = self._compile_patterns(
            SECRET_LEAKAGE_PATTERNS
        )

    @staticmethod
    def _compile_patterns(
        patterns: Iterable[str],
    ) -> tuple[Pattern[str], ...]:
        """
        Compile raw regular-expression patterns.

        Args:
            patterns:
                Regex expressions to compile.

        Returns:
            Tuple containing compiled case-insensitive expressions.
        """

        return tuple(
            re.compile(
                pattern,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )

    @staticmethod
    def _matches_any(
        message: str,
        patterns: Iterable[Pattern[str]],
    ) -> bool:
        """
        Determine whether any expression matches the response.

        Args:
            message:
                Generated response.

            patterns:
                Compiled expressions.

        Returns:
            True when at least one expression matches.
        """

        return any(
            pattern.search(message) is not None
            for pattern in patterns
        )

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate generated output for sensitive-information leakage.

        Args:
            message:
                Generated response returned by the model.

        Returns:
            ValidationResult:
                Success when no configured disclosure pattern is detected.
        """

        if not isinstance(message, str):
            return ValidationResult.failure(
                error_code="OUTPUT_INVALID_TYPE",
                message="Generated response must be textual.",
                validator=self.__class__.__name__,
                category="OUTPUT_SECURITY",
                severity=ValidationSeverity.ERROR,
            )

        if self._matches_any(
            message,
            self._instruction_patterns,
        ):
            return ValidationResult.failure(
                error_code="OUTPUT_INSTRUCTION_LEAKAGE",
                message=(
                    "Generated response may expose internal "
                    "application instructions."
                ),
                validator=self.__class__.__name__,
                category="OUTPUT_SECURITY",
                severity=ValidationSeverity.CRITICAL,
            )

        if self._matches_any(
            message,
            self._reasoning_patterns,
        ):
            return ValidationResult.failure(
                error_code="OUTPUT_REASONING_LEAKAGE",
                message=(
                    "Generated response may expose private "
                    "model reasoning."
                ),
                validator=self.__class__.__name__,
                category="OUTPUT_SECURITY",
                severity=ValidationSeverity.CRITICAL,
            )

        if self._matches_any(
            message,
            self._secret_patterns,
        ):
            return ValidationResult.failure(
                error_code="OUTPUT_SECRET_LEAKAGE",
                message=(
                    "Generated response may expose sensitive "
                    "credentials or tokens."
                ),
                validator=self.__class__.__name__,
                category="OUTPUT_SECURITY",
                severity=ValidationSeverity.CRITICAL,
            )

        return ValidationResult.success()