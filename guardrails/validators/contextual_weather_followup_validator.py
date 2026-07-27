"""
Deterministic contextual weather follow-up validator.

This validator is used only after a conversation has already completed
at least one valid weather-agent turn.

It deliberately accepts only narrow, low-ambiguity follow-up forms such
as "What about tomorrow?" or "How about Mumbai?". It is not a replacement
for the normal WeatherIntentValidator and must never be used for a new
conversation without established weather context.
"""

from __future__ import annotations

import re

from weather_intelligence_agent_v2.config.city_aliases import CITY_ALIASES
from weather_intelligence_agent_v2.config.city_resolver import resolve_city
from weather_intelligence_agent_v2.guardrails.config.intent_vocabulary import (
    TIME_TERMS,
)
from weather_intelligence_agent_v2.guardrails.models import ValidationResult
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class ContextualWeatherFollowupValidator(BaseValidator):
    """
    Validate narrow follow-up requests inside an established weather chat.

    Supported contextual forms include:

    - tomorrow
    - what about tomorrow
    - how about next week
    - and friday
    - what about mumbai
    - how about london

    Longer or unrelated requests remain rejected and therefore cannot use
    conversation context to bypass the weather-domain boundary.
    """

    TOKEN_PATTERN = re.compile(r"[A-Za-z']+")
    SPACE_PATTERN = re.compile(r"\s+")
    EDGE_PUNCTUATION_PATTERN = re.compile(
        r"^[\s,;:!?\.\-]+|[\s,;:!?\.\-]+$"
    )

    FOLLOWUP_PREFIXES = (
        "what about ",
        "how about ",
        "and ",
    )

    KNOWN_CITIES = {
        city.lower()
        for city in CITY_ALIASES.values()
    }

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate a contextual follow-up message.

        Args:
            message:
                User input from an already-established weather conversation.

        Returns:
            ValidationResult indicating whether the message is a safe,
            narrowly-scoped contextual weather follow-up.
        """

        if message is None:
            return self._failure()

        text = self._normalize(message)

        if not text:
            return self._failure()

        candidate = self._remove_followup_prefix(text)

        if self._is_time_reference(candidate):
            return ValidationResult.success()

        if self._is_known_city(candidate):
            return ValidationResult.success()

        return self._failure()

    def _normalize(
        self,
        message: str,
    ) -> str:
        """
        Normalize whitespace, casing, and edge punctuation.
        """

        text = message.strip().lower()
        text = self.EDGE_PUNCTUATION_PATTERN.sub(
            "",
            text,
        )

        return self.SPACE_PATTERN.sub(
            " ",
            text,
        )

    def _remove_followup_prefix(
        self,
        text: str,
    ) -> str:
        """
        Remove one supported conversational follow-up prefix.
        """

        for prefix in self.FOLLOWUP_PREFIXES:

            if text.startswith(prefix):
                return text[len(prefix):].strip()

        return text

    def _is_time_reference(
        self,
        text: str,
    ) -> bool:
        """
        Return True only for a configured standalone time expression.
        """

        return text in TIME_TERMS

    def _is_known_city(
        self,
        text: str,
    ) -> bool:
        """
        Return True only when the entire follow-up resolves to a city.
        """

        if not text:
            return False

        if text in self.KNOWN_CITIES:
            return True

        tokens = self.TOKEN_PATTERN.findall(text)

        if len(tokens) != 1:
            return False

        token = tokens[0]

        resolved_city = resolve_city(
            token
        )

        if resolved_city.lower() != token.lower():
            return True

        return (
            resolved_city.lower()
            in self.KNOWN_CITIES
        )

    def _failure(
        self,
    ) -> ValidationResult:
        """
        Return the standard weather-domain validation failure.
        """

        return ValidationResult.failure(
            error_code="OUTSIDE_WEATHER_DOMAIN",
            message=(
                "This assistant only supports "
                "weather-related requests."
            ),
            validator=self.__class__.__name__,
            category="Domain Validation",
        )