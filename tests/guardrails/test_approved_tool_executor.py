"""
Tests for approved HITL tool execution.
"""

from __future__ import annotations

import pytest

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalExecutionStatus,
)
from weather_intelligence_agent_v2.guardrails.approval_service import (
    ApprovalService,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)
from weather_intelligence_agent_v2.services.approved_tool_executor import (
    ApprovedToolExecutor,
)


def test_approved_weather_reminder_executes() -> None:

    service = ApprovalService()

    request = (
        service.create_request(
            tool_name=(
                "create_weather_reminder"
            ),
            arguments={
                "city": "Delhi",
                "reminder_time": (
                    "tomorrow morning"
                ),
                "message": (
                    "Check Delhi weather."
                ),
            },
            approval_level=(
                ApprovalLevel.CONFIRMATION
            ),
        )
    )

    service.approve(
        request.request_id
    )

    executor = (
        ApprovedToolExecutor()
    )

    result = executor.execute(
        request
    )

    request.mark_execution_success(
        result
    )

    assert (
        request.execution_status
        == ApprovalExecutionStatus
        .EXECUTED
    )

    assert (
        result[
            "success"
        ]
        is True
    )


def test_pending_request_cannot_execute() -> None:

    service = ApprovalService()

    request = (
        service.create_request(
            tool_name=(
                "create_weather_reminder"
            ),
            arguments={
                "city": "Delhi",
                "reminder_time": (
                    "tomorrow morning"
                ),
                "message": (
                    "Check weather."
                ),
            },
            approval_level=(
                ApprovalLevel.CONFIRMATION
            ),
        )
    )

    executor = (
        ApprovedToolExecutor()
    )

    with pytest.raises(
        ValueError
    ):

        executor.execute(
            request
        )


def test_rejected_request_cannot_execute() -> None:

    service = ApprovalService()

    request = (
        service.create_request(
            tool_name=(
                "create_weather_reminder"
            ),
            arguments={
                "city": "Delhi",
                "reminder_time": (
                    "tomorrow morning"
                ),
                "message": (
                    "Check weather."
                ),
            },
            approval_level=(
                ApprovalLevel.CONFIRMATION
            ),
        )
    )

    service.reject(
        request.request_id
    )

    executor = (
        ApprovedToolExecutor()
    )

    with pytest.raises(
        ValueError
    ):

        executor.execute(
            request
        )


def test_unknown_approved_tool_cannot_execute() -> None:

    service = ApprovalService()

    request = (
        service.create_request(
            tool_name=(
                "unregistered_tool"
            ),
            arguments={},
            approval_level=(
                ApprovalLevel.CONFIRMATION
            ),
        )
    )

    service.approve(
        request.request_id
    )

    executor = (
        ApprovedToolExecutor()
    )

    with pytest.raises(
        ValueError
    ):

        executor.execute(
            request
        )