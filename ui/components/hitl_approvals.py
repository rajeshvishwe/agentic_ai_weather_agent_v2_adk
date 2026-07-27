"""
Streamlit Human-in-the-Loop approval UI.

This component provides the presentation layer for HITL approval
requests created by the Weather Intelligence backend.

Responsibilities:

- retrieve pending approval requests
- display tool details and arguments
- approve and execute approved actions
- reject pending actions
- display execution status
- display execution result
- append approval/execution outcomes to the visible chat history
- display resolved approval history

Important:

This phase provides Streamlit conversation continuation.

It does not yet inject the post-approval execution result back into
the Google ADK session/event stream.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from weather_intelligence_agent_v2.ui.api_client import (
    WeatherApiClient,
    WeatherApiError,
)


# ============================================================
# CHAT HELPERS
# ============================================================


def _append_assistant_message(
    message: str,
) -> None:
    """
    Append one assistant message to visible Streamlit chat history.

    Duplicate consecutive messages are avoided because Streamlit
    reruns frequently.

    Args:
        message:
            Assistant message to append.
    """

    normalized_message = (
        message.strip()
    )

    if not normalized_message:
        return

    messages = (
        st.session_state
        .chat_messages
    )

    if messages:

        last_message = (
            messages[-1]
        )

        if (
            last_message.get("role")
            == "assistant"
            and last_message.get(
                "content"
            )
            == normalized_message
        ):

            return

    messages.append(
        {
            "role": "assistant",
            "content": (
                normalized_message
            ),
        }
    )


def _build_execution_message(
    approval: dict[
        str,
        Any,
    ],
) -> str:
    """
    Build user-facing assistant confirmation after execution.

    Args:
        approval:
            Approval API response.

    Returns:
        Natural-language assistant confirmation.
    """

    tool_name = str(
        approval.get(
            "tool_name",
            "",
        )
    )

    execution_status = str(
        approval.get(
            "execution_status",
            "NOT_STARTED",
        )
    ).upper()

    execution_result = (
        approval.get(
            "execution_result"
        )
    )

    # --------------------------------------------------------
    # Weather reminder success
    # --------------------------------------------------------

    if (
        tool_name
        == "create_weather_reminder"
        and execution_status
        == "EXECUTED"
        and isinstance(
            execution_result,
            dict,
        )
    ):

        city = str(
            execution_result.get(
                "city",
                "",
            )
        ).strip()

        reminder_time = str(
            execution_result.get(
                "reminder_time",
                "",
            )
        ).strip()

        reminder_message = str(
            execution_result.get(
                "message",
                "",
            )
        ).strip()

        parts: list[str] = [
            "✅ Your weather reminder"
        ]

        if city:

            parts.append(
                f"for **{city}**"
            )

        if reminder_time:

            parts.append(
                f"for **{reminder_time}**"
            )

        confirmation = (
            " ".join(
                parts
            )
            + " has been created successfully."
        )

        if reminder_message:

            confirmation += (
                "\n\n"
                f"**Reminder:** "
                f"{reminder_message}"
            )

        return confirmation

    # --------------------------------------------------------
    # Generic execution success
    # --------------------------------------------------------

    if (
        execution_status
        == "EXECUTED"
    ):

        return (
            "✅ The approved action was "
            "executed successfully."
        )

    # --------------------------------------------------------
    # Execution failure
    # --------------------------------------------------------

    if (
        execution_status
        == "FAILED"
    ):

        return (
            "⚠️ Human approval was granted, "
            "but the requested action could "
            "not be executed successfully."
        )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return (
        "✅ Human approval was recorded."
    )


def _build_rejection_message(
    approval: dict[
        str,
        Any,
    ],
) -> str:
    """
    Build conversational rejection message.

    Args:
        approval:
            Rejected approval response.

    Returns:
        User-facing rejection message.
    """

    tool_name = str(
        approval.get(
            "tool_name",
            "",
        )
    )

    if (
        tool_name
        == "create_weather_reminder"
    ):

        return (
            "❌ The weather reminder request "
            "was rejected and was not executed."
        )

    return (
        "❌ The requested action was rejected "
        "and was not executed."
    )


# ============================================================
# PRESENTATION HELPERS
# ============================================================


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


def _render_execution(
    approval: dict[
        str,
        Any,
    ],
) -> None:
    """
    Render post-approval execution state.
    """

    execution_status = str(
        approval.get(
            "execution_status",
            "NOT_STARTED",
        )
    ).upper()

    # --------------------------------------------------------
    # Successful execution
    # --------------------------------------------------------

    if (
        execution_status
        == "EXECUTED"
    ):

        st.success(
            (
                "✅ Approved tool executed "
                "successfully."
            )
        )

        result = approval.get(
            "execution_result"
        )

        if isinstance(
            result,
            dict,
        ):

            st.markdown(
                "**Execution Result**"
            )

            st.json(
                result,
                expanded=False,
            )

        return

    # --------------------------------------------------------
    # Failed execution
    # --------------------------------------------------------

    if (
        execution_status
        == "FAILED"
    ):

        st.error(
            (
                "Approved tool execution "
                "failed."
            )
        )

        execution_error = (
            approval.get(
                "execution_error"
            )
        )

        if execution_error:

            st.caption(
                str(
                    execution_error
                )
            )

        return

    # --------------------------------------------------------
    # Not executed
    # --------------------------------------------------------

    st.caption(
        "Execution has not started."
    )


# ============================================================
# APPROVAL REQUEST
# ============================================================


def _render_approval_request(
    api_client: WeatherApiClient,
    approval: dict[
        str,
        Any,
    ],
) -> None:
    """
    Render one approval request.

    Pending requests provide:

    - Approve & Execute
    - Reject

    Resolved requests display their final state.
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
    ).upper()

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

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        st.markdown(
            f"#### 🔐 {tool_name}"
        )

        column_1, column_2 = (
            st.columns(
                2
            )
        )

        column_1.metric(
            "Approval Level",
            approval_level,
        )

        column_2.metric(
            "Approval Status",
            approval_status,
        )

        # ----------------------------------------------------
        # Arguments
        # ----------------------------------------------------

        st.markdown(
            "**Requested Arguments**"
        )

        _render_arguments(
            arguments
        )

        # ====================================================
        # PENDING
        # ====================================================

        if (
            approval_status
            == "PENDING"
        ):

            approve_column, (
                reject_column
            ) = st.columns(
                2
            )

            # ------------------------------------------------
            # APPROVE + EXECUTE
            # ------------------------------------------------

            with approve_column:

                if st.button(
                    "✅ Approve & Execute",
                    key=(
                        f"approve_{request_id}"
                    ),
                    width="stretch",
                    type="primary",
                ):

                    try:

                        updated_approval = (
                            api_client
                            .approve_request(
                                request_id
                            )
                        )

                        chat_message = (
                            _build_execution_message(
                                updated_approval
                            )
                        )

                        _append_assistant_message(
                            chat_message
                        )

                        st.rerun()

                    except WeatherApiError as exc:

                        st.error(
                            str(
                                exc
                            )
                        )

            # ------------------------------------------------
            # REJECT
            # ------------------------------------------------

            with reject_column:

                if st.button(
                    "❌ Reject",
                    key=(
                        f"reject_{request_id}"
                    ),
                    width="stretch",
                ):

                    try:

                        updated_approval = (
                            api_client
                            .reject_request(
                                request_id
                            )
                        )

                        chat_message = (
                            _build_rejection_message(
                                updated_approval
                            )
                        )

                        _append_assistant_message(
                            chat_message
                        )

                        st.rerun()

                    except WeatherApiError as exc:

                        st.error(
                            str(
                                exc
                            )
                        )

            return

        # ====================================================
        # REJECTED
        # ====================================================

        if (
            approval_status
            == "REJECTED"
        ):

            st.warning(
                (
                    "❌ Request rejected. "
                    "Tool was not executed."
                )
            )

            return

        # ====================================================
        # APPROVED
        # ====================================================

        if (
            approval_status
            == "APPROVED"
        ):

            st.success(
                "Human approval granted."
            )

            _render_execution(
                approval
            )


