"""
FastAPI routes for Human-in-the-Loop approval management.

These endpoints allow a human operator to:

- inspect a pending approval request
- approve a request
- reject a request

This module does not execute approved tools yet. It manages only the
approval lifecycle.

Tool resumption/execution will be introduced in a later HITL phase.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    get_approval_service,
)
from weather_intelligence_agent_v2.schemas.approval_schema import (
    ApprovalResponse,
)


router = APIRouter(
    prefix="/approvals",
    tags=["HITL Approvals"],
)


@router.get(
    "/{request_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    request_id: str,
) -> ApprovalResponse:
    """
    Retrieve a HITL approval request.

    Args:
        request_id:
            Unique approval request identifier.

    Returns:
        ApprovalResponse:
            Current approval request state.

    Raises:
        HTTPException:
            If the approval request does not exist.
    """

    approval_service = get_approval_service()

    try:
        request = approval_service.get_request(
            request_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request was not found.",
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

    Args:
        request_id:
            Unique approval request identifier.

    Returns:
        ApprovalResponse:
            Updated approved request.

    Raises:
        HTTPException:
            If the request does not exist or has already been resolved.
    """

    approval_service = get_approval_service()

    try:
        request = approval_service.approve(
            request_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request was not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval request has already been resolved.",
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

    Args:
        request_id:
            Unique approval request identifier.

    Returns:
        ApprovalResponse:
            Updated rejected request.

    Raises:
        HTTPException:
            If the request does not exist or has already been resolved.
    """

    approval_service = get_approval_service()

    try:
        request = approval_service.reject(
            request_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request was not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval request has already been resolved.",
        ) from exc

    return ApprovalResponse.from_domain(
        request
    )