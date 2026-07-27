"""
FastAPI routes for Human-in-the-Loop approval management.

Endpoints support:

- listing approval requests
- inspecting one approval request
- approving a pending request
- rejecting a pending request

Important:

This phase manages the approval lifecycle only.

Approval does not yet automatically resume or execute the blocked
Google ADK tool operation.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    get_approval_service,
)
from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalStatus,
)
from weather_intelligence_agent_v2.schemas.approval_schema import (
    ApprovalResponse,
)


router = APIRouter(
    prefix="/approvals",
    tags=[
        "HITL Approvals"
    ],
)


@router.get(
    "",
    response_model=list[
        ApprovalResponse
    ],
)
def list_approvals(
    approval_status: (
        ApprovalStatus
        | None
    ) = Query(
        default=None,
        alias="status",
    ),
) -> list[ApprovalResponse]:
    """
    List Human-in-the-Loop approval requests.

    Optional query:

        /approvals?status=PENDING

        /approvals?status=APPROVED

        /approvals?status=REJECTED
    """

    approval_service = (
        get_approval_service()
    )

    requests = (
        approval_service.list_requests(
            status=approval_status
        )
    )

    return [
        ApprovalResponse.from_domain(
            request
        )
        for request in requests
    ]


@router.get(
    "/{request_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    request_id: str,
) -> ApprovalResponse:
    """
    Retrieve a HITL approval request.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service.get_request(
                request_id
            )
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Approval request was "
                "not found."
            ),
        ) from exc

    return ApprovalResponse.from_domain(
        request
    )


@router.post(
    "/{request_id}/approve",
    response_model=ApprovalResponse,
)
def approve_request(
    request_id: str,
) -> ApprovalResponse:
    """
    Approve a pending HITL request.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service.approve(
                request_id
            )
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Approval request was "
                "not found."
            ),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Approval request has "
                "already been resolved."
            ),
        ) from exc

    return ApprovalResponse.from_domain(
        request
    )


@router.post(
    "/{request_id}/reject",
    response_model=ApprovalResponse,
)
def reject_request(
    request_id: str,
) -> ApprovalResponse:
    """
    Reject a pending HITL request.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service.reject(
                request_id
            )
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Approval request was "
                "not found."
            ),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Approval request has "
                "already been resolved."
            ),
        ) from exc

    return ApprovalResponse.from_domain(
        request
    )