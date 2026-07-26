"""
Production FastAPI integration tests for HITL approval routes.

These tests verify that Phase 9.5 approval endpoints are registered
with the real Weather Intelligence FastAPI application.

No Gemini calls or external weather API calls are required.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from weather_intelligence_agent_v2.api.app import app
from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    get_approval_service,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


def test_approval_route_is_registered_in_application() -> None:
    """
    Pending approvals must be retrievable through the production app.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Delhi",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    with TestClient(app) as client:
        response = client.get(
            f"/approvals/{request.request_id}"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["request_id"] == request.request_id
    assert payload["status"] == "PENDING"


def test_approval_route_can_approve_request() -> None:
    """
    Production approval endpoint must approve pending requests.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Mumbai",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    with TestClient(app) as client:
        response = client.post(
            f"/approvals/{request.request_id}/approve"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "APPROVED"
    assert payload["resolved_at"] is not None


def test_approval_route_can_reject_request() -> None:
    """
    Production approval endpoint must reject pending requests.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.EXPLICIT_APPROVAL,
    )

    with TestClient(app) as client:
        response = client.post(
            f"/approvals/{request.request_id}/reject"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "REJECTED"


def test_unknown_approval_returns_404_from_application() -> None:
    """
    Unknown approval requests must return HTTP 404.
    """

    with TestClient(app) as client:
        response = client.get(
            "/approvals/not-a-real-request"
        )

    assert response.status_code == 404


def test_existing_health_endpoint_still_works() -> None:
    """
    HITL router registration must not break existing API behavior.
    """

    with TestClient(app) as client:
        response = client.get(
            "/health"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "UP"