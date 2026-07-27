"""
Human-in-the-loop security policy.

This module defines tool risk levels and approval requirements.

Read-only Weather Intelligence tools execute automatically.

Side-effecting or user-action tools require human approval before
execution.
"""

from __future__ import annotations

from enum import Enum


class ApprovalLevel(
    str,
    Enum,
):
    """
    Approval requirement for tool execution.
    """

    AUTO = "AUTO"

    CONFIRMATION = (
        "CONFIRMATION"
    )

    EXPLICIT_APPROVAL = (
        "EXPLICIT_APPROVAL"
    )


TOOL_APPROVAL_POLICY: dict[
    str,
    ApprovalLevel,
] = {

    # ----------------------------------------------------------
    # Read-only weather tools
    # ----------------------------------------------------------

    "get_current_weather": (
        ApprovalLevel.AUTO
    ),

    "get_forecast": (
        ApprovalLevel.AUTO
    ),

    "analyze_weather": (
        ApprovalLevel.AUTO
    ),

    "get_weather_intelligence": (
        ApprovalLevel.AUTO
    ),

    "get_weather_plan": (
        ApprovalLevel.AUTO
    ),

    # ----------------------------------------------------------
    # Side-effecting / action tools
    # ----------------------------------------------------------

    "create_weather_reminder": (
        ApprovalLevel.CONFIRMATION
    ),

    # Future examples:
    #
    # "send_weather_alert":
    #     ApprovalLevel.CONFIRMATION,
    #
    # "create_calendar_event":
    #     ApprovalLevel.CONFIRMATION,
    #
    # "cancel_booking":
    #     ApprovalLevel.EXPLICIT_APPROVAL,
    #
    # "purchase_ticket":
    #     ApprovalLevel.EXPLICIT_APPROVAL,
}