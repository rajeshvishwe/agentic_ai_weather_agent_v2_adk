"""
Pydantic schemas for Human-in-the-Loop approval APIs.

These schemas expose approval state through the FastAPI boundary
without leaking internal implementation details.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalRequest,
)


class ApprovalResponse(BaseModel):
    """
    Public API representation of a HITL approval request.

    Attributes:
        request_id:
            Unique approval request identifier.

        tool_name:
            Tool awaiting approval.

        arguments:
            Arguments associated with the requested tool execution.

        approval_level:
            Required human approval level.

        status:
            Current approval lifecycle status.

        created_at:
            UTC creation timestamp.

        resolved_at:
            UTC resolution timestamp when approved or rejected.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    request_id: str
    tool_name: str
    arguments: dict[str, Any]
    approval_level: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None

    @classmethod
    def from_domain(
        cls,
        request: ApprovalRequest,
    ) -> "ApprovalResponse":
        """
        Convert an ApprovalRequest domain object into an API response.

        Args:
            request:
                Approval domain object.

        Returns:
            ApprovalResponse:
                Public API representation.
        """

        return cls(
            request_id=request.request_id,
            tool_name=request.tool_name,
            arguments=dict(request.arguments),
            approval_level=request.approval_level.value,
            status=request.status.value,
            created_at=request.created_at,
            resolved_at=request.resolved_at,
        )