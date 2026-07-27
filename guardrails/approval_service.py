"""
In-memory HITL approval service.

Responsibilities:

- create requests
- retrieve requests
- list requests
- approve requests
- reject requests
- record approved-tool execution
- emit approval metrics

The storage implementation is currently process-local.

Redis, Firestore, Cloud SQL, or another persistent backend can replace
this implementation later.
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

    def __init__(
        self,
    ) -> None:

        self._requests: dict[
            str,
            ApprovalRequest,
        ] = {}

    @staticmethod
    def _approval_level_label(
        approval_level: ApprovalLevel,
    ) -> str:

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
        Create pending approval request.
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
        Retrieve request.
        """

        try:

            return self._requests[
                request_id
            ]

        except KeyError as exc:

            raise KeyError(
                (
                    "Approval request was "
                    "not found."
                )
            ) from exc

    def list_requests(
        self,
        status: (
            ApprovalStatus
            | None
        ) = None,
    ) -> list[
        ApprovalRequest
    ]:
        """
        List requests newest first.
        """

        requests = list(
            self._requests.values()
        )

        if status is not None:

            requests = [
                request
                for request
                in requests
                if request.status
                == status
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
        Approve request.

        Execution remains a separate operation.
        """

        request = (
            self.get_request(
                request_id
            )
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
        Reject request.
        """

        request = (
            self.get_request(
                request_id
            )
        )

        request.reject()

        HITL_APPROVAL_OUTCOMES_TOTAL.labels(
            status="rejected",
        ).inc()

        return request