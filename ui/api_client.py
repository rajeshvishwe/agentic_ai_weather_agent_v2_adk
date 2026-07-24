"""
HTTP client for communicating with the Weather Intelligence API.

The Streamlit application communicates with backend functionality
exclusively through this client abstraction.

Backend application services and Google ADK components must never
be instantiated directly inside the Streamlit UI layer.
"""

from typing import Any

import requests
from requests import Response
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
)
from requests.exceptions import RequestException
from requests.exceptions import Timeout


class WeatherApiError(Exception):
    """
    Base exception raised by the Weather API client.
    """


class WeatherApiConnectionError(WeatherApiError):
    """
    Raised when the FastAPI backend cannot be reached.
    """


class WeatherApiTimeoutError(WeatherApiError):
    """
    Raised when an API request exceeds the configured timeout.
    """


class WeatherApiResponseError(WeatherApiError):
    """
    Raised when the API returns an unsuccessful HTTP response.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
    ) -> None:
        """
        Initialize the API response error.

        Args:
            status_code:
                HTTP status code returned by the backend.

            message:
                Human-readable error description.
        """

        self.status_code = status_code
        self.message = message

        super().__init__(
            f"Weather API returned HTTP "
            f"{status_code}: {message}"
        )


class WeatherApiClient:
    """
    Client abstraction for the Weather Intelligence FastAPI API.

    The client encapsulates:

    - URL construction
    - HTTP communication
    - request timeout handling
    - connection error handling
    - HTTP response validation
    - JSON decoding
    - weather planning API communication
    - conversational weather API communication

    This prevents HTTP concerns from leaking into Streamlit
    presentation code.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        """
        Initialize the Weather API client.

        Args:
            base_url:
                Base URL of the FastAPI backend.

            timeout_seconds:
                Maximum request duration in seconds.
        """

        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        """
        Retrieve backend health information.

        Returns:
            Health response returned by FastAPI.

        Raises:
            WeatherApiError:
                If communication with the API fails.
        """

        response = self._request(
            method="GET",
            path="/health",
        )

        return self._decode_json(
            response
        )

    def get_weather_plan(
        self,
        city: str,
    ) -> dict[str, Any]:
        """
        Retrieve a complete weather planning report.

        Args:
            city:
                City for which weather intelligence is requested.

        Returns:
            Weather planning response returned by FastAPI.

        Raises:
            WeatherApiError:
                If communication with the API fails.
        """

        response = self._request(
            method="POST",
            path="/weather/plan",
            json={
                "city": city,
            },
        )

        return self._decode_json(
            response
        )

    def chat(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Send a conversational message to the weather agent.

        The request is sent to the FastAPI chat endpoint.
        Streamlit never interacts directly with Google ADK.

        Args:
            session_id:
                Unique conversation session identifier.

            message:
                User message sent to the weather agent.

        Returns:
            Weather chat response returned by FastAPI.

        Raises:
            WeatherApiError:
                If communication with the API fails.
        """

        response = self._request(
            method="POST",
            path="/weather/chat",
            json={
                "session_id": session_id,
                "message": message,
            },
        )

        return self._decode_json(
            response
        )

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Response:
        """
        Execute an HTTP request against the FastAPI backend.

        Args:
            method:
                HTTP method.

            path:
                API endpoint path.

            **kwargs:
                Additional arguments passed to requests.request.

        Returns:
            Successful HTTP response.

        Raises:
            WeatherApiConnectionError:
                If the backend cannot be reached.

            WeatherApiTimeoutError:
                If the request exceeds the configured timeout.

            WeatherApiResponseError:
                If the API returns a non-success HTTP status.

            WeatherApiError:
                For other HTTP communication failures.
        """

        url = f"{self._base_url}{path}"

        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self._timeout_seconds,
                **kwargs,
            )

        except Timeout as exc:
            raise WeatherApiTimeoutError(
                "The Weather Intelligence API request "
                "timed out."
            ) from exc

        except RequestsConnectionError as exc:
            raise WeatherApiConnectionError(
                "Unable to connect to the "
                "Weather Intelligence API."
            ) from exc

        except RequestException as exc:
            raise WeatherApiError(
                "Unexpected error while communicating "
                "with the Weather Intelligence API."
            ) from exc

        if not response.ok:
            message = self._extract_error_message(
                response
            )

            raise WeatherApiResponseError(
                status_code=response.status_code,
                message=message,
            )

        return response

    @staticmethod
    def _decode_json(
        response: Response,
    ) -> dict[str, Any]:
        """
        Decode a successful JSON API response.

        Args:
            response:
                Successful HTTP response.

        Returns:
            Parsed JSON dictionary.

        Raises:
            WeatherApiError:
                If the response does not contain valid JSON or
                has an unexpected response structure.
        """

        try:
            payload = response.json()

        except ValueError as exc:
            raise WeatherApiError(
                "Weather Intelligence API returned "
                "an invalid JSON response."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise WeatherApiError(
                "Weather Intelligence API returned "
                "an unexpected response format."
            )

        return payload

    @staticmethod
    def _extract_error_message(
        response: Response,
    ) -> str:
        """
        Extract a useful error message from a failed API response.

        FastAPI normally returns errors using:

            {
                "detail": "Error description"
            }

        Args:
            response:
                Failed HTTP response.

        Returns:
            Human-readable error message.
        """

        try:
            payload = response.json()

            if isinstance(
                payload,
                dict,
            ):
                detail = payload.get(
                    "detail"
                )

                if detail:
                    return str(
                        detail
                    )

        except ValueError:
            pass

        if response.text:
            return response.text

        return "Unknown API error."