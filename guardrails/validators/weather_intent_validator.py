"""
Deterministic weather-intent validator with hybrid location resolution.

The validator determines whether a request belongs to the weather
domain without invoking an LLM.

Location detection uses a hybrid strategy:

1. Local aliases/canonical names for short forms such as
   BLR, DEL and NYC.

2. Open-Meteo geocoding fallback for normal global
   city/place names.

The external geocoding fallback is deliberately attempted only
after the message already looks like a weather-planning question.

This prevents every unrelated prompt from depending on an
external API.
"""

from __future__ import annotations

import re
from collections.abc import Callable

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
from weather_intelligence_agent_v2.services.geocoding_service import (
    is_valid_city,
)


class WeatherIntentValidator(
    BaseValidator
):
    """
    Validate whether a request belongs to the weather domain.

    The validator combines:

    - explicit weather vocabulary
    - weather-dependent activities
    - time references
    - local city aliases
    - global geocoding fallback
    """

    TOKEN_PATTERN = re.compile(
        r"[A-Za-z']+"
    )

    # --------------------------------------------------------------
    # Natural-language calendar dates
    #
    # Examples:
    #
    # 2nd August
    # 2 August
    # August 2
    # August 2nd
    # --------------------------------------------------------------

    MONTH_DATE_PATTERN = re.compile(
        r"\b(?:"
        r"\d{1,2}(?:st|nd|rd|th)?\s+"
        r"(?:"
        r"jan(?:uary)?|"
        r"feb(?:ruary)?|"
        r"mar(?:ch)?|"
        r"apr(?:il)?|"
        r"may|"
        r"jun(?:e)?|"
        r"jul(?:y)?|"
        r"aug(?:ust)?|"
        r"sep(?:tember)?|"
        r"oct(?:ober)?|"
        r"nov(?:ember)?|"
        r"dec(?:ember)?"
        r")"
        r"|"
        r"(?:"
        r"jan(?:uary)?|"
        r"feb(?:ruary)?|"
        r"mar(?:ch)?|"
        r"apr(?:il)?|"
        r"may|"
        r"jun(?:e)?|"
        r"jul(?:y)?|"
        r"aug(?:ust)?|"
        r"sep(?:tember)?|"
        r"oct(?:ober)?|"
        r"nov(?:ember)?|"
        r"dec(?:ember)?"
        r")\s+"
        r"\d{1,2}(?:st|nd|rd|th)?"
        r")\b",
        re.IGNORECASE,
    )

    # --------------------------------------------------------------
    # Numeric calendar dates
    #
    # Examples:
    #
    # 02/08
    # 02/08/2026
    # 02-08-2026
    # --------------------------------------------------------------

    NUMERIC_DATE_PATTERN = re.compile(
        r"\b"
        r"\d{1,2}"
        r"[/-]"
        r"\d{1,2}"
        r"(?:[/-]\d{2,4})?"
        r"\b"
    )

    # --------------------------------------------------------------
    # Candidate location extraction
    #
    # Examples:
    #
    # in Dehradun tomorrow
    # to Rio de Janeiro next week
    # visit Reykjavik
    # for Manali next week
    #
    # Note:
    #
    # "to visit Reykjavik"
    #
    # initially produces:
    #
    # "visit reykjavik"
    #
    # The candidate-normalization step below removes the leading
    # planning/action word.
    # --------------------------------------------------------------

    LOCATION_PHRASE_PATTERN = re.compile(
        r"\b"
        r"(?:in|to|at|near|visit|visiting|for)"
        r"\s+"
        r"([a-z][a-z .'-]{1,60}?)"
        r"(?="
        r"\s+(?:"
        r"today|tomorrow|tonight|"
        r"this|next|upcoming|coming|"
        r"on|during|for|in|at|to|"
        r"trip|visit|travel|trek|tour|"
        r"holiday|vacation|"
        r"week|weekend|month|day"
        r")\b"
        r"|[?.,!]"
        r"|$"
        r")",
        re.IGNORECASE,
    )

    # Words that may incorrectly become part of a captured
    # location when a preceding preposition is matched first.
    #
    # Example:
    #
    # "to visit Reykjavik"
    #
    # regex candidate:
    #     "visit reykjavik"
    #
    # normalized candidate:
    #     "reykjavik"

    LOCATION_LEADING_ACTIONS = (
        "visit ",
        "visiting ",
        "travel to ",
        "travel ",
        "trip to ",
        "trip ",
        "tour ",
        "trek to ",
        "trek ",
    )

    # Local canonical cities are cached once.

    KNOWN_CITIES = {
        city.lower()
        for city in CITY_ALIASES.values()
    }

    def __init__(
        self,
        location_lookup: (
            Callable[[str], bool]
            | None
        ) = None,
    ) -> None:
        """
        Initialize validator.

        Args:
            location_lookup:
                Optional global location lookup.

                Production:
                    Open-Meteo geocoding.

                Tests:
                    deterministic injected function.
        """

        self._location_lookup = (
            location_lookup
            or is_valid_city
        )

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate whether input belongs to the weather domain.

        Args:
            message:
                User input.

        Returns:
            ValidationResult.
        """

        if message is None:

            return ValidationResult.success()

        text = message.lower()

        # ----------------------------------------------------------
        # Rule 1
        # Explicit weather terminology.
        # ----------------------------------------------------------

        if self._contains_weather_terms(
            text
        ):

            return ValidationResult.success()

        contains_activity = (
            self._contains_weather_activity(
                text
            )
        )

        contains_time = (
            self._contains_time_reference(
                text
            )
        )

        contains_question = (
            self._contains_question_pattern(
                text
            )
        )

        # ----------------------------------------------------------
        # Fast local alias/city lookup.
        # ----------------------------------------------------------

        contains_local_city = (
            self._contains_local_city(
                text
            )
        )

        # ----------------------------------------------------------
        # Rule 2
        # Weather-dependent activity + time/local city.
        #
        # Existing behavior is intentionally preserved.
        #
        # Examples:
        #
        # trekking tomorrow
        # travel next week
        # hiking in Delhi
        # ----------------------------------------------------------

        if contains_activity:

            if (
                contains_time
                or contains_local_city
            ):

                return ValidationResult.success()

        # ----------------------------------------------------------
        # Rule 3
        # Local city + time.
        # ----------------------------------------------------------

        if (
            contains_local_city
            and contains_time
        ):

            return ValidationResult.success()

        # ----------------------------------------------------------
        # Rule 4
        # Question pattern + local city.
        # ----------------------------------------------------------

        if (
            contains_question
            and contains_local_city
        ):

            return ValidationResult.success()

        # ----------------------------------------------------------
        # Global-city fallback.
        #
        # Open-Meteo is only queried if the sentence already
        # contains planning/question/time evidence.
        #
        # Examples:
        #
        # Which day is better to visit Reykjavik?
        #
        # Can I plan for Dehradun next week?
        #
        # Dehradun trip for 2nd August
        # ----------------------------------------------------------

        should_try_global_location = any(
            (
                contains_question,
                contains_activity,
                contains_time,
            )
        )

        if should_try_global_location:

            contains_global_city = (
                self._contains_global_city(
                    text
                )
            )

            if contains_global_city:

                return ValidationResult.success()

        # ----------------------------------------------------------
        # Outside supported domain.
        # ----------------------------------------------------------

        return ValidationResult.failure(
            error_code=(
                "OUTSIDE_WEATHER_DOMAIN"
            ),
            message=(
                "This assistant only supports "
                "weather-related requests."
            ),
            validator=(
                self.__class__.__name__
            ),
            category=(
                "Domain Validation"
            ),
        )

    def _contains_weather_terms(
        self,
        text: str,
    ) -> bool:
        """
        Detect explicit weather terminology.

        Args:
            text:
                Lowercase user input.

        Returns:
            True if weather terminology is present.
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

        Args:
            text:
                Lowercase user input.

        Returns:
            True when a weather-sensitive activity is present.
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
        Detect relative and calendar time expressions.

        Supported examples:

        - tomorrow
        - next week
        - upcoming week
        - 2nd August
        - August 2
        - 02/08/2026

        Args:
            text:
                Lowercase user input.

        Returns:
            True if time/date context exists.
        """

        if any(
            value in text
            for value in TIME_TERMS
        ):

            return True

        if self.MONTH_DATE_PATTERN.search(
            text
        ):

            return True

        return bool(
            self.NUMERIC_DATE_PATTERN.search(
                text
            )
        )

    def _contains_question_pattern(
        self,
        text: str,
    ) -> bool:
        """
        Detect common weather/planning question forms.

        Args:
            text:
                Lowercase user input.

        Returns:
            True when a supported question pattern exists.
        """

        return any(
            pattern in text
            for pattern in QUESTION_PATTERNS
        )

    def _contains_local_city(
        self,
        text: str,
    ) -> bool:
        """
        Detect city using the local alias dictionary.

        Examples:

        BLR
        DEL
        BOM
        NYC
        LDN
        DXB

        Args:
            text:
                Lowercase user input.

        Returns:
            True when a local alias/canonical city is found.
        """

        tokens = self.TOKEN_PATTERN.findall(
            text
        )

        for token in tokens:

            resolved_city = resolve_city(
                token
            )

            # Local alias detected.

            if (
                resolved_city.lower()
                != token.lower()
            ):

                return True

            # Locally-known canonical city.

            if (
                resolved_city.lower()
                in self.KNOWN_CITIES
            ):

                return True

        # Multi-word cities such as:
        #
        # New York
        # Los Angeles
        # San Francisco

        return any(
            city in text
            for city in self.KNOWN_CITIES
        )

    def _normalize_location_candidate(
        self,
        candidate: str,
    ) -> str:
        """
        Normalize an extracted location phrase.

        Removes leading planning/action words that may have been
        captured because a preceding preposition matched first.

        Examples:

            visit reykjavik
                -> reykjavik

            visiting paris
                -> paris

            travel to rio de janeiro
                -> rio de janeiro

        Args:
            candidate:
                Raw extracted location candidate.

        Returns:
            Normalized location candidate.
        """

        normalized = " ".join(
            candidate.split()
        ).strip(
            " .,'-\t\n"
        )

        if not normalized:

            return ""

        changed = True

        while changed:

            changed = False

            for prefix in (
                self.LOCATION_LEADING_ACTIONS
            ):

                if normalized.startswith(
                    prefix
                ):

                    normalized = (
                        normalized[
                            len(prefix):
                        ]
                        .strip()
                    )

                    changed = True

                    break

        return normalized

    def _extract_location_candidates(
        self,
        text: str,
    ) -> tuple[str, ...]:
        """
        Extract plausible global location phrases.

        Examples:

            Can I plan for Dehradun next week?
                -> dehradun

            Which day is better to visit Reykjavik?
                -> reykjavik

            Should I travel to Rio de Janeiro tomorrow?
                -> rio de janeiro

        No LLM or NER model is required.

        Args:
            text:
                Lowercase user input.

        Returns:
            Unique location candidates.
        """

        candidates: list[str] = []

        for match in (
            self.LOCATION_PHRASE_PATTERN.finditer(
                text
            )
        ):

            candidate = (
                self._normalize_location_candidate(
                    match.group(1)
                )
            )

            if len(candidate) < 2:

                continue

            if candidate in TIME_TERMS:

                continue

            if candidate not in candidates:

                candidates.append(
                    candidate
                )

        return tuple(
            candidates
        )

    def _contains_global_city(
        self,
        text: str,
    ) -> bool:
        """
        Validate extracted location candidates globally.

        Production uses Open-Meteo geocoding.

        External failures fail closed and never crash the
        guardrail pipeline.

        Args:
            text:
                Lowercase user input.

        Returns:
            True when a valid global populated place is found.
        """

        candidates = (
            self._extract_location_candidates(
                text
            )
        )

        for candidate in candidates:

            try:

                if self._location_lookup(
                    candidate
                ):

                    return True

            except Exception:

                # Geocoding is a fallback validation mechanism.
                #
                # Network/API failures must never crash input
                # validation.

                continue

        return False