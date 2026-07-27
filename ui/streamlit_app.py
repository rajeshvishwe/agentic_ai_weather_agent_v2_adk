"""
Streamlit frontend for Weather Intelligence Agent v2.

The application provides two primary presentation experiences:

1. Weather Dashboard
2. Conversational AI Assistant

Navigation is displayed centrally in the main application area.

The implementation deliberately uses explicit page routing instead
of Streamlit tabs because page routing has proven stable in the
current environment.

All backend functionality is accessed exclusively through
WeatherApiClient.

Streamlit does not:

- execute Google ADK directly
- create ADK runners
- call weather services directly
- calculate backend analytics
- duplicate guardrails
- duplicate weather business logic
"""

from __future__ import annotations

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


# ============================================================
# CONSTANTS
# ============================================================

DASHBOARD_PAGE = "📊 Weather Dashboard"

ASSISTANT_PAGE = "💬 AI Assistant"


# ============================================================
# API CLIENT
# ============================================================


def create_api_client() -> WeatherApiClient:
    """
    Create the FastAPI client used by Streamlit.

    Returns:
        Configured WeatherApiClient.
    """

    return WeatherApiClient(
        base_url=ui_settings.api_base_url,
        timeout_seconds=(
            ui_settings.request_timeout_seconds
        ),
    )


# ============================================================
# SESSION STATE
# ============================================================


def create_chat_session_id() -> str:
    """
    Generate a unique backend chat-session identifier.

    Returns:
        UUID string.
    """

    return str(
        uuid.uuid4()
    )


def initialize_session_state() -> None:
    """
    Initialize application session state.

    Dashboard state:
        weather_plan
        last_city

    Chat state:
        chat_messages
        chat_session_id

    Navigation state:
        active_page
    """

    if "weather_plan" not in st.session_state:

        st.session_state.weather_plan = None

    if "last_city" not in st.session_state:

        st.session_state.last_city = None

    if "chat_messages" not in st.session_state:

        st.session_state.chat_messages = []

    if "chat_session_id" not in st.session_state:

        st.session_state.chat_session_id = (
            create_chat_session_id()
        )

    if "active_page" not in st.session_state:

        st.session_state.active_page = (
            DASHBOARD_PAGE
        )


def start_new_conversation() -> None:
    """
    Start a completely new backend conversation.
    """

    st.session_state.chat_messages = []

    st.session_state.chat_session_id = (
        create_chat_session_id()
    )


def clear_chat_history() -> None:
    """
    Clear visible chat history.

    The backend chat session ID is preserved so the existing
    Google ADK conversational context remains available.
    """

    st.session_state.chat_messages = []


def open_dashboard() -> None:
    """
    Navigate to the Weather Dashboard.
    """

    st.session_state.active_page = (
        DASHBOARD_PAGE
    )


def open_ai_assistant() -> None:
    """
    Navigate to the AI Assistant.
    """

    st.session_state.active_page = (
        ASSISTANT_PAGE
    )


# ============================================================
# UI STYLING
# ============================================================


