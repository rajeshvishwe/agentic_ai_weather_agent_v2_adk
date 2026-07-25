"""
Deterministic weather intent validator.

This validator determines whether a user request belongs to the
weather domain without invoking an LLM.

The validator intentionally relies on deterministic rules,
allowing invalid requests to be rejected before reaching
the Google ADK agent.

Design Goals
------------
- Deterministic
- Fast
- Extensible
- Testable
- Configuration-driven
"""

from __future__ import annotations

import re

from weather_intelligence_agent_v2.config.city_aliases import (
    CITY_ALIASES,
)
from weather_intelligence_agent_v2.config.city_resolver import (
    resolve_city,
)
from weather_intelligence_agent_v2.guardrails.config.intent_vocabulary import (
    QUESTION_PATTERNS,
    TIME_TERMS,
    WEATHER_ACTIONS,
    WEATHER_TERMS,
)
from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class WeatherIntentValidator(BaseValidator):
    """
    Validate whether a request belongs to the weather domain.
    """

    TOKEN_PATTERN = re.compile(r"[A-Za-z']+")

    #
    # Cache canonical city names once.
    #
    KNOWN_CITIES = {
        city.lower()
        for city in CITY_ALIASES.values()
    }

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate that the request belongs to the weather domain.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        # Defensive check.
        if message is None:
            return ValidationResult.success()

        text = message.lower()

        #
        # Rule 1
        # Direct weather terminology.
        #
        if self._contains_weather_terms(text):
            return ValidationResult.success()

        #
        # Rule 2
        # Weather-dependent activities.
        #
        if self._contains_weather_activity(text):

            if (
                self._contains_time_reference(text)
                or self._contains_known_city(text)
            ):
                return ValidationResult.success()

        #
        # Rule 3
        # City + Time.
        #
        if (
            self._contains_known_city(text)
            and self._contains_time_reference(text)
        ):
            return ValidationResult.success()

        #
        # Rule 4
        # Question pattern + City.
        #
        if (
            self._contains_question_pattern(text)
            and self._contains_known_city(text)
        ):
            return ValidationResult.success()

        return ValidationResult.failure(
            error_code="OUTSIDE_WEATHER_DOMAIN",
            message=(
                "This assistant only supports "
                "weather-related requests."
            ),
            validator=self.__class__.__name__,
            category="Domain Validation",
        )

    def _contains_weather_terms(
        self,
        text: str,
    ) -> bool:
        """
        Detect explicit weather terminology.
        """

        return any(
            term in text
            for term in WEATHER_TERMS
        )

    def _contains_weather_activity(
        self,
        text: str,
    ) -> bool:
        """
        Detect weather-dependent activities.
        """

        return any(
            activity in text
            for activity in WEATHER_ACTIONS
        )

    def _contains_time_reference(
        self,
        text: str,
    ) -> bool:
        """
        Detect time expressions.
        """

        return any(
            value in text
            for value in TIME_TERMS
        )

    def _contains_question_pattern(
        self,
        text: str,
    ) -> bool:
        """
        Detect common weather question patterns.
        """

        return any(
            pattern in text
            for pattern in QUESTION_PATTERNS
        )

    def _contains_known_city(
        self,
        text: str,
    ) -> bool:
        """
        Detect known cities using aliases and canonical names.
        """

        #
        # Check aliases using the existing resolver.
        #
        tokens = self.TOKEN_PATTERN.findall(text)

        for token in tokens:

            resolved_city = resolve_city(token)

            #
            # Alias detected.
            #
            if resolved_city.lower() != token.lower():
                return True

            #
            # Canonical city detected.
            #
            if resolved_city.lower() in self.KNOWN_CITIES:
                return True

        #
        # Handle multi-word cities such as "New York".
        #
        return any(
            city in text
            for city in self.KNOWN_CITIES
        )