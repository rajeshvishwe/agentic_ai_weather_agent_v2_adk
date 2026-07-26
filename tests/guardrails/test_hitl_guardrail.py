"""
Unit tests for Phase 9.5 Human-in-the-Loop policy.
"""

from __future__ import annotations

import pytest

from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)
from weather_intelligence_agent_v2.guardrails.hitl_guardrail import (
    HITLGuardrail,
)


def test_current_weather_is_auto_approved() -> None:
    """Current-weather lookup must execute automatically."""

    guardrail = HITLGuardrail()

    decision = guardrail.evaluate(
        "get_current_weather"
    )

    assert decision.approval_level == ApprovalLevel.AUTO
    assert decision.auto_execute is True


def test_forecast_is_auto_approved() -> None:
    """Forecast lookup must execute automatically."""

    guardrail = HITLGuardrail()

    decision = guardrail.evaluate(
        "get_forecast"
    )

    assert decision.approval_level == ApprovalLevel.AUTO
    assert decision.auto_execute is True


def test_weather_analysis_is_auto_approved() -> None:
    """Weather analytics must execute automatically."""

    guardrail = HITLGuardrail()

    decision = guardrail.evaluate(
        "analyze_weather"
    )

    assert decision.approval_level == ApprovalLevel.AUTO
    assert decision.auto_execute is True


def test_weather_intelligence_is_auto_approved() -> None:
    """Weather intelligence must execute automatically."""

    guardrail = HITLGuardrail()

    decision = guardrail.evaluate(
        "get_weather_intelligence"
    )

    assert decision.approval_level == ApprovalLevel.AUTO
    assert decision.auto_execute is True


def test_weather_plan_is_auto_approved() -> None:
    """Weather planning must execute automatically."""

    guardrail = HITLGuardrail()

    decision = guardrail.evaluate(
        "get_weather_plan"
    )

    assert decision.approval_level == ApprovalLevel.AUTO
    assert decision.auto_execute is True


def test_unknown_tool_fails_closed() -> None:
    """Unknown tools must not receive implicit approval."""

    guardrail = HITLGuardrail()

    with pytest.raises(ValueError):
        guardrail.evaluate(
            "unknown_tool"
        )