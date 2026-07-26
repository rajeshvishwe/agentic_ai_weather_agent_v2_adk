"""
In-memory HITL approval service.

This service manages ApprovalRequest objects for Phase 9.5.

The in-memory implementation is intentionally simple and suitable for
local development and testing.

A distributed persistence layer can later replace this implementation
without changing the approval domain model.
"""

from __future__ import annotations

from typing import Any

from weather_intelligence_agent_v2.guardrails.approval_models import (
    ApprovalRequest,
)
from weather_intelligence_agent_v2.guardrails.config.hitl_policy import (
    ApprovalLevel,
)


class ApprovalService:
    """
    Manage human approval requests.

    The service currently stores requests in application memory.

    It supports:

    - creating approval requests
    - retrieving requests
    - approving requests
    - rejecting requests
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory approval store.
        """

        self._requests: dict[str, ApprovalRequest] = {}

    def create_request(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        approval_level: ApprovalLevel,
    ) -> ApprovalRequest:
        """
        Create a pending approval request.

        Args:
            tool_name:
                Tool awaiting approval.

            arguments:
                Tool execution arguments.

            approval_level:
                Required approval level.

        Returns:
            ApprovalRequest:
                Newly created pending request.
        """

        request = ApprovalRequest(
            tool_name=tool_name,
            arguments=dict(arguments),
            approval_level=approval_level,
        )

        self._requests[request.request_id] = request

        return request

    def get_request(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Retrieve an approval request.

        Args:
            request_id:
                Unique request identifier.

        Returns:
            ApprovalRequest:
                Matching approval request.

        Raises:
            KeyError:
                If the request does not exist.
        """

        try:
            return self._requests[request_id]
        except KeyError as exc:
            raise KeyError(
                "Approval request was not found."
            ) from exc

    def approve(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Approve a pending request.

        Args:
            request_id:
                Request identifier.

        Returns:
            ApprovalRequest:
                Updated approved request.
        """

        request = self.get_request(
            request_id
        )

        request.approve()

        return request

    def reject(
        self,
        request_id: str,
    ) -> ApprovalRequest:
        """
        Reject a pending request.

        Args:
            request_id:
                Request identifier.

        Returns:
            ApprovalRequest:
                Updated rejected request.
        """

        request = self.get_request(
            request_id
        )

        request.reject()

        return request