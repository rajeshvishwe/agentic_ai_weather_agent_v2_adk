"""
Google ADK tool-execution security and HITL callback.

This module integrates:

1. Phase 9.4 ToolGuardrail
2. Phase 9.5 Human-in-the-Loop policy
3. Phase 9.5 ApprovalService

with Google ADK's before-tool execution lifecycle.

Execution flow:

    ADK tool request
        -> ToolGuardrail
        -> HITLGuardrail
        -> AUTO: execute normally
        -> APPROVAL REQUIRED: create pending ApprovalRequest
        -> BLOCKED: reject execution

Current read-only weather tools remain configured for automatic
execution.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from weather_intelligence_agent_v2.guardrails.approval_service import (
    ApprovalService,
)
from weather_intelligence_agent_v2.guardrails.hitl_guardrail import (
    HITLGuardrail,
)
from weather_intelligence_agent_v2.guardrails.tool_guardrail import (
    ToolGuardrail,
)


_TOOL_GUARDRAIL = ToolGuardrail()
_HITL_GUARDRAIL = HITLGuardrail()
_APPROVAL_SERVICE = ApprovalService()


def weather_before_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any] | None:
    """
    Validate and authorize an ADK tool request before execution.

    Processing stages:

    1. Validate tool authorization and arguments.
    2. Evaluate HITL approval requirements.
    3. Automatically allow low-risk tools.
    4. Create a pending approval request for operations requiring
       human approval.

    Args:
        tool:
            Google ADK tool selected by the model.

        args:
            Arguments generated for the selected tool.

        tool_context:
            Google ADK execution context associated with the tool call.

    Returns:
        None:
            Tool may execute normally.

        dict[str, Any]:
            Tool execution must be skipped. The returned dictionary
            describes either the security rejection or pending human
            approval request.
    """

    del tool_context

    tool_name = getattr(
        tool,
        "name",
        "",
    )

    # ------------------------------------------------------------
    # Phase 9.4 — Tool security validation
    # ------------------------------------------------------------

    validation = _TOOL_GUARDRAIL.validate(
        tool_name=tool_name,
        arguments=args,
    )

    if not validation.is_valid:
        return {
            "status": "blocked",
            "error_code": validation.error_code,
            "message": (
                "The requested weather tool operation was blocked "
                "by the tool security policy."
            ),
        }

    # ------------------------------------------------------------
    # Phase 9.5 — HITL policy
    # ------------------------------------------------------------

    try:
        hitl_decision = _HITL_GUARDRAIL.evaluate(
            tool_name
        )
    except ValueError:
        return {
            "status": "blocked",
            "error_code": "HITL_POLICY_NOT_FOUND",
            "message": (
                "The requested tool operation does not have "
                "an approval policy."
            ),
        }

    # Low-risk/read-only tool.
    if hitl_decision.auto_execute:
        return None

    # ------------------------------------------------------------
    # Phase 9.5 — Approval request creation
    # ------------------------------------------------------------

    approval_request = _APPROVAL_SERVICE.create_request(
        tool_name=tool_name,
        arguments=args,
        approval_level=hitl_decision.approval_level,
    )

    return {
        "status": "approval_required",
        "error_code": "HITL_APPROVAL_REQUIRED",
        "request_id": approval_request.request_id,
        "approval_status": approval_request.status.value,
        "approval_level": approval_request.approval_level.value,
        "message": (
            "Human approval is required before this "
            "tool operation can execute."
        ),
    }


def get_approval_service() -> ApprovalService:
    """
    Return the application-level HITL approval service.

    This accessor keeps approval storage encapsulated while allowing
    later API endpoints and tests to interact with pending approval
    requests.

    Returns:
        ApprovalService:
            Shared in-memory approval service instance.
    """

    return _APPROVAL_SERVICE