# ============================================================
# MAIN HITL COMPONENT
# ============================================================


def render_hitl_approvals(
    api_client: WeatherApiClient,
) -> None:
    """
    Render the complete Human-in-the-Loop panel.

    Pending approval requests are displayed first.

    Resolved approval history is available through an optional
    toggle.
    """

    st.divider()

    with st.expander(
        "🛡️ Human Approvals",
        expanded=False,
    ):

        st.caption(
            (
                "Sensitive agent actions require "
                "human confirmation before "
                "execution."
            )
        )

        # ----------------------------------------------------
        # Pending approvals
        # ----------------------------------------------------

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

        else:

            st.warning(
                (
                    f"{len(pending)} request(s) "
                    "require human attention."
                )
            )

            for approval in pending:

                _render_approval_request(
                    api_client,
                    approval,
                )

        # ----------------------------------------------------
        # Approval history
        # ----------------------------------------------------

        show_history = st.toggle(
            (
                "Show resolved approval "
                "history"
            ),
            value=False,
            key="show_hitl_history",
        )

        if not show_history:

            return

        try:

            all_requests = (
                api_client.list_approvals()
            )

        except WeatherApiError as exc:

            st.error(
                str(
                    exc
                )
            )

            return

        resolved = [
            approval
            for approval
            in all_requests
            if str(
                approval.get(
                    "status",
                    "",
                )
            ).upper()
            != "PENDING"
        ]

        if not resolved:

            st.info(
                (
                    "No resolved approval "
                    "requests yet."
                )
            )

            return

        st.markdown(
            "### Approval History"
        )

        for approval in resolved:

            _render_approval_request(
                api_client,
                approval,
            )