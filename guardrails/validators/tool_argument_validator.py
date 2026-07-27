"""
Tool argument security validator.

This validator performs deterministic validation of arguments supplied
to approved Google ADK weather tools.

The validator protects tool execution from malformed, missing,
unexpected, or excessively large argument values.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
    ValidationSeverity,
)


class ToolArgumentValidator:
    """
    Validate arguments supplied to approved weather tools.

    Supported tool argument contracts:

    - get_current_weather(city: str)

    - get_forecast(city: str)

    - analyze_weather(cities: list[str])

    - get_weather_intelligence(city: str)

    - get_weather_plan(city: str)

    - create_weather_reminder(
          city: str,
          reminder_time: str,
          message: str,
      )

    Validation follows a deny-by-default approach.

    Unexpected parameters are rejected rather than silently ignored.
    """

    MAX_CITY_LENGTH = 100
    MAX_CITIES = 10

    MAX_REMINDER_TIME_LENGTH = 120
    MAX_REMINDER_MESSAGE_LENGTH = 500

    TOOL_ARGUMENT_POLICY: dict[
        str,
        dict[
            str,
            frozenset[str],
        ],
    ] = {
        "get_current_weather": {
            "required": frozenset(
                {
                    "city",
                }
            ),
            "allowed": frozenset(
                {
                    "city",
                }
            ),
        },

        "get_forecast": {
            "required": frozenset(
                {
                    "city",
                }
            ),
            "allowed": frozenset(
                {
                    "city",
                }
            ),
        },

        "analyze_weather": {
            "required": frozenset(
                {
                    "cities",
                }
            ),
            "allowed": frozenset(
                {
                    "cities",
                }
            ),
        },

        "get_weather_intelligence": {
            "required": frozenset(
                {
                    "city",
                }
            ),
            "allowed": frozenset(
                {
                    "city",
                }
            ),
        },

        "get_weather_plan": {
            "required": frozenset(
                {
                    "city",
                }
            ),
            "allowed": frozenset(
                {
                    "city",
                }
            ),
        },

        "create_weather_reminder": {
            "required": frozenset(
                {
                    "city",
                    "reminder_time",
                    "message",
                }
            ),
            "allowed": frozenset(
                {
                    "city",
                    "reminder_time",
                    "message",
                }
            ),
        },
    }

    def validate(
        self,
        tool_name: str,
        arguments: Mapping[
            str,
            Any,
        ],
    ) -> ValidationResult:
        """
        Validate arguments for an approved weather tool.

        Args:
            tool_name:
                Name of the requested tool.

            arguments:
                Mapping containing tool arguments.

        Returns:
            ValidationResult:
                Success when arguments satisfy the configured
                deterministic security policy.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_ARGUMENT_INVALID_TOOL_NAME"
                ),
                message=(
                    "Tool name must be textual."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if (
            tool_name
            not in self.TOOL_ARGUMENT_POLICY
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_ARGUMENT_POLICY_NOT_FOUND"
                ),
                message=(
                    "No argument policy exists "
                    "for the requested tool."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if not isinstance(
            arguments,
            Mapping,
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_ARGUMENTS_INVALID_TYPE"
                ),
                message=(
                    "Tool arguments must be "
                    "provided as a mapping."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        policy = (
            self.TOOL_ARGUMENT_POLICY[
                tool_name
            ]
        )

        required_arguments = (
            policy[
                "required"
            ]
        )

        allowed_arguments = (
            policy[
                "allowed"
            ]
        )

        provided_arguments = frozenset(
            arguments.keys()
        )

        missing_arguments = (
            required_arguments
            - provided_arguments
        )

        if missing_arguments:
            return ValidationResult.failure(
                error_code=(
                    "TOOL_ARGUMENT_REQUIRED"
                ),
                message=(
                    "Required tool argument "
                    "is missing."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        unexpected_arguments = (
            provided_arguments
            - allowed_arguments
        )

        if unexpected_arguments:
            return ValidationResult.failure(
                error_code=(
                    "TOOL_ARGUMENT_UNEXPECTED"
                ),
                message=(
                    "Unexpected tool argument "
                    "was provided."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.CRITICAL
                ),
            )

        # ------------------------------------------------------
        # Multi-city analytics
        # ------------------------------------------------------

        if (
            tool_name
            == "analyze_weather"
        ):
            return self._validate_cities(
                arguments.get(
                    "cities"
                )
            )

        # ------------------------------------------------------
        # HITL weather reminder
        # ------------------------------------------------------

        if (
            tool_name
            == "create_weather_reminder"
        ):
            return (
                self._validate_weather_reminder(
                    arguments
                )
            )

        # ------------------------------------------------------
        # Standard single-city tools
        # ------------------------------------------------------

        return self._validate_city(
            arguments.get(
                "city"
            )
        )

    def _validate_weather_reminder(
        self,
        arguments: Mapping[
            str,
            Any,
        ],
    ) -> ValidationResult:
        """
        Validate weather reminder arguments.
        """

        city_result = (
            self._validate_city(
                arguments.get(
                    "city"
                )
            )
        )

        if not city_result.is_valid:
            return city_result

        reminder_time_result = (
            self._validate_text_argument(
                value=(
                    arguments.get(
                        "reminder_time"
                    )
                ),
                field_name=(
                    "Reminder time"
                ),
                error_prefix=(
                    "TOOL_REMINDER_TIME"
                ),
                max_length=(
                    self.MAX_REMINDER_TIME_LENGTH
                ),
            )
        )

        if not (
            reminder_time_result.is_valid
        ):
            return (
                reminder_time_result
            )

        message_result = (
            self._validate_text_argument(
                value=(
                    arguments.get(
                        "message"
                    )
                ),
                field_name=(
                    "Reminder message"
                ),
                error_prefix=(
                    "TOOL_REMINDER_MESSAGE"
                ),
                max_length=(
                    self.MAX_REMINDER_MESSAGE_LENGTH
                ),
            )
        )

        if not message_result.is_valid:
            return message_result

        return ValidationResult.success()

    def _validate_text_argument(
        self,
        *,
        value: Any,
        field_name: str,
        error_prefix: str,
        max_length: int,
    ) -> ValidationResult:
        """
        Validate a generic textual tool argument.
        """

        if not isinstance(
            value,
            str,
        ):
            return ValidationResult.failure(
                error_code=(
                    f"{error_prefix}_INVALID_TYPE"
                ),
                message=(
                    f"{field_name} must "
                    "be textual."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        normalized_value = (
            value.strip()
        )

        if not normalized_value:
            return ValidationResult.failure(
                error_code=(
                    f"{error_prefix}_EMPTY"
                ),
                message=(
                    f"{field_name} must "
                    "not be empty."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if (
            len(
                normalized_value
            )
            > max_length
        ):
            return ValidationResult.failure(
                error_code=(
                    f"{error_prefix}_TOO_LONG"
                ),
                message=(
                    f"{field_name} exceeds "
                    "the maximum permitted "
                    "length."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.WARNING
                ),
            )

        return ValidationResult.success()

    def _validate_city(
        self,
        city: Any,
    ) -> ValidationResult:
        """
        Validate a single city argument.
        """

        if not isinstance(
            city,
            str,
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_CITY_INVALID_TYPE"
                ),
                message=(
                    "City must be textual."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        normalized_city = (
            city.strip()
        )

        if not normalized_city:
            return ValidationResult.failure(
                error_code=(
                    "TOOL_CITY_EMPTY"
                ),
                message=(
                    "City must not be empty."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if (
            len(
                normalized_city
            )
            > self.MAX_CITY_LENGTH
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_CITY_TOO_LONG"
                ),
                message=(
                    "City exceeds the maximum "
                    "permitted length."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.WARNING
                ),
            )

        return ValidationResult.success()

    def _validate_cities(
        self,
        cities: Any,
    ) -> ValidationResult:
        """
        Validate multi-city arguments used by weather analytics.
        """

        if not isinstance(
            cities,
            list,
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_CITIES_INVALID_TYPE"
                ),
                message=(
                    "Cities must be provided "
                    "as a list."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if not cities:
            return ValidationResult.failure(
                error_code=(
                    "TOOL_CITIES_EMPTY"
                ),
                message=(
                    "Cities list must not "
                    "be empty."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.ERROR
                ),
            )

        if (
            len(
                cities
            )
            > self.MAX_CITIES
        ):
            return ValidationResult.failure(
                error_code=(
                    "TOOL_TOO_MANY_CITIES"
                ),
                message=(
                    "Too many cities were "
                    "requested for one tool "
                    "call."
                ),
                validator=(
                    self.__class__.__name__
                ),
                category=(
                    "TOOL_ARGUMENT_SECURITY"
                ),
                severity=(
                    ValidationSeverity.WARNING
                ),
            )

        for city in cities:

            city_result = (
                self._validate_city(
                    city
                )
            )

            if not (
                city_result.is_valid
            ):
                return city_result

        return ValidationResult.success()