"""
Human-in-the-loop approval guardrail.

This component determines whether a validated tool request may execute
automatically or requires human approval.
"""

from __future__ import annotations

from dataclasses import dataclass

from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
    TOOL_APPROVAL_POLICY,
)


@dataclass(frozen=True)
class HITLDecision:
    """
    Result of HITL policy evaluation.

    Attributes:
        tool_name:
            Requested tool.

        approval_level:
            Required human-approval level.

        auto_execute:
            Whether the tool may execute immediately.
    """

    tool_name: str
    approval_level: ApprovalLevel
    auto_execute: bool


class HITLGuardrail:
    """
    Evaluate human-approval requirements for tool execution.

    The guardrail uses a deny-by-default policy for tools that are not
    present in the configured approval policy.
    """

    def evaluate(
        self,
        tool_name: str,
    ) -> HITLDecision:
        """
        Determine the approval requirement for a tool.

        Args:
            tool_name:
                Requested tool name.

        Returns:
            HITLDecision:
                Approval decision for the requested tool.

        Raises:
            ValueError:
                If the tool has no configured approval policy.
        """

        if tool_name not in TOOL_APPROVAL_POLICY:
            raise ValueError(
                "No HITL approval policy exists for the requested tool."
            )

        approval_level = TOOL_APPROVAL_POLICY[tool_name]

        return HITLDecision(
            tool_name=tool_name,
            approval_level=approval_level,
            auto_execute=(
                approval_level == ApprovalLevel.AUTO
            ),
        )