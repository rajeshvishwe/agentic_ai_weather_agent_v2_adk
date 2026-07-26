"""
Human-in-the-loop approval domain models.

These models represent the lifecycle of tool-execution approval requests.

The implementation is framework-independent so approval state can later
be stored in memory, Redis, Firestore, or another persistent backend.
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


class ApprovalStatus(str, Enum):
    """
    Lifecycle status of a human approval request.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ApprovalRequest:
    """
    Represent a tool execution awaiting human approval.

    Attributes:
        request_id:
            Unique approval request identifier.

        tool_name:
            Tool requesting execution.

        arguments:
            Tool arguments requiring approval.

        approval_level:
            Required approval level.

        status:
            Current approval lifecycle state.

        created_at:
            UTC timestamp when the request was created.

        resolved_at:
            UTC timestamp when approved or rejected.
    """

    tool_name: str
    arguments: dict[str, Any]
    approval_level: ApprovalLevel

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: ApprovalStatus = ApprovalStatus.PENDING

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    resolved_at: datetime | None = None

    def approve(self) -> None:
        """
        Mark the request as approved.

        Raises:
            ValueError:
                If the request has already been resolved.
        """

        self._ensure_pending()

        self.status = ApprovalStatus.APPROVED
        self.resolved_at = datetime.now(timezone.utc)

    def reject(self) -> None:
        """
        Mark the request as rejected.

        Raises:
            ValueError:
                If the request has already been resolved.
        """

        self._ensure_pending()

        self.status = ApprovalStatus.REJECTED
        self.resolved_at = datetime.now(timezone.utc)

    def _ensure_pending(self) -> None:
        """
        Ensure the request has not already been resolved.

        Raises:
            ValueError:
                If the request is already approved or rejected.
        """

        if self.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Approval request has already been resolved."
            )