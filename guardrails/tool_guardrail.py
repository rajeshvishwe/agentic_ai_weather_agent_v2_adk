"""
Enterprise tool guardrail orchestration.

The ToolGuardrail validates tool execution requests before an approved
tool is allowed to run.

Phase 9.4 uses deterministic validation so authorization decisions are
predictable, auditable, and testable.

Phase 11 observability records Prometheus metrics when tool execution is
blocked while preserving the existing deterministic validation behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.tool_argument_validator import (
    ToolArgumentValidator,
)
from weather_intelligence_agent_v2.guardrails.validators.tool_name_validator import (
    ToolNameValidator,
)
from weather_intelligence_agent_v2.observability.security_metrics import (
    TOOL_GUARDRAIL_BLOCKS_TOTAL,
)


class ToolGuardrail:
    """
    Coordinate deterministic validation of tool execution requests.

    Validation order is fail-fast:

    1. Validate tool authorization.
    2. Validate tool arguments.

    If tool-name validation fails, argument validation is not executed.

    Prometheus metrics are emitted only when validation rejects the
    requested tool execution.
    """

    def __init__(self) -> None:
        """
        Initialize tool guardrail validators.
        """

        self._tool_name_validator = ToolNameValidator()
        self._tool_argument_validator = ToolArgumentValidator()

    def validate(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
    ) -> ValidationResult:
        """
        Validate a requested tool execution.

        Validation remains fail-fast.

        Tool-name failures are recorded separately from tool-argument
        failures so operational monitoring can distinguish authorization
        blocks from invalid-argument blocks.

        Args:
            tool_name:
                Name of the tool requested by the agent.

            arguments:
                Arguments supplied to the requested tool.

        Returns:
            ValidationResult:
                Success when the tool is authorized and all arguments
                satisfy the configured security policy.
        """

        tool_name_result = (
            self._tool_name_validator.validate(
                tool_name
            )
        )

        if not tool_name_result.is_valid:

            TOOL_GUARDRAIL_BLOCKS_TOTAL.labels(
                validation_stage="tool_name",
            ).inc()

            return tool_name_result

        argument_result = (
            self._tool_argument_validator.validate(
                tool_name=tool_name,
                arguments=arguments,
            )
        )

        if not argument_result.is_valid:

            TOOL_GUARDRAIL_BLOCKS_TOTAL.labels(
                validation_stage="tool_arguments",
            ).inc()

        return argument_result