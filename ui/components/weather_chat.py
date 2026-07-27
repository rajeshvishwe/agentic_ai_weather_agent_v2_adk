"""
Conversational weather assistant UI.

This module is presentation-only.

It renders:

- assistant landing state
- starter prompts
- conversation history
- chat input
- loading feedback
- API errors
- Human-in-the-Loop approval panel

All weather, Google ADK, guardrail, and approval functionality
remains in the FastAPI backend.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from weather_intelligence_agent_v2.ui.api_client import (
    WeatherApiClient,
    WeatherApiConnectionError,
    WeatherApiError,
    WeatherApiResponseError,
    WeatherApiTimeoutError,
)
from weather_intelligence_agent_v2.ui.components.hitl_approvals import (
    render_hitl_approvals,
)


STARTER_PROMPTS: tuple[
    tuple[str, str],
    ...,
] = (
    (
        "🌤️ Current Weather",
        (
            "What is the current weather "
            "in Delhi?"
        ),
    ),
    (
        "📅 7-Day Forecast",
        (
            "Give me the 7-day forecast "
            "for Mumbai."
        ),
    ),
    (
        "🌍 Compare Cities",
        (
            "Compare the weather in "
            "Delhi and London."
        ),
    ),
    (
        "🚶 Outdoor Planning",
        (
            "Is it a good day for outdoor "
            "activities in Bengaluru?"
        ),
    ),
)


def render_welcome() -> None:
    """
    Render assistant landing content.
    """

    if (
        st.session_state.chat_messages
    ):

        return

    st.markdown(
        (
            "### 👋 How can I help "
            "with the weather?"
        )
    )

    st.caption(
        (
            "Ask about current conditions, "
            "forecasts, city comparisons, "
            "risks, or outdoor plans."
        )
    )


def render_starter_prompts(
) -> Optional[str]:
    """
    Render starter-question buttons.
    """

    if (
        st.session_state.chat_messages
    ):

        return None

    st.write("")

    columns = st.columns(
        2,
        gap="small",
    )

    selected_prompt: (
        Optional[str]
    ) = None

    for index, (
        label,
        prompt,
    ) in enumerate(
        STARTER_PROMPTS
    ):

        with columns[
            index % 2
        ]:

            if st.button(
                label,
                key=(
                    "starter_prompt_"
                    f"{index}"
                ),
                help=prompt,
                width="stretch",
            ):

                selected_prompt = (
                    prompt
                )

    return selected_prompt


def render_chat_history() -> None:
    """
    Render conversation history.
    """

    for message in (
        st.session_state.chat_messages
    ):

        role = message.get(
            "role",
            "assistant",
        )

        content = message.get(
            "content",
            "",
        )

        avatar = (
            "👤"
            if role == "user"
            else "🌦️"
        )

        with st.chat_message(
            role,
            avatar=avatar,
        ):

            st.markdown(
                content
            )


def render_chat_error(
    error: WeatherApiError,
) -> None:
    """
    Render user-friendly API errors.
    """

    if isinstance(
        error,
        WeatherApiConnectionError,
    ):

        st.error(
            (
                "Unable to connect to "
                "the Weather Intelligence "
                "backend."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiTimeoutError,
    ):

        st.error(
            (
                "The weather assistant "
                "took too long to respond. "
                "Please try again."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiResponseError,
    ):

        if (
            error.status_code
            == 400
        ):

            st.warning(
                error.message
            )

        else:

            st.error(
                (
                    "Backend error "
                    f"({error.status_code}): "
                    f"{error.message}"
                )
            )

        return

    st.error(
        (
            "Unable to process your "
            f"request. {error}"
        )
    )


def process_chat_message(
    api_client: WeatherApiClient,
    user_message: str,
) -> None:
    """
    Send one user message to FastAPI.
    """

    normalized_message = (
        user_message.strip()
    )

    if not normalized_message:

        return

    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": (
                normalized_message
            ),
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(
            normalized_message
        )

    try:

        with st.chat_message(
            "assistant",
            avatar="🌦️",
        ):

            with st.spinner(
                "Thinking..."
            ):

                response = (
                    api_client.chat(
                        session_id=(
                            st.session_state
                            .chat_session_id
                        ),
                        message=(
                            normalized_message
                        ),
                    )
                )

            assistant_response = (
                response.get(
                    "response"
                )
            )

            if not assistant_response:

                assistant_response = (
                    "I couldn't generate "
                    "a weather response. "
                    "Please try again."
                )

            st.markdown(
                assistant_response
            )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": (
                    assistant_response
                ),
            }
        )

    except WeatherApiError as exc:

        with st.chat_message(
            "assistant",
            avatar="🌦️",
        ):

            render_chat_error(
                exc
            )


def render_weather_chat(
    api_client: WeatherApiClient,
) -> None:
    """
    Render conversational weather UI.

    Layout:

    1. Welcome
    2. Starter prompts
    3. Conversation
    4. Chat input
    5. HITL approval panel
    """

    render_welcome()

    selected_prompt = (
        render_starter_prompts()
    )

    if not (
        st.session_state
        .chat_messages
    ):

        st.write("")

        st.divider()

    render_chat_history()

    user_message = st.chat_input(
        "Ask about the weather..."
    )

    message_to_process = (
        selected_prompt
        or user_message
    )

    if message_to_process:

        process_chat_message(
            api_client=api_client,
            user_message=(
                message_to_process
            ),
        )

    # --------------------------------------------------------
    # Human-in-the-Loop approval panel
    # --------------------------------------------------------

    render_hitl_approvals(
        api_client
    )