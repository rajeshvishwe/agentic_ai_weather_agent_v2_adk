"""
Unit tests for the Phase 9.5 HITL approval service.
"""

from __future__ import annotations

import pytest

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalStatus,
)
from weather_intelligence_agent_v2.guardrails.approval_service import (
    ApprovalService,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


def test_create_approval_request() -> None:
    """New approval requests must start in PENDING state."""

    service = ApprovalService()

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Delhi",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    assert request.request_id
    assert request.tool_name == "future_side_effect_tool"
    assert request.status == ApprovalStatus.PENDING
    assert request.resolved_at is None


def test_created_request_can_be_retrieved() -> None:
    """Created requests must be retrievable by identifier."""

    service = ApprovalService()

    created = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Mumbai",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    retrieved = service.get_request(
        created.request_id
    )

    assert retrieved is created


def test_request_can_be_approved() -> None:
    """Pending requests must support approval."""

    service = ApprovalService()

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    approved = service.approve(
        request.request_id
    )

    assert approved.status == ApprovalStatus.APPROVED
    assert approved.resolved_at is not None


def test_request_can_be_rejected() -> None:
    """Pending requests must support rejection."""

    service = ApprovalService()

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.EXPLICIT_APPROVAL,
    )

    rejected = service.reject(
        request.request_id
    )

    assert rejected.status == ApprovalStatus.REJECTED
    assert rejected.resolved_at is not None


def test_approved_request_cannot_be_approved_again() -> None:
    """Resolved approval requests must not be modified twice."""

    service = ApprovalService()

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    service.approve(
        request.request_id
    )

    with pytest.raises(ValueError):
        service.approve(
            request.request_id
        )


def test_rejected_request_cannot_be_approved() -> None:
    """Rejected requests must remain resolved."""

    service = ApprovalService()

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    service.reject(
        request.request_id
    )

    with pytest.raises(ValueError):
        service.approve(
            request.request_id
        )


def test_unknown_request_fails() -> None:
    """Unknown approval identifiers must fail explicitly."""

    service = ApprovalService()

    with pytest.raises(KeyError):
        service.get_request(
            "missing-request-id"
        )


def test_arguments_are_copied_when_request_is_created() -> None:
    """External argument mutation must not alter stored request data."""

    service = ApprovalService()

    arguments = {
        "city": "Delhi",
    }

    request = service.create_request(
        tool_name="future_side_effect_tool",
        arguments=arguments,
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    arguments["city"] = "Mumbai"

    assert request.arguments["city"] == "Delhi"