"""
Streamlit frontend for the Weather Intelligence Agent.

The application provides two complementary experiences:

1. Structured Weather Dashboard
2. Conversational Weather Intelligence Assistant

All backend functionality is accessed exclusively through
WeatherApiClient.

Streamlit never directly instantiates backend weather services,
Google ADK agents, runners, or session services.
"""

import uuid

import streamlit as st

from weather_intelligence_agent_v2.ui.api_client import (
    WeatherApiClient,
    WeatherApiConnectionError,
    WeatherApiError,
    WeatherApiResponseError,
    WeatherApiTimeoutError,
)
from weather_intelligence_agent_v2.ui.components.weather_chat import (
    render_weather_chat,
)
from weather_intelligence_agent_v2.ui.components.weather_dashboard import (
    render_weather_dashboard,
)
from weather_intelligence_agent_v2.ui.config import (
    ui_settings,
)


def create_api_client() -> WeatherApiClient:
    """
    Create the Weather Intelligence API client.

    Returns:
        Configured WeatherApiClient instance.
    """

    return WeatherApiClient(
        base_url=ui_settings.api_base_url,
        timeout_seconds=(
            ui_settings.request_timeout_seconds
        ),
    )


def initialize_session_state() -> None:
    """
    Initialize Streamlit application session state.

    Dashboard state:
        weather_plan:
            Last structured weather planning response.

        last_city:
            Last city requested through the dashboard.

    Chat state:
        chat_messages:
            Conversation messages displayed by Streamlit.

        chat_session_id:
            Stable conversation identifier used by the backend
            ADK session infrastructure.
    """

    defaults = {
        "weather_plan": None,
        "last_city": None,
        "chat_messages": [],
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value

    if (
        "chat_session_id"
        not in st.session_state
    ):
        st.session_state.chat_session_id = (
            create_chat_session_id()
        )


def create_chat_session_id() -> str:
    """
    Generate a new unique chat session identifier.

    Returns:
        UUID string used as the ADK conversation session ID.
    """

    return str(
        uuid.uuid4()
    )


def start_new_conversation() -> None:
    """
    Start a completely new conversation.

    This operation:

    - Clears visible Streamlit chat history.
    - Generates a new chat session ID.
    - Causes subsequent messages to use a new ADK session.

    The previous backend session may remain in the current
    in-memory session service until application shutdown, but
    it will no longer be referenced by this Streamlit session.
    """

    st.session_state.chat_messages = []

    st.session_state.chat_session_id = (
        create_chat_session_id()
    )


def clear_chat_history() -> None:
    """
    Clear visible Streamlit conversation history.

    The existing chat session ID is preserved.

    This means the backend ADK conversational context remains
    active even though previous messages are no longer displayed
    in the Streamlit interface.
    """

    st.session_state.chat_messages = []


def render_sidebar(
    api_client: WeatherApiClient,
) -> None:
    """
    Render application controls and backend status.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    with st.sidebar:

        st.title(
            "🌦️ Weather Intelligence"
        )

        st.caption(
            "Enterprise AI Weather Platform"
        )

        st.divider()

        # -----------------------------------------------------
        # Backend Status
        # -----------------------------------------------------

        st.subheader(
            "Backend Status"
        )

        try:

            health = api_client.health()

            status = health.get(
                "status",
                "UNKNOWN",
            )

            if (
                str(status).upper()
                == "UP"
            ):
                st.success(
                    "FastAPI backend is online."
                )

            else:
                st.warning(
                    f"Backend status: {status}"
                )

            version = health.get(
                "version"
            )

            if version:
                st.caption(
                    f"API Version: {version}"
                )

        except WeatherApiError:

            st.error(
                "FastAPI backend is unavailable."
            )

        st.divider()

        # -----------------------------------------------------
        # Conversation Controls
        # -----------------------------------------------------

        st.subheader(
            "Conversation"
        )

        if st.button(
            "➕ New Conversation",
            use_container_width=True,
            type="primary",
        ):

            start_new_conversation()

            st.rerun()

        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True,
        ):

            clear_chat_history()

            st.rerun()

        message_count = len(
            st.session_state.chat_messages
        )

        user_message_count = sum(
            1
            for message
            in st.session_state.chat_messages
            if message.get("role")
            == "user"
        )

        st.caption(
            f"Messages: {message_count}"
        )

        st.caption(
            f"Questions: {user_message_count}"
        )

        st.divider()

        # -----------------------------------------------------
        # Backend Configuration
        # -----------------------------------------------------

        st.caption(
            f"Backend: "
            f"{ui_settings.api_base_url}"
        )

        # Session IDs are useful during development but should
        # not occupy the normal production interface.

        with st.expander(
            "Developer Information"
        ):

            st.caption(
                "Chat Session ID"
            )

            st.code(
                st.session_state
                .chat_session_id,
                language=None,
            )


def render_api_error(
    error: WeatherApiError,
) -> None:
    """
    Render a user-friendly dashboard API error.

    Args:
        error:
            Error raised by WeatherApiClient.
    """

    if isinstance(
        error,
        WeatherApiConnectionError,
    ):

        st.error(
            "Unable to connect to the FastAPI backend. "
            "Make sure the API server is running."
        )

        return

    if isinstance(
        error,
        WeatherApiTimeoutError,
    ):

        st.error(
            "The weather request timed out. "
            "Please try again."
        )

        return

    if isinstance(
        error,
        WeatherApiResponseError,
    ):

        st.error(
            f"Weather API error "
            f"({error.status_code}): "
            f"{error.message}"
        )

        return

    st.error(
        str(error)
    )


def render_search_form(
    api_client: WeatherApiClient,
) -> None:
    """
    Render structured weather dashboard search.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    st.subheader(
        "🔎 Weather Dashboard"
    )

    st.caption(
        "Generate structured weather forecasts, "
        "analytics, and intelligence for a city."
    )

    with st.form(
        "weather_search_form"
    ):

        city = st.text_input(
            "Enter City",
            placeholder=(
                "Example: Delhi, London, Tokyo"
            ),
        )

        submitted = (
            st.form_submit_button(
                "Generate Weather Intelligence",
                type="primary",
                use_container_width=True,
            )
        )

    if not submitted:
        return

    normalized_city = (
        city.strip()
    )

    if not normalized_city:

        st.warning(
            "Please enter a city."
        )

        return

    try:

        with st.spinner(
            f"Analyzing weather conditions "
            f"for {normalized_city}..."
        ):

            weather_plan = (
                api_client
                .get_weather_plan(
                    normalized_city
                )
            )

        st.session_state.weather_plan = (
            weather_plan
        )

        st.session_state.last_city = (
            normalized_city
        )

    except WeatherApiError as exc:

        render_api_error(
            exc
        )


def render_dashboard_section() -> None:
    """
    Render structured weather dashboard data.
    """

    weather_plan = (
        st.session_state.weather_plan
    )

    if weather_plan is None:

        st.info(
            "Enter a city above to generate "
            "the weather dashboard."
        )

        return

    last_city = (
        st.session_state.last_city
    )

    st.success(
        f"Weather intelligence generated "
        f"for {last_city}."
    )

    st.divider()

    render_weather_dashboard(
        weather_plan
    )


def main() -> None:
    """
    Run the Weather Intelligence Streamlit application.
    """

    st.set_page_config(
        page_title=(
            "Weather Intelligence Agent"
        ),
        page_icon="🌦️",
        layout="wide",
    )

    initialize_session_state()

    api_client = (
        create_api_client()
    )

    render_sidebar(
        api_client
    )

    st.title(
        "🌦️ Weather Intelligence Agent"
    )

    st.caption(
        "AI-powered weather forecasting, "
        "analytics, planning, and "
        "conversational intelligence."
    )

    st.divider()

    # ---------------------------------------------------------
    # Structured Weather Dashboard
    # ---------------------------------------------------------

    render_search_form(
        api_client
    )

    render_dashboard_section()

    # ---------------------------------------------------------
    # Conversational Weather Assistant
    # ---------------------------------------------------------

    st.divider()

    render_weather_chat(
        api_client
    )


if __name__ == "__main__":
    main()