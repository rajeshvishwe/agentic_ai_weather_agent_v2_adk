"""
Approved HITL tool executor.

This component executes only explicitly allowlisted tools after a
human has approved the associated ApprovalRequest.

Security properties:

- request must already be APPROVED
- tool name is allowlisted
- arguments are revalidated immediately before execution
- arbitrary dynamic imports are not permitted
- eval/exec are never used
- execution occurs at most once per ApprovalRequest
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalRequest,
    ApprovalStatus,
)
from weather_intelligence_agent_v2.guardrails.tool_guardrail import (
    ToolGuardrail,
)
from weather_intelligence_agent_v2.tools.reminder_tools import (
    create_weather_reminder,
)


ApprovedToolCallable = Callable[
    ...,
    dict[str, Any],
]


class ApprovedToolExecutor:
    """
    Execute explicitly approved HITL tools.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize secure executable-tool registry.
        """

        self._tool_guardrail = (
            ToolGuardrail()
        )

        self._registry: dict[
            str,
            ApprovedToolCallable,
        ] = {
            "create_weather_reminder": (
                create_weather_reminder
            ),
        }

    def execute(
        self,
        request: ApprovalRequest,
    ) -> dict[str, Any]:
        """
        Execute one approved request.

        Args:
            request:
                Approved HITL request.

        Returns:
            Tool result.

        Raises:
            ValueError:
                If request is not approved,
                tool is not executable,
                or security validation fails.
        """

        if (
            request.status
            != ApprovalStatus.APPROVED
        ):

            raise ValueError(
                (
                    "Only approved HITL "
                    "requests may execute."
                )
            )

        tool_name = (
            request.tool_name
        )

        arguments = dict(
            request.arguments
        )

        # ------------------------------------------------------
        # Defense in depth:
        # revalidate immediately before execution.
        # ------------------------------------------------------

        validation = (
            self._tool_guardrail.validate(
                tool_name=tool_name,
                arguments=arguments,
            )
        )

        if not validation.is_valid:

            raise ValueError(
                (
                    "Approved tool request "
                    "failed security "
                    "revalidation."
                )
            )

        tool = self._registry.get(
            tool_name
        )

        if tool is None:

            raise ValueError(
                (
                    "Approved tool is not "
                    "registered for execution."
                )
            )

        result = tool(
            **arguments
        )

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                (
                    "Approved tool returned "
                    "an invalid result format."
                )
            )

        return result