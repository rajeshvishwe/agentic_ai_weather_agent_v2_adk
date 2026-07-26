"""
API tests for Human-in-the-Loop approval routes.

The approval router is tested in isolation before it is registered with
the production Weather Intelligence FastAPI application.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from weather_intelligence_agent_v2.api.approval_routes import (
    router,
)
from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    get_approval_service,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


def _build_test_client() -> TestClient:
    """
    Create an isolated FastAPI application for approval-route testing.

    Returns:
        TestClient:
            FastAPI test client containing only the approval router.
    """

    app = FastAPI()

    app.include_router(
        router
    )

    return TestClient(
        app
    )


def test_get_pending_approval_request() -> None:
    """
    A pending approval request must be retrievable through the API.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Delhi",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    with _build_test_client() as client:
        response = client.get(
            f"/approvals/{request.request_id}"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["request_id"] == request.request_id
    assert payload["tool_name"] == "future_side_effect_tool"
    assert payload["status"] == "PENDING"
    assert payload["approval_level"] == "CONFIRMATION"


def test_approve_pending_request() -> None:
    """
    A pending request must be approvable through the API.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={
            "city": "Mumbai",
        },
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    with _build_test_client() as client:
        response = client.post(
            f"/approvals/{request.request_id}/approve"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "APPROVED"
    assert payload["resolved_at"] is not None


def test_reject_pending_request() -> None:
    """
    A pending request must be rejectable through the API.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.EXPLICIT_APPROVAL,
    )

    with _build_test_client() as client:
        response = client.post(
            f"/approvals/{request.request_id}/reject"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "REJECTED"
    assert payload["resolved_at"] is not None


def test_missing_approval_returns_404() -> None:
    """
    Unknown approval identifiers must return HTTP 404.
    """

    with _build_test_client() as client:
        response = client.get(
            "/approvals/not-a-real-request"
        )

    assert response.status_code == 404


def test_approve_missing_request_returns_404() -> None:
    """
    Approving an unknown request must return HTTP 404.
    """

    with _build_test_client() as client:
        response = client.post(
            "/approvals/not-a-real-request/approve"
        )

    assert response.status_code == 404


def test_reject_missing_request_returns_404() -> None:
    """
    Rejecting an unknown request must return HTTP 404.
    """

    with _build_test_client() as client:
        response = client.post(
            "/approvals/not-a-real-request/reject"
        )

    assert response.status_code == 404


def test_resolved_request_cannot_be_approved_twice() -> None:
    """
    Resolving the same request twice must return HTTP 409.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    approval_service.approve(
        request.request_id
    )

    with _build_test_client() as client:
        response = client.post(
            f"/approvals/{request.request_id}/approve"
        )

    assert response.status_code == 409


def test_rejected_request_cannot_be_approved() -> None:
    """
    A rejected request must not later become approved.
    """

    approval_service = get_approval_service()

    request = approval_service.create_request(
        tool_name="future_side_effect_tool",
        arguments={},
        approval_level=ApprovalLevel.CONFIRMATION,
    )

    approval_service.reject(
        request.request_id
    )

    with _build_test_client() as client:
        response = client.post(
            f"/approvals/{request.request_id}/approve"
        )

    assert response.status_code == 409