"""
HTTP client for communicating with the Weather Intelligence API.

The Streamlit application communicates with backend functionality
exclusively through this client abstraction.

Backend application services and Google ADK components must never
be instantiated directly inside the Streamlit UI layer.

Supported API groups:

- health
- weather planning
- conversational weather
- HITL approval management
"""

from __future__ import annotations

from typing import Any

import requests
from requests import Response
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
)
from requests.exceptions import (
    RequestException,
    Timeout,
)


class WeatherApiError(
    Exception
):
    """
    Base Weather API client exception.
    """


class WeatherApiConnectionError(
    WeatherApiError
):
    """
    Raised when FastAPI cannot be reached.
    """


class WeatherApiTimeoutError(
    WeatherApiError
):
    """
    Raised when a request times out.
    """


class WeatherApiResponseError(
    WeatherApiError
):
    """
    Raised for unsuccessful HTTP responses.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
    ) -> None:

        self.status_code = (
            status_code
        )

        self.message = message

        super().__init__(
            (
                "Weather API returned HTTP "
                f"{status_code}: {message}"
            )
        )


class WeatherApiClient:
    """
    HTTP client for Weather Intelligence FastAPI.

    Responsibilities:

    - URL construction
    - request execution
    - timeout handling
    - HTTP error handling
    - JSON decoding
    - weather planning
    - conversational weather
    - HITL approval lifecycle
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 30.0,
    ) -> None:

        self._base_url = (
            base_url.rstrip("/")
        )

        self._timeout_seconds = (
            timeout_seconds
        )

    # ========================================================
    # Health
    # ========================================================

    def health(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve backend health.
        """

        response = self._request(
            method="GET",
            path="/health",
        )

        return self._decode_json_object(
            response
        )

    # ========================================================
    # Weather Planning
    # ========================================================

    def get_weather_plan(
        self,
        city: str,
    ) -> dict[str, Any]:
        """
        Retrieve complete weather plan.
        """

        response = self._request(
            method="POST",
            path="/weather/plan",
            json={
                "city": city,
            },
        )

        return self._decode_json_object(
            response
        )

    # ========================================================
    # Conversational Weather
    # ========================================================

    def chat(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Send one conversational request.
        """

        response = self._request(
            method="POST",
            path="/weather/chat",
            json={
                "session_id": (
                    session_id
                ),
                "message": message,
            },
        )

        return self._decode_json_object(
            response
        )

    # ========================================================
    # HITL Approvals
    # ========================================================

    def list_approvals(
        self,
        status: str | None = None,
    ) -> list[
        dict[str, Any]
    ]:
        """
        List HITL approval requests.

        Args:
            status:
                Optional status filter.

                PENDING
                APPROVED
                REJECTED

        Returns:
            Approval response dictionaries.
        """

        params: dict[
            str,
            str,
        ] = {}

        if status:

            params["status"] = status

        response = self._request(
            method="GET",
            path="/approvals",
            params=params,
        )

        return self._decode_json_list(
            response
        )

    def get_approval(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve a single approval request.
        """

        response = self._request(
            method="GET",
            path=(
                f"/approvals/{request_id}"
            ),
        )

        return self._decode_json_object(
            response
        )

    def approve_request(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Approve a pending HITL request.
        """

        response = self._request(
            method="POST",
            path=(
                f"/approvals/"
                f"{request_id}/approve"
            ),
        )

        return self._decode_json_object(
            response
        )

    def reject_request(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Reject a pending HITL request.
        """

        response = self._request(
            method="POST",
            path=(
                f"/approvals/"
                f"{request_id}/reject"
            ),
        )

        return self._decode_json_object(
            response
        )

    # ========================================================
    # HTTP
    # ========================================================

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Response:
        """
        Execute HTTP request.
        """

        url = (
            f"{self._base_url}"
            f"{path}"
        )

        try:

            response = (
                requests.request(
                    method=method,
                    url=url,
                    timeout=(
                        self._timeout_seconds
                    ),
                    **kwargs,
                )
            )

        except Timeout as exc:

            raise WeatherApiTimeoutError(
                (
                    "The Weather Intelligence "
                    "API request timed out."
                )
            ) from exc

        except (
            RequestsConnectionError
        ) as exc:

            raise (
                WeatherApiConnectionError(
                    (
                        "Unable to connect to "
                        "the Weather "
                        "Intelligence API."
                    )
                )
            ) from exc

        except RequestException as exc:

            raise WeatherApiError(
                (
                    "Unexpected error while "
                    "communicating with the "
                    "Weather Intelligence API."
                )
            ) from exc

        if not response.ok:

            message = (
                self._extract_error_message(
                    response
                )
            )

            raise (
                WeatherApiResponseError(
                    status_code=(
                        response.status_code
                    ),
                    message=message,
                )
            )

        return response

    # ========================================================
    # JSON Decoding
    # ========================================================

    @staticmethod
    def _decode_json_object(
        response: Response,
    ) -> dict[str, Any]:
        """
        Decode JSON object response.
        """

        try:

            payload = response.json()

        except ValueError as exc:

            raise WeatherApiError(
                (
                    "Weather Intelligence API "
                    "returned invalid JSON."
                )
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):

            raise WeatherApiError(
                (
                    "Weather Intelligence API "
                    "returned an unexpected "
                    "response format."
                )
            )

        return payload

    @staticmethod
    def _decode_json_list(
        response: Response,
    ) -> list[
        dict[str, Any]
    ]:
        """
        Decode JSON list response.
        """

        try:

            payload = response.json()

        except ValueError as exc:

            raise WeatherApiError(
                (
                    "Weather Intelligence API "
                    "returned invalid JSON."
                )
            ) from exc

        if not isinstance(
            payload,
            list,
        ):

            raise WeatherApiError(
                (
                    "Weather Intelligence API "
                    "returned an unexpected "
                    "list response format."
                )
            )

        result: list[
            dict[str, Any]
        ] = []

        for item in payload:

            if not isinstance(
                item,
                dict,
            ):

                raise WeatherApiError(
                    (
                        "Weather Intelligence "
                        "approval response "
                        "contains an invalid "
                        "item."
                    )
                )

            result.append(
                item
            )

        return result

    # ========================================================
    # Error Extraction
    # ========================================================

    @staticmethod
    def _extract_error_message(
        response: Response,
    ) -> str:
        """
        Extract useful FastAPI error.
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

                if isinstance(
                    detail,
                    dict,
                ):

                    message = detail.get(
                        "message"
                    )

                    if message:

                        return str(
                            message
                        )

                    return str(
                        detail
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