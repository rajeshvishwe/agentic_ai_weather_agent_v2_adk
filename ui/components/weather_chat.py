"""
Production conversational weather chat UI.

This module manages the Streamlit presentation layer for the
Weather Intelligence conversational assistant.

Responsibilities:

- Display conversation history
- Provide suggested starter prompts
- Accept user chat input
- Send messages through WeatherApiClient
- Display assistant responses
- Handle frontend API errors safely

This module does not:

- Execute Google ADK agents directly
- Manage backend ADK sessions
- Call weather services directly
- Perform weather analytics or intelligence

Agent execution and conversational context are managed by the
FastAPI backend.
"""

from typing import Optional

import streamlit as st

from weather_intelligence_agent_v2.ui.api_client import (
    WeatherApiClient,
    WeatherApiConnectionError,
    WeatherApiError,
    WeatherApiResponseError,
    WeatherApiTimeoutError,
)


STARTER_PROMPTS = [
    "What's the current weather in Delhi?",
    "Give me the 7-day forecast for Mumbai.",
    "Which day is best for outdoor activities in London?",
    "Analyze the weather risks in Dubai this week.",
]


def render_chat_history() -> None:
    """
    Render conversation messages stored in Streamlit session state.

    Streamlit session state contains presentation history only.
    Authoritative conversational context is maintained by the
    backend ADK session.
    """

    for message in st.session_state.chat_messages:

        role = message.get(
            "role",
            "assistant",
        )

        content = message.get(
            "content",
            "",
        )

        with st.chat_message(role):
            st.markdown(content)


def render_starter_prompts() -> Optional[str]:
    """
    Render suggested starter prompts.

    Starter prompts are displayed only when the conversation
    contains no messages.

    Returns:
        Selected starter prompt, or None when no prompt
        was selected.
    """

    if st.session_state.chat_messages:
        return None

    st.markdown(
        "**Try asking:**"
    )

    columns = st.columns(2)

    selected_prompt = None

    for index, prompt in enumerate(
        STARTER_PROMPTS
    ):
        column = columns[
            index % 2
        ]

        with column:
            if st.button(
                prompt,
                key=f"starter_prompt_{index}",
                use_container_width=True,
            ):
                selected_prompt = prompt

    return selected_prompt


def render_chat_error(
    error: WeatherApiError,
) -> None:
    """
    Render a user-friendly conversational API error.

    Args:
        error:
            Error raised by WeatherApiClient.
    """

    if isinstance(
        error,
        WeatherApiConnectionError,
    ):
        st.error(
            "The Weather Intelligence backend "
            "is currently unavailable. "
            "Please try again when the service "
            "is available."
        )

        return

    if isinstance(
        error,
        WeatherApiTimeoutError,
    ):
        st.error(
            "The weather assistant took too long "
            "to respond. Please try your question again."
        )

        return

    if isinstance(
        error,
        WeatherApiResponseError,
    ):
        st.error(
            f"The weather assistant returned an error "
            f"({error.status_code}): "
            f"{error.message}"
        )

        return

    st.error(
        "Unable to process your weather question. "
        f"{error}"
    )


def process_chat_message(
    api_client: WeatherApiClient,
    user_message: str,
) -> None:
    """
    Process a conversational weather request.

    The user message is added to UI history before the API call.

    The assistant response is added only after a successful
    backend response. This prevents failed backend requests from
    creating fake assistant messages in conversation history.

    Args:
        api_client:
            Client used to communicate with FastAPI.

        user_message:
            User message to send to the weather agent.
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
        "user"
    ):
        st.markdown(
            normalized_message
        )

    try:

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Analyzing your weather request..."
            ):

                response = api_client.chat(
                    session_id=(
                        st.session_state
                        .chat_session_id
                    ),
                    message=normalized_message,
                )

            assistant_response = (
                response.get(
                    "response"
                )
            )

            if not assistant_response:
                assistant_response = (
                    "I was unable to generate a "
                    "weather response. "
                    "Please try again."
                )

            st.markdown(
                assistant_response
            )

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
            }
        )

    except WeatherApiError as exc:

        with st.chat_message(
            "assistant"
        ):
            render_chat_error(
                exc
            )


def render_weather_chat(
    api_client: WeatherApiClient,
) -> None:
    """
    Render the production conversational weather assistant.

    Args:
        api_client:
            Client used to communicate with FastAPI.
    """

    st.subheader(
        "💬 Weather Intelligence Assistant"
    )

    st.caption(
        "Ask follow-up questions about current weather, "
        "forecasts, analytics, planning, and "
        "weather intelligence."
    )

    render_chat_history()

    selected_prompt = (
        render_starter_prompts()
    )

    user_message = st.chat_input(
        "Ask a weather question..."
    )

    message_to_process = (
        selected_prompt
        or user_message
    )

    if message_to_process:
        process_chat_message(
            api_client=api_client,
            user_message=message_to_process,
        )