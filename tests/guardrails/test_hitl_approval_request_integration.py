"""
Integration tests for HITL approval-request creation.

These tests verify that the ADK before-tool callback creates a real
pending ApprovalRequest when the HITL policy requires human approval.

No Gemini or external weather API calls are made.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from weather_intelligence_agent_v2.guardrails import (
    adk_tool_guardrail_callback as callback_module,
)
from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalStatus,
)
from weather_intelligence_agent_v2.guardrails.approval_service import (
    ApprovalService,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)
from weather_intelligence_agent_v2.guardrails.hitl_guardrail import (
    HITLDecision,
)


@dataclass
class FakeTool:
    """
    Minimal ADK-compatible tool.

    Attributes:
        name:
            Tool identifier.
    """

    name: str


class FakeToolContext:
    """
    Minimal ToolContext-compatible test double.
    """


class ConfirmationRequiredHITLGuardrail:
    """
    HITL test double requiring confirmation.
    """

    def evaluate(
        self,
        tool_name: str,
    ) -> HITLDecision:
        """
        Return a confirmation-required decision.

        Args:
            tool_name:
                Requested tool.

        Returns:
            HITLDecision:
                Decision requiring confirmation.
        """

        return HITLDecision(
            tool_name=tool_name,
            approval_level=ApprovalLevel.CONFIRMATION,
            auto_execute=False,
        )


class ExplicitApprovalHITLGuardrail:
    """
    HITL test double requiring explicit approval.
    """

    def evaluate(
        self,
        tool_name: str,
    ) -> HITLDecision:
        """
        Return an explicit-approval decision.

        Args:
            tool_name:
                Requested tool.

        Returns:
            HITLDecision:
                Decision requiring explicit approval.
        """

        return HITLDecision(
            tool_name=tool_name,
            approval_level=ApprovalLevel.EXPLICIT_APPROVAL,
            auto_execute=False,
        )


def test_confirmation_creates_pending_approval_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Confirmation-required tools must create a pending request.
    """

    approval_service = ApprovalService()

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ConfirmationRequiredHITLGuardrail(),
    )

    monkeypatch.setattr(
        callback_module,
        "_APPROVAL_SERVICE",
        approval_service,
    )

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "approval_required"
    assert result["request_id"]
    assert result["approval_status"] == "PENDING"
    assert (
        result["approval_level"]
        == ApprovalLevel.CONFIRMATION.value
    )

    request = approval_service.get_request(
        result["request_id"]
    )

    assert request.status == ApprovalStatus.PENDING
    assert request.tool_name == "get_current_weather"
    assert request.arguments == {
        "city": "Delhi",
    }


def test_explicit_approval_creates_pending_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Explicit-approval operations must create pending requests.
    """

    approval_service = ApprovalService()

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ExplicitApprovalHITLGuardrail(),
    )

    monkeypatch.setattr(
        callback_module,
        "_APPROVAL_SERVICE",
        approval_service,
    )

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Mumbai",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None

    assert result["status"] == "approval_required"

    assert (
        result["approval_level"]
        == ApprovalLevel.EXPLICIT_APPROVAL.value
    )

    request = approval_service.get_request(
        result["request_id"]
    )

    assert request.status == ApprovalStatus.PENDING


def test_pending_request_can_be_approved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Callback-created requests must support approval.
    """

    approval_service = ApprovalService()

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ConfirmationRequiredHITLGuardrail(),
    )

    monkeypatch.setattr(
        callback_module,
        "_APPROVAL_SERVICE",
        approval_service,
    )

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    request = approval_service.approve(
        result["request_id"]
    )

    assert request.status == ApprovalStatus.APPROVED


def test_pending_request_can_be_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Callback-created requests must support rejection.
    """

    approval_service = ApprovalService()

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ConfirmationRequiredHITLGuardrail(),
    )

    monkeypatch.setattr(
        callback_module,
        "_APPROVAL_SERVICE",
        approval_service,
    )

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    request = approval_service.reject(
        result["request_id"]
    )

    assert request.status == ApprovalStatus.REJECTED


def test_auto_approved_weather_tool_creates_no_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Current AUTO tools must continue execution without HITL requests.
    """

    approval_service = ApprovalService()

    monkeypatch.setattr(
        callback_module,
        "_APPROVAL_SERVICE",
        approval_service,
    )

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_current_weather"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is None
    assert approval_service._requests == {}