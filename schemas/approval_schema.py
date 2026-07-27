"""
Pydantic schemas for HITL approval APIs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
)

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalRequest,
)


class ApprovalResponse(
    BaseModel
):
    """
    Public HITL request representation.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    request_id: str

    tool_name: str

    arguments: dict[
        str,
        Any,
    ]

    approval_level: str

    status: str

    created_at: datetime

    resolved_at: (
        datetime
        | None
    ) = None

    execution_status: str

    executed_at: (
        datetime
        | None
    ) = None

    execution_result: (
        dict[str, Any]
        | None
    ) = None

    execution_error: (
        str
        | None
    ) = None

    @classmethod
    def from_domain(
        cls,
        request: ApprovalRequest,
    ) -> "ApprovalResponse":
        """
        Convert domain request to API response.
        """

        return cls(
            request_id=(
                request.request_id
            ),
            tool_name=(
                request.tool_name
            ),
            arguments=dict(
                request.arguments
            ),
            approval_level=(
                request.approval_level
                .value
            ),
            status=(
                request.status.value
            ),
            created_at=(
                request.created_at
            ),
            resolved_at=(
                request.resolved_at
            ),
            execution_status=(
                request.execution_status
                .value
            ),
            executed_at=(
                request.executed_at
            ),
            execution_result=(
                dict(
                    request.execution_result
                )
                if (
                    request.execution_result
                    is not None
                )
                else None
            ),
            execution_error=(
                request.execution_error
            ),
        )