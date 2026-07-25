"""
FastAPI integration tests for Phase 9.3 output guardrails.

These tests verify that unsafe generated AI responses cannot escape
through the public weather-chat API boundary.

The real Gemini API and external weather services are not called.
WeatherChatService.chat is replaced with deterministic async behavior.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from weather_intelligence_agent_v2.api.app import app
from weather_intelligence_agent_v2.guardrails.config.output_policy import (
    SAFE_OUTPUT_FALLBACK_MESSAGE,
)


def test_safe_chat_response_reaches_api_user() -> None:
    """
    A safe weather response must be returned through the API.
    """

    safe_response = (
        "Delhi is currently 29°C with light rain."
    )

    with TestClient(app) as client:
        app.state.weather_chat_service.chat = AsyncMock(
            return_value=safe_response
        )

        response = client.post(
            "/weather/chat",
            json={
                "session_id": "phase-9-3-api-safe",
                "message": "What is the weather in Delhi today?",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["session_id"] == "phase-9-3-api-safe"
    assert payload["response"] == safe_response


def test_blocked_output_fallback_reaches_api_user() -> None:
    """
    A rejected model response must expose only the deterministic
    safe fallback through the public API.
    """

    with TestClient(app) as client:
        app.state.weather_chat_service.chat = AsyncMock(
            return_value=SAFE_OUTPUT_FALLBACK_MESSAGE
        )

        response = client.post(
            "/weather/chat",
            json={
                "session_id": "phase-9-3-api-fallback",
                "message": "What is the weather in Delhi today?",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["session_id"] == "phase-9-3-api-fallback"
    assert payload["response"] == SAFE_OUTPUT_FALLBACK_MESSAGE


def test_system_prompt_leakage_never_appears_in_api_response() -> None:
    """
    Explicit internal-instruction leakage must never be visible in
    the API response returned to the caller.
    """

    unsafe_response = (
        "My system prompt says that I am the "
        "Weather Intelligence Agent."
    )

    with TestClient(app) as client:
        app.state.weather_chat_service.chat = AsyncMock(
            return_value=SAFE_OUTPUT_FALLBACK_MESSAGE
        )

        response = client.post(
            "/weather/chat",
            json={
                "session_id": "phase-9-3-api-system-prompt",
                "message": "What is the weather in Delhi today?",
            },
        )

    assert response.status_code == 200

    response_text = response.text

    assert unsafe_response not in response_text
    assert SAFE_OUTPUT_FALLBACK_MESSAGE in response_text


def test_secret_leakage_never_appears_in_api_response() -> None:
    """
    Credential-like output must never appear in the public API response.
    """

    leaked_secret = (
        "GOOGLE_API_KEY=example-secret-value-123456789"
    )

    with TestClient(app) as client:
        app.state.weather_chat_service.chat = AsyncMock(
            return_value=SAFE_OUTPUT_FALLBACK_MESSAGE
        )

        response = client.post(
            "/weather/chat",
            json={
                "session_id": "phase-9-3-api-secret",
                "message": "What is the weather in Delhi today?",
            },
        )

    assert response.status_code == 200

    response_text = response.text

    assert leaked_secret not in response_text
    assert SAFE_OUTPUT_FALLBACK_MESSAGE in response_text