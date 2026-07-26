"""
Integration tests for HITL enforcement inside the ADK tool callback.

These tests verify that:

1. Current read-only weather tools continue to execute automatically.
2. Invalid tools are still blocked by Phase 9.4.
3. A tool requiring human confirmation is not automatically executed.
4. A missing HITL policy fails closed.

Gemini and external weather APIs are not called.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from weather_intelligence_agent_v2.guardrails import (
    adk_tool_guardrail_callback as callback_module,
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
    Minimal ADK-compatible tool test double.

    Attributes:
        name:
            Tool identifier supplied to the callback.
    """

    name: str


class FakeToolContext:
    """
    Minimal ToolContext-compatible test double.
    """


class ConfirmationRequiredHITLGuardrail:
    """
    Test double that requires user confirmation.
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
            HITLDecision requiring confirmation.
        """

        return HITLDecision(
            tool_name=tool_name,
            approval_level=ApprovalLevel.CONFIRMATION,
            auto_execute=False,
        )


class ExplicitApprovalHITLGuardrail:
    """
    Test double requiring explicit human approval.
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
            HITLDecision requiring explicit approval.
        """

        return HITLDecision(
            tool_name=tool_name,
            approval_level=ApprovalLevel.EXPLICIT_APPROVAL,
            auto_execute=False,
        )


class MissingPolicyHITLGuardrail:
    """
    Test double representing missing HITL configuration.
    """

    def evaluate(
        self,
        tool_name: str,
    ) -> HITLDecision:
        """
        Simulate an absent approval policy.

        Args:
            tool_name:
                Requested tool.

        Raises:
            ValueError:
                Always raised to simulate missing configuration.
        """

        del tool_name

        raise ValueError(
            "Missing HITL policy."
        )


def test_current_weather_remains_auto_executable() -> None:
    """
    Current-weather lookup must continue executing automatically.
    """

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


def test_forecast_remains_auto_executable() -> None:
    """
    Forecast lookup must continue executing automatically.
    """

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="get_forecast"
        ),
        args={
            "city": "Mumbai",
        },
        tool_context=FakeToolContext(),
    )

    assert result is None


def test_weather_analysis_remains_auto_executable() -> None:
    """
    Multi-city analytics must remain automatically executable.
    """

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="analyze_weather"
        ),
        args={
            "cities": [
                "Delhi",
                "Mumbai",
            ],
        },
        tool_context=FakeToolContext(),
    )

    assert result is None


def test_invalid_tool_is_still_blocked_before_hitl() -> None:
    """
    Tool security validation must occur before HITL evaluation.
    """

    result = callback_module.weather_before_tool_callback(
        tool=FakeTool(
            name="execute_shell_command"
        ),
        args={
            "city": "Delhi",
        },
        tool_context=FakeToolContext(),
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["error_code"] == "TOOL_NOT_ALLOWED"


def test_confirmation_required_tool_does_not_auto_execute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Confirmation-level operations must not execute automatically.
    """

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ConfirmationRequiredHITLGuardrail(),
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

    assert (
        result["error_code"]
        == "HITL_APPROVAL_REQUIRED"
    )

    assert (
        result["approval_level"]
        == ApprovalLevel.CONFIRMATION.value
    )


def test_explicit_approval_tool_does_not_auto_execute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    High-impact operations must stop pending explicit approval.
    """

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        ExplicitApprovalHITLGuardrail(),
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

    assert (
        result["approval_level"]
        == ApprovalLevel.EXPLICIT_APPROVAL.value
    )


def test_missing_hitl_policy_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Missing approval configuration must never result in execution.
    """

    monkeypatch.setattr(
        callback_module,
        "_HITL_GUARDRAIL",
        MissingPolicyHITLGuardrail(),
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

    assert result["status"] == "blocked"

    assert (
        result["error_code"]
        == "HITL_POLICY_NOT_FOUND"
    )