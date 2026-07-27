"""
In-memory HITL approval service.

This service manages ApprovalRequest objects.

The implementation is intentionally lightweight for local
development and testing.

Responsibilities:

- create approval requests
- retrieve approval requests
- list approval requests
- approve requests
- reject requests
- emit Prometheus HITL metrics

A persistent implementation such as Redis or Firestore can later
replace this service without changing the approval domain model.
"""

from __future__ import annotations

from typing import Any

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalRequest,
    ApprovalStatus,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)
from weather_intelligence_agent_v2.observability.security_metrics import (
    HITL_APPROVAL_OUTCOMES_TOTAL,
    HITL_APPROVAL_REQUESTS_TOTAL,
)


class ApprovalService:
    """
    Manage Human-in-the-Loop approval requests.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory approval store.
        """

        self._requests: dict[
            str,
            ApprovalRequest,
        ] = {}

    @staticmethod
    def _approval_level_label(
        approval_level: ApprovalLevel,
    ) -> str:
        """
        Return stable metric label for approval level.
        """

        value = getattr(
            approval_level,
            "value",
            None,
        )

        if isinstance(
            value,
            str,
        ):
            return value

        return str(
            approval_level
        )

    def create_request(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        approval_level: ApprovalLevel,
    ) -> ApprovalRequest:
        """
        Create a new pending approval request.
        """

        request = ApprovalRequest(
            tool_name=tool_name,
            arguments=dict(
                arguments
            ),
            approval_level=(
                approval_level
            ),
        )

        self._requests[
            request.request_id
        ] = request

        HITL_APPROVAL_REQUESTS_TOTAL.labels(
            approval_level=(
                self._approval_level_label(
                    approval_level
                )
            ),
        ).inc()

        return request

    def get_request(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Retrieve an approval request.

        Raises:
            KeyError:
                If the request does not exist.
        """

        try:

            return self._requests[
                request_id
            ]

        except KeyError as exc:

            raise KeyError(
                "Approval request was not found."
            ) from exc

    def list_requests(
        self,
        status: ApprovalStatus | None = None,
    ) -> list[ApprovalRequest]:
        """
        List approval requests.

        Args:
            status:
                Optional status filter.

                Examples:

                PENDING
                APPROVED
                REJECTED

                None returns all requests.

        Returns:
            Approval requests ordered newest first.
        """

        requests = list(
            self._requests.values()
        )

        if status is not None:

            requests = [
                request
                for request in requests
                if request.status == status
            ]

        return sorted(
            requests,
            key=lambda request: (
                request.created_at
            ),
            reverse=True,
        )

    def approve(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Approve a pending request.
        """

        request = self.get_request(
            request_id
        )

        request.approve()

        HITL_APPROVAL_OUTCOMES_TOTAL.labels(
            status="approved",
        ).inc()

        return request

    def reject(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Reject a pending request.
        """

        request = self.get_request(
            request_id
        )

        request.reject()

        HITL_APPROVAL_OUTCOMES_TOTAL.labels(
            status="rejected",
        ).inc()

        return request