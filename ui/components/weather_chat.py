"""
Conversational weather assistant UI.

This module is presentation-only.

It renders:

- assistant landing state
- example prompts
- conversation history
- chat input
- loading feedback
- API errors

All weather and Agentic AI functionality remains in the FastAPI
backend.
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


STARTER_PROMPTS: tuple[
    tuple[str, str],
    ...,
] = (
    (
        "🌤️ Current Weather",
        "What is the current weather in Delhi?",
    ),
    (
        "📅 7-Day Forecast",
        "Give me the 7-day forecast for Mumbai.",
    ),
    (
        "🌍 Compare Cities",
        "Compare the weather in Delhi and London.",
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
    Render the assistant landing content.

    The application title is deliberately not repeated here.
    """

    if st.session_state.chat_messages:
        return

    st.markdown(
        "### 👋 How can I help with the weather?"
    )

    st.caption(
        (
            "Ask about current conditions, forecasts, "
            "city comparisons, risks, or outdoor plans."
        )
    )


def render_starter_prompts() -> Optional[str]:
    """
    Render four compact example-question buttons.

    Returns:
        Selected starter prompt or None.
    """

    if st.session_state.chat_messages:
        return None

    st.write("")

    columns = st.columns(
        2,
        gap="small",
    )

    selected_prompt: Optional[str] = None

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
                    f"starter_prompt_{index}"
                ),
                help=prompt,
                use_container_width=True,
            ):

                selected_prompt = prompt

    return selected_prompt


def render_chat_history() -> None:
    """
    Render visible conversation messages.
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
    Render user-friendly chat errors.
    """

    if isinstance(
        error,
        WeatherApiConnectionError,
    ):

        st.error(
            (
                "Unable to connect to the "
                "Weather Intelligence backend."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiTimeoutError,
    ):

        st.error(
            (
                "The weather assistant took too long "
                "to respond. Please try again."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiResponseError,
    ):

        if error.status_code == 400:

            st.warning(
                error.message
            )

        else:

            st.error(
                (
                    f"Backend error "
                    f"({error.status_code}): "
                    f"{error.message}"
                )
            )

        return

    st.error(
        (
            "Unable to process your request. "
            f"{error}"
        )
    )


def process_chat_message(
    api_client: WeatherApiClient,
    user_message: str,
) -> None:
    """
    Send one user message to the FastAPI chat endpoint.

    Args:
        api_client:
            Weather Intelligence API client.

        user_message:
            User question.
    """

    normalized_message = (
        user_message.strip()
    )

    if not normalized_message:
        return

    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": normalized_message,
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

                response = api_client.chat(
                    session_id=(
                        st.session_state
                        .chat_session_id
                    ),
                    message=(
                        normalized_message
                    ),
                )

            assistant_response = (
                response.get(
                    "response"
                )
            )

            if not assistant_response:

                assistant_response = (
                    "I couldn't generate a weather "
                    "response. Please try again."
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
    Render the complete conversational UI.

    No duplicate application or assistant title is rendered here.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    render_welcome()

    selected_prompt = (
        render_starter_prompts()
    )

    if not st.session_state.chat_messages:

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