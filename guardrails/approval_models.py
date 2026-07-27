"""
Human-in-the-loop approval domain models.

These models represent both:

1. Human approval lifecycle
2. Post-approval tool execution lifecycle

Approval and execution are intentionally modeled separately.

Example:

PENDING
   ↓
APPROVED
   ↓
EXECUTED

or:

PENDING
   ↓
APPROVED
   ↓
EXECUTION_FAILED

A rejected request never executes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


class ApprovalStatus(
    str,
    Enum,
):
    """
    Human approval lifecycle.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalExecutionStatus(
    str,
    Enum,
):
    """
    Post-approval tool execution lifecycle.
    """

    NOT_STARTED = "NOT_STARTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


@dataclass
class ApprovalRequest:
    """
    Represent a HITL tool-execution request.
    """

    tool_name: str
    arguments: dict[str, Any]
    approval_level: ApprovalLevel

    request_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    status: ApprovalStatus = (
        ApprovalStatus.PENDING
    )

    created_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    resolved_at: (
        datetime
        | None
    ) = None

    execution_status: (
        ApprovalExecutionStatus
    ) = (
        ApprovalExecutionStatus
        .NOT_STARTED
    )

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

    def approve(
        self,
    ) -> None:
        """
        Approve pending request.
        """

        self._ensure_pending()

        self.status = (
            ApprovalStatus.APPROVED
        )

        self.resolved_at = (
            datetime.now(
                timezone.utc
            )
        )

    def reject(
        self,
    ) -> None:
        """
        Reject pending request.
        """

        self._ensure_pending()

        self.status = (
            ApprovalStatus.REJECTED
        )

        self.resolved_at = (
            datetime.now(
                timezone.utc
            )
        )

    def mark_execution_success(
        self,
        result: dict[
            str,
            Any,
        ],
    ) -> None:
        """
        Record successful approved-tool execution.
        """

        self._ensure_approved()

        self._ensure_not_executed()

        self.execution_status = (
            ApprovalExecutionStatus
            .EXECUTED
        )

        self.execution_result = dict(
            result
        )

        self.execution_error = None

        self.executed_at = (
            datetime.now(
                timezone.utc
            )
        )

    def mark_execution_failure(
        self,
        message: str,
    ) -> None:
        """
        Record failed approved-tool execution.
        """

        self._ensure_approved()

        self._ensure_not_executed()

        self.execution_status = (
            ApprovalExecutionStatus
            .FAILED
        )

        self.execution_error = (
            message
        )

        self.execution_result = None

        self.executed_at = (
            datetime.now(
                timezone.utc
            )
        )

    def _ensure_pending(
        self,
    ) -> None:
        """
        Ensure human decision has not already occurred.
        """

        if (
            self.status
            != ApprovalStatus.PENDING
        ):

            raise ValueError(
                (
                    "Approval request has "
                    "already been resolved."
                )
            )

    def _ensure_approved(
        self,
    ) -> None:
        """
        Ensure execution only follows approval.
        """

        if (
            self.status
            != ApprovalStatus.APPROVED
        ):

            raise ValueError(
                (
                    "Tool execution requires "
                    "an approved request."
                )
            )

    def _ensure_not_executed(
        self,
    ) -> None:
        """
        Prevent duplicate tool execution.
        """

        if (
            self.execution_status
            != ApprovalExecutionStatus
            .NOT_STARTED
        ):

            raise ValueError(
                (
                    "Approved tool execution "
                    "has already been attempted."
                )
            )