"""
Prompt injection validator.

This validator detects common prompt injection attacks using
deterministic pattern matching.

No LLM is used.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.config.prompt_patterns import (
    CHAIN_OF_THOUGHT_PATTERNS,
    INSTRUCTION_OVERRIDE_PATTERNS,
    JAILBREAK_PATTERNS,
    PROMPT_EXTRACTION_PATTERNS,
    ROLE_HIJACK_PATTERNS,
    TOOL_ABUSE_PATTERNS,
)
from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class PromptInjectionValidator(BaseValidator):
    """
    Detect common prompt injection attacks using
    deterministic pattern matching.

    This validator blocks attempts such as:

    - Prompt injection
    - Prompt extraction
    - Role hijacking
    - Jailbreak attempts
    - Chain-of-thought extraction
    - Tool abuse
    """

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate user input for prompt manipulation attacks.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        # Let LengthValidator handle None/empty inputs.
        if message is None:
            return ValidationResult.success()

        text = message.lower()

        checks = (
            (
                "PROMPT_INJECTION",
                INSTRUCTION_OVERRIDE_PATTERNS,
            ),
            (
                "PROMPT_EXTRACTION",
                PROMPT_EXTRACTION_PATTERNS,
            ),
            (
                "ROLE_HIJACK",
                ROLE_HIJACK_PATTERNS,
            ),
            (
                "JAILBREAK",
                JAILBREAK_PATTERNS,
            ),
            (
                "CHAIN_OF_THOUGHT",
                CHAIN_OF_THOUGHT_PATTERNS,
            ),
            (
                "TOOL_ABUSE",
                TOOL_ABUSE_PATTERNS,
            ),
        )

        for error_code, patterns in checks:

            if any(
                pattern in text
                for pattern in patterns
            ):

                return ValidationResult.failure(
                    error_code=error_code,
                    message=(
                        "The request contains unsupported "
                        "prompt manipulation instructions."
                    ),
                    validator=self.__class__.__name__,
                    category="Prompt Security",
                    severity=ValidationSeverity.CRITICAL,
                )

        return ValidationResult.success()