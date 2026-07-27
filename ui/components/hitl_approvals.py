"""
Streamlit Human-in-the-Loop approval UI.

This component displays HITL approval requests created by the
FastAPI / Google ADK backend.

Responsibilities:

- retrieve pending approval requests
- display tool name and arguments
- display approval level
- allow human approval
- allow human rejection
- optionally display resolved approval history

Important:

The current backend manages approval state only.

Approving a request does not yet resume or execute the suspended
Google ADK tool call automatically.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from weather_intelligence_agent_v2.ui.api_client import (
    WeatherApiClient,
    WeatherApiError,
)


def _render_arguments(
    arguments: dict[
        str,
        Any,
    ],
) -> None:
    """
    Render tool arguments safely.
    """

    if not arguments:

        st.caption(
            "No tool arguments."
        )

        return

    st.json(
        arguments,
        expanded=False,
    )


def _render_approval_request(
    api_client: WeatherApiClient,
    approval: dict[
        str,
        Any,
    ],
) -> None:
    """
    Render one HITL approval request.
    """

    request_id = str(
        approval.get(
            "request_id",
            "",
        )
    )

    tool_name = str(
        approval.get(
            "tool_name",
            "Unknown tool",
        )
    )

    approval_level = str(
        approval.get(
            "approval_level",
            "Unknown",
        )
    )

    approval_status = str(
        approval.get(
            "status",
            "Unknown",
        )
    )

    arguments = approval.get(
        "arguments",
        {},
    )

    if not isinstance(
        arguments,
        dict,
    ):

        arguments = {}

    with st.container(
        border=True,
    ):

        st.markdown(
            f"#### 🔐 {tool_name}"
        )

        metadata_column_1, (
            metadata_column_2
        ) = st.columns(
            2
        )

        metadata_column_1.metric(
            "Approval Level",
            approval_level,
        )

        metadata_column_2.metric(
            "Status",
            approval_status,
        )

        st.markdown(
            "**Requested Arguments**"
        )

        _render_arguments(
            arguments
        )

        if (
            approval_status.upper()
            != "PENDING"
        ):

            if (
                approval_status.upper()
                == "APPROVED"
            ):

                st.success(
                    "Approved"
                )

            elif (
                approval_status.upper()
                == "REJECTED"
            ):

                st.error(
                    "Rejected"
                )

            return

        approve_column, (
            reject_column
        ) = st.columns(
            2
        )

        with approve_column:

            if st.button(
                "✅ Approve",
                key=(
                    f"approve_{request_id}"
                ),
                width="stretch",
                type="primary",
            ):

                try:

                    api_client.approve_request(
                        request_id
                    )

                    st.success(
                        (
                            "Approval request "
                            "approved."
                        )
                    )

                    st.rerun()

                except WeatherApiError as exc:

                    st.error(
                        str(
                            exc
                        )
                    )

        with reject_column:

            if st.button(
                "❌ Reject",
                key=(
                    f"reject_{request_id}"
                ),
                width="stretch",
            ):

                try:

                    api_client.reject_request(
                        request_id
                    )

                    st.warning(
                        (
                            "Approval request "
                            "rejected."
                        )
                    )

                    st.rerun()

                except WeatherApiError as exc:

                    st.error(
                        str(
                            exc
                        )
                    )


def render_hitl_approvals(
    api_client: WeatherApiClient,
) -> None:
    """
    Render Human-in-the-Loop approval panel.
    """

    st.divider()

    with st.expander(
        "🛡️ Human Approvals",
        expanded=False,
    ):

        st.caption(
            (
                "Sensitive tool operations that "
                "require human approval appear "
                "here."
            )
        )

        try:

            pending = (
                api_client.list_approvals(
                    status="PENDING"
                )
            )

        except WeatherApiError as exc:

            st.error(
                (
                    "Unable to retrieve HITL "
                    "approval requests."
                )
            )

            st.caption(
                str(
                    exc
                )
            )

            return

        if not pending:

            st.success(
                (
                    "No pending human "
                    "approvals."
                )
            )

            st.caption(
                (
                    "Current read-only weather "
                    "tools are configured for "
                    "automatic execution."
                )
            )

        else:

            st.warning(
                (
                    f"{len(pending)} approval "
                    "request(s) require human "
                    "attention."
                )
            )

            for approval in pending:

                _render_approval_request(
                    api_client,
                    approval,
                )

        show_history = st.toggle(
            "Show resolved approval history",
            value=False,
            key="show_hitl_history",
        )

        if show_history:

            try:

                all_requests = (
                    api_client.list_approvals()
                )

            except WeatherApiError as exc:

                st.error(
                    (
                        "Unable to retrieve "
                        "approval history."
                    )
                )

                st.caption(
                    str(
                        exc
                    )
                )

                return

            resolved_requests = [
                approval
                for approval in all_requests
                if str(
                    approval.get(
                        "status",
                        "",
                    )
                ).upper()
                != "PENDING"
            ]

            if not resolved_requests:

                st.info(
                    (
                        "No resolved approval "
                        "requests yet."
                    )
                )

            else:

                st.markdown(
                    "### Approval History"
                )

                for approval in (
                    resolved_requests
                ):

                    _render_approval_request(
                        api_client,
                        approval,
                    )

        st.info(
            (
                "Current HITL phase records "
                "approval decisions only. "
                "Approved tool execution is not "
                "automatically resumed yet."
            )
        )