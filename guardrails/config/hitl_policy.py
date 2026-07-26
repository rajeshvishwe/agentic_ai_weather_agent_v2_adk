"""
Human-in-the-loop security policy.

This module defines tool risk levels and approval requirements.

Existing Weather Intelligence Agent tools are read-only and therefore
remain auto-approved.

Future side-effecting tools can be assigned higher approval levels
without changing the HITL orchestration interface.
"""

from __future__ import annotations

from enum import Enum


class ApprovalLevel(str, Enum):
    """
    Approval requirement for tool execution.
    """

    AUTO = "AUTO"
    CONFIRMATION = "CONFIRMATION"
    EXPLICIT_APPROVAL = "EXPLICIT_APPROVAL"


TOOL_APPROVAL_POLICY: dict[str, ApprovalLevel] = {
    "get_current_weather": ApprovalLevel.AUTO,
    "get_forecast": ApprovalLevel.AUTO,
    "analyze_weather": ApprovalLevel.AUTO,
    "get_weather_intelligence": ApprovalLevel.AUTO,
    "get_weather_plan": ApprovalLevel.AUTO,

    # Future examples:
    #
    # "send_weather_alert": ApprovalLevel.CONFIRMATION,
    # "create_calendar_event": ApprovalLevel.CONFIRMATION,
    # "cancel_booking": ApprovalLevel.EXPLICIT_APPROVAL,
    # "purchase_ticket": ApprovalLevel.EXPLICIT_APPROVAL,
}