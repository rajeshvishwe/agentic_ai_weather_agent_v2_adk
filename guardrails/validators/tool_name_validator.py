"""
Tool-name authorization validator.

This validator ensures that Google ADK may execute only tools that are
explicitly approved by the Weather Intelligence Agent security policy.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.guardrails.config.tool_policy import (
    ALLOWED_TOOLS,
)
from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)


class ToolNameValidator:
    """
    Validate requested tool names against the configured allow-list.

    The validator implements a deny-by-default policy:

    - explicitly allowed tool -> PASS
    - unknown tool -> BLOCK
    - empty tool name -> BLOCK
    - non-string tool name -> BLOCK
    """

    def __init__(
        self,
        allowed_tools: frozenset[str] = ALLOWED_TOOLS,
    ) -> None:
        """
        Initialize the tool-name validator.

        Args:
            allowed_tools:
                Immutable collection containing authorized tool names.
        """

        self._allowed_tools = allowed_tools

    def validate(
        self,
        tool_name: str,
    ) -> ValidationResult:
        """
        Validate whether a requested tool is authorized.

        Args:
            tool_name:
                Name of the tool requested by the agent.

        Returns:
            ValidationResult:
                Successful result when the tool is authorized.
                Otherwise, a deterministic validation failure.
        """

        if not isinstance(tool_name, str):
            return ValidationResult.failure(
                error_code="TOOL_INVALID_NAME_TYPE",
                message="Tool name must be textual.",
                validator=self.__class__.__name__,
                category="TOOL_SECURITY",
                severity=ValidationSeverity.ERROR,
            )

        normalized_tool_name = tool_name.strip()

        if not normalized_tool_name:
            return ValidationResult.failure(
                error_code="TOOL_NAME_EMPTY",
                message="Tool name must not be empty.",
                validator=self.__class__.__name__,
                category="TOOL_SECURITY",
                severity=ValidationSeverity.ERROR,
            )

        if normalized_tool_name not in self._allowed_tools:
            return ValidationResult.failure(
                error_code="TOOL_NOT_ALLOWED",
                message="Requested tool is not authorized.",
                validator=self.__class__.__name__,
                category="TOOL_SECURITY",
                severity=ValidationSeverity.CRITICAL,
            )

        return ValidationResult.success()