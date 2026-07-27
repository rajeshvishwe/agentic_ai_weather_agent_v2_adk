"""
FastAPI routes for Human-in-the-Loop approval management.

Approval flow:

PENDING
    ↓
Approve
    ↓
Security revalidation
    ↓
ApprovedToolExecutor
    ↓
EXECUTED / FAILED

Rejected requests never execute.
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
from weather_intelligence_agent_v2.services.approved_tool_executor import (
    ApprovedToolExecutor,
)


router = APIRouter(
    prefix="/approvals",
    tags=[
        "HITL Approvals"
    ],
)


_APPROVED_TOOL_EXECUTOR = (
    ApprovedToolExecutor()
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
) -> list[
    ApprovalResponse
]:
    """
    List approval requests.
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
        for request
        in requests
    ]


@router.get(
    "/{request_id}",
    response_model=(
        ApprovalResponse
    ),
)
def get_approval(
    request_id: str,
) -> ApprovalResponse:
    """
    Retrieve approval request.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service
            .get_request(
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

    return (
        ApprovalResponse
        .from_domain(
            request
        )
    )


@router.post(
    "/{request_id}/approve",
    response_model=(
        ApprovalResponse
    ),
)
def approve_request(
    request_id: str,
) -> ApprovalResponse:
    """
    Approve and execute one HITL request.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service
            .approve(
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

    # ----------------------------------------------------------
    # Execute only AFTER successful human approval.
    # ----------------------------------------------------------

    try:

        execution_result = (
            _APPROVED_TOOL_EXECUTOR
            .execute(
                request
            )
        )

        request.mark_execution_success(
            execution_result
        )

    except Exception:

        request.mark_execution_failure(
            (
                "Approved tool execution "
                "failed."
            )
        )

    return (
        ApprovalResponse
        .from_domain(
            request
        )
    )


@router.post(
    "/{request_id}/reject",
    response_model=(
        ApprovalResponse
    ),
)
def reject_request(
    request_id: str,
) -> ApprovalResponse:
    """
    Reject request.

    Rejection never executes the tool.
    """

    approval_service = (
        get_approval_service()
    )

    try:

        request = (
            approval_service
            .reject(
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

    return (
        ApprovalResponse
        .from_domain(
            request
        )
    )