def apply_custom_styles() -> None:
    """
    Apply lightweight presentation styling.

    Styling includes:

    - compact metric cards
    - centered navigation area
    - controlled main-content width
    - sidebar separator

    No application behavior is modified.
    """

    st.markdown(
        """
<style>

/* =========================================================
   Main application container
   ========================================================= */

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}


/* =========================================================
   Sidebar
   ========================================================= */

div[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}


/* =========================================================
   Metric cards
   ========================================================= */

div[data-testid="stMetric"] {
    border: 1px solid rgba(128, 128, 128, 0.18);
    border-radius: 12px;

    padding-top: 0.55rem;
    padding-bottom: 0.55rem;
    padding-left: 0.65rem;
    padding-right: 0.65rem;

    min-height: 92px;

    overflow: hidden;
}


/* Metric label */

div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    line-height: 1.15 !important;
    font-weight: 500 !important;

    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
}


/* Metric value */

div[data-testid="stMetricValue"] {
    font-size: 1.15rem !important;
    line-height: 1.2 !important;
    font-weight: 600 !important;

    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
}


div[data-testid="stMetricValue"] > div {
    font-size: 1.15rem !important;
    line-height: 1.2 !important;

    white-space: normal !important;
    overflow-wrap: anywhere !important;
}


/* Metric delta */

div[data-testid="stMetricDelta"] {
    font-size: 0.70rem !important;
    line-height: 1.1 !important;
}


/* =========================================================
   Navigation buttons
   ========================================================= */

div[data-testid="stButton"] > button {
    border-radius: 10px;
    min-height: 2.8rem;
    font-weight: 600;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ERROR HANDLING
# ============================================================


def render_api_error(
    error: WeatherApiError,
) -> None:
    """
    Render user-friendly Weather API errors.

    Args:
        error:
            WeatherApiClient error.
    """

    if isinstance(
        error,
        WeatherApiConnectionError,
    ):

        st.error(
            (
                "Unable to connect to the FastAPI backend. "
                "Make sure the API server is running."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiTimeoutError,
    ):

        st.error(
            (
                "The weather request timed out. "
                "Please try again."
            )
        )

        return

    if isinstance(
        error,
        WeatherApiResponseError,
    ):

        st.error(
            (
                f"Weather API error "
                f"({error.status_code}): "
                f"{error.message}"
            )
        )

        return

    st.error(
        str(error)
    )


# ============================================================
# SIDEBAR
# ============================================================


def render_sidebar(
    api_client: WeatherApiClient,
) -> None:
    """
    Render backend status and conversation controls.

    Navigation is intentionally not displayed in the sidebar.

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

        # ----------------------------------------------------
        # Backend status
        # ----------------------------------------------------

        st.subheader(
            "Backend Status"
        )

        try:

            health = api_client.health()

            status = str(
                health.get(
                    "status",
                    "UNKNOWN",
                )
            ).upper()

            if status == "UP":

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

        # ----------------------------------------------------
        # Conversation controls
        # ----------------------------------------------------

        st.subheader(
            "Conversation"
        )

        if st.button(
            "➕ New Conversation",
            type="primary",
            width="stretch",
        ):

            start_new_conversation()

            st.rerun()

        if st.button(
            "🗑️ Clear Chat",
            width="stretch",
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

        # ----------------------------------------------------
        # Backend information
        # ----------------------------------------------------

        st.caption(
            (
                "Backend: "
                f"{ui_settings.api_base_url}"
            )
        )

        with st.expander(
            "Developer Information"
        ):

            st.caption(
                "Chat Session ID"
            )

            st.code(
                st.session_state.chat_session_id,
                language=None,
            )


# ============================================================
# APPLICATION HEADER
# ============================================================


def render_header() -> None:
    """
    Render application-level branding.
    """

    st.title(
        "🌦️ Weather Intelligence Agent"
    )

    st.caption(
        (
            "AI-powered weather forecasting, analytics, "
            "planning, and conversational intelligence."
        )
    )


# ============================================================
# CENTER NAVIGATION
# ============================================================


def render_center_navigation() -> None:
    """
    Render centered Dashboard and AI Assistant navigation.

    The navigation behaves like two application tabs while using
    explicit session-state routing rather than st.tabs().
    """

    left_space, dashboard_column, assistant_column, right_space = (
        st.columns(
            [
                1.5,
                2,
                2,
                1.5,
            ],
            gap="small",
        )
    )

    del left_space
    del right_space

    with dashboard_column:

        dashboard_active = (
            st.session_state.active_page
            == DASHBOARD_PAGE
        )

        dashboard_label = (
            "✓ 📊 Weather Dashboard"
            if dashboard_active
            else "📊 Weather Dashboard"
        )

        if st.button(
            dashboard_label,
            key="dashboard_navigation",
            width="stretch",
            type=(
                "primary"
                if dashboard_active
                else "secondary"
            ),
        ):

            open_dashboard()

            st.rerun()

    with assistant_column:

        assistant_active = (
            st.session_state.active_page
            == ASSISTANT_PAGE
        )

        assistant_label = (
            "✓ 💬 AI Assistant"
            if assistant_active
            else "💬 AI Assistant"
        )

        if st.button(
            assistant_label,
            key="assistant_navigation",
            width="stretch",
            type=(
                "primary"
                if assistant_active
                else "secondary"
            ),
        ):

            open_ai_assistant()

            st.rerun()

    st.divider()


# ============================================================
# WEATHER DASHBOARD
# ============================================================


def render_weather_search(
    api_client: WeatherApiClient,
) -> None:
    """
    Render single-city Weather Dashboard search.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    st.subheader(
        "🔎 Explore a City"
    )

    with st.form(
        "weather_search_form"
    ):

        city = st.text_input(
            "Enter City",
            placeholder=(
                "Example: Delhi, Mumbai, London, Tokyo"
            ),
        )

        submitted = (
            st.form_submit_button(
                "Generate Weather Intelligence",
                type="primary",
                width="stretch",
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
            (
                "Analyzing weather conditions "
                f"for {normalized_city}..."
            )
        ):

            weather_plan = (
                api_client.get_weather_plan(
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


def render_dashboard_page(
    api_client: WeatherApiClient,
) -> None:
    """
    Render complete Weather Dashboard.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    render_weather_search(
        api_client
    )

    weather_plan = (
        st.session_state.weather_plan
    )

    if weather_plan is None:

        st.info(
            (
                "Enter a city above to generate "
                "weather intelligence."
            )
        )

        return

    last_city = (
        st.session_state.last_city
    )

    st.success(
        (
            "Weather intelligence generated "
            f"for {last_city}."
        )
    )

    st.divider()

    render_weather_dashboard(
        weather_plan
    )


# ============================================================
# AI ASSISTANT
# ============================================================


def render_ai_assistant_page(
    api_client: WeatherApiClient,
) -> None:
    """
    Render conversational Weather Intelligence Assistant.

    Args:
        api_client:
            Weather Intelligence API client.
    """

    render_weather_chat(
        api_client
    )


# ============================================================
# MAIN APPLICATION
# ============================================================


def main() -> None:
    """
    Run Weather Intelligence Agent Streamlit frontend.
    """

    st.set_page_config(
        page_title=(
            "Weather Intelligence Agent"
        ),
        page_icon="🌦️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_styles()

    initialize_session_state()

    api_client = (
        create_api_client()
    )

    render_sidebar(
        api_client
    )

    render_header()

    render_center_navigation()

    if (
        st.session_state.active_page
        == DASHBOARD_PAGE
    ):

        render_dashboard_page(
            api_client
        )

    elif (
        st.session_state.active_page
        == ASSISTANT_PAGE
    ):

        render_ai_assistant_page(
            api_client
        )


if __name__ == "__main__":
    main()