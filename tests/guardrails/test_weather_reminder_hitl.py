"""
HITL tests for create_weather_reminder.

These tests verify that:

- the tool is authorized
- arguments are validated
- the HITL policy requires confirmation
- the ADK callback creates a pending approval request
- the tool does not execute automatically
"""

from __future__ import annotations

from dataclasses import dataclass

from weather_intelligence_agent_v2.guardrails import (
    adk_tool_guardrail_callback as callback_module,
)
from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalStatus,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


@dataclass
class FakeTool:
    """
    Minimal ADK tool test double.
    """

    name: str


class FakeToolContext:
    """
    Minimal ToolContext-compatible test double.
    """


def test_weather_reminder_requires_confirmation() -> None:
    """
    Weather reminder must never auto-execute.
    """

    result = (
        callback_module
        .weather_before_tool_callback(
            tool=FakeTool(
                name=(
                    "create_weather_reminder"
                )
            ),
            args={
                "city": "Delhi",
                "reminder_time": (
                    "tomorrow morning"
                ),
                "message": (
                    "Check Delhi weather."
                ),
            },
            tool_context=(
                FakeToolContext()
            ),
        )
    )

    assert result is not None

    assert (
        result[
            "status"
        ]
        == "approval_required"
    )

    assert (
        result[
            "error_code"
        ]
        == "HITL_APPROVAL_REQUIRED"
    )

    assert (
        result[
            "approval_level"
        ]
        == (
            ApprovalLevel
            .CONFIRMATION
            .value
        )
    )

    assert (
        result[
            "approval_status"
        ]
        == (
            ApprovalStatus
            .PENDING
            .value
        )
    )

    assert result[
        "request_id"
    ]


def test_weather_reminder_request_is_stored() -> None:
    """
    Pending reminder request must be stored by ApprovalService.
    """

    result = (
        callback_module
        .weather_before_tool_callback(
            tool=FakeTool(
                name=(
                    "create_weather_reminder"
                )
            ),
            args={
                "city": "Mumbai",
                "reminder_time": (
                    "Saturday morning"
                ),
                "message": (
                    "Check Mumbai rain "
                    "forecast."
                ),
            },
            tool_context=(
                FakeToolContext()
            ),
        )
    )

    approval_service = (
        callback_module
        .get_approval_service()
    )

    request = (
        approval_service
        .get_request(
            result[
                "request_id"
            ]
        )
    )

    assert (
        request.tool_name
        == "create_weather_reminder"
    )

    assert (
        request.status
        == ApprovalStatus.PENDING
    )

    assert request.arguments == {
        "city": "Mumbai",
        "reminder_time": (
            "Saturday morning"
        ),
        "message": (
            "Check Mumbai rain "
            "forecast."
        ),
    }


def test_invalid_weather_reminder_arguments_are_blocked() -> None:
    """
    Invalid reminder request must be blocked before HITL.
    """

    result = (
        callback_module
        .weather_before_tool_callback(
            tool=FakeTool(
                name=(
                    "create_weather_reminder"
                )
            ),
            args={
                "city": "Delhi",
                "reminder_time": "",
                "message": (
                    "Check weather."
                ),
            },
            tool_context=(
                FakeToolContext()
            ),
        )
    )

    assert result is not None

    assert (
        result[
            "status"
        ]
        == "blocked"
    )

    assert (
        result[
            "error_code"
        ]
        == "TOOL_REMINDER_TIME_EMPTY"
    )