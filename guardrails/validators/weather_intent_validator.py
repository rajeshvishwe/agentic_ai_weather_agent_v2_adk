"""
Deterministic weather-intent validator with hybrid location resolution.

Location resolution strategy:

1. Canonical city names may be recognized directly in normal text.

2. Short aliases such as BLR, DEL, NYC, CAN, MAN, etc. are not
   globally scanned through arbitrary prose because airport codes
   may overlap with normal English words.

3. Aliases are resolved only after text has been identified as an
   actual location phrase.

4. Unknown locations are validated through the injected global
   geocoding lookup, backed by Open-Meteo in production.

5. If a request contains an apparent location, that location must
   resolve successfully before generic planning/time vocabulary can
   allow the request.
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
    Validate whether user input belongs to the weather domain.
    """

    # ==========================================================
    # DATE EXPRESSIONS
    # ==========================================================

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

    NUMERIC_DATE_PATTERN = re.compile(
        r"\b"
        r"\d{1,2}"
        r"[/-]"
        r"\d{1,2}"
        r"(?:[/-]\d{2,4})?"
        r"\b"
    )

    # ==========================================================
    # LOCATION EXTRACTION
    # ==========================================================

    LOCATION_PHRASE_PATTERN = re.compile(
        r"\b"
        r"(?:"
        r"visit|"
        r"visiting|"
        r"in|"
        r"to|"
        r"at|"
        r"near|"
        r"for"
        r")"
        r"\s+"
        r"([a-z][a-z .'-]{1,60}?)"
        r"(?="
        r"\s+(?:"
        r"today|"
        r"tomorrow|"
        r"tonight|"
        r"this|"
        r"next|"
        r"upcoming|"
        r"coming|"
        r"on|"
        r"during|"
        r"week|"
        r"weekend|"
        r"month|"
        r"day|"
        r"trip|"
        r"travel|"
        r"visit|"
        r"trek|"
        r"tour|"
        r"holiday|"
        r"vacation"
        r")\b"
        r"|"
        r"[?.,!]"
        r"|"
        r"$"
        r")",
        re.IGNORECASE,
    )

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

    # Sometimes the regex can capture the connector immediately
    # before the time expression.
    #
    # Example:
    #
    #     for Testopolis in upcoming week
    #
    # raw candidate:
    #
    #     testopolis in
    #
    # expected candidate:
    #
    #     testopolis

    LOCATION_TRAILING_CONNECTORS = (
        " in",
        " on",
        " at",
        " to",
        " for",
        " during",
        " near",
    )

    # ==========================================================
    # LOCATION DICTIONARIES
    # ==========================================================

    KNOWN_ALIASES = {
        alias.lower()
        for alias
        in CITY_ALIASES.keys()
    }

    KNOWN_CITIES = {
        city.lower()
        for city
        in CITY_ALIASES.values()
    }

    def __init__(
        self,
        location_lookup: (
            Callable[
                [str],
                bool,
            ]
            | None
        ) = None,
    ) -> None:
        """
        Initialize validator.

        Args:
            location_lookup:
                Optional location validator.

                Production:
                    Open-Meteo geocoding.

                Tests:
                    Injected deterministic function.
        """

        self._location_lookup = (
            location_lookup
            or is_valid_city
        )

    # ==========================================================
    # MAIN VALIDATION
    # ==========================================================

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate weather-domain intent.
        """

        if message is None:

            return (
                ValidationResult.success()
            )

        text = (
            message
            .strip()
            .lower()
        )

        contains_weather = (
            self._contains_weather_terms(
                text
            )
        )

        contains_question = (
            self._contains_question_pattern(
                text
            )
        )

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

        planning_context = any(
            (
                contains_weather,
                contains_question,
                contains_activity,
                contains_time,
            )
        )

        # ------------------------------------------------------
        # Known canonical city in free-form text.
        # ------------------------------------------------------

        contains_known_city = (
            self._contains_canonical_city(
                text
            )
        )

        if (
            contains_known_city
            and planning_context
        ):

            return (
                ValidationResult.success()
            )

        # ------------------------------------------------------
        # Extract explicit location candidates.
        # ------------------------------------------------------

        location_candidates = (
            self._extract_location_candidates(
                text
            )
        )

        if location_candidates:

            if not planning_context:

                return (
                    self._outside_domain()
                )

            for candidate in (
                location_candidates
            ):

                # ----------------------------------------------
                # Local alias / canonical resolution
                # ----------------------------------------------

                if self._is_local_location(
                    candidate
                ):

                    return (
                        ValidationResult.success()
                    )

                # ----------------------------------------------
                # Global geocoding fallback
                # ----------------------------------------------

                try:

                    if self._location_lookup(
                        candidate
                    ):

                        return (
                            ValidationResult.success()
                        )

                except Exception:

                    # External geocoding must never crash the
                    # deterministic guardrail pipeline.

                    continue

            # A location was supplied but could not be validated.

            return (
                self._outside_domain()
            )

        # ------------------------------------------------------
        # Explicit weather terminology without location.
        # ------------------------------------------------------

        if contains_weather:

            return (
                ValidationResult.success()
            )

        # ------------------------------------------------------
        # Location-free weather-sensitive planning.
        # ------------------------------------------------------

        if (
            contains_activity
            and contains_time
        ):

            return (
                ValidationResult.success()
            )

        return (
            self._outside_domain()
        )

    # ==========================================================
    # WEATHER VOCABULARY
    # ==========================================================

    @staticmethod
    def _contains_weather_terms(
        text: str,
    ) -> bool:
        """
        Detect explicit weather terminology.
        """

        return any(
            term in text
            for term
            in WEATHER_TERMS
        )

    @staticmethod
    def _contains_weather_activity(
        text: str,
    ) -> bool:
        """
        Detect weather-sensitive activities.
        """

        return any(
            action in text
            for action
            in WEATHER_ACTIONS
        )

    @staticmethod
    def _contains_question_pattern(
        text: str,
    ) -> bool:
        """
        Detect supported question patterns.
        """

        return any(
            pattern in text
            for pattern
            in QUESTION_PATTERNS
        )

    # ==========================================================
    # TIME RECOGNITION
    # ==========================================================

    def _contains_time_reference(
        self,
        text: str,
    ) -> bool:
        """
        Detect relative or explicit date expressions.
        """

        if any(
            term in text
            for term
            in TIME_TERMS
        ):

            return True

        if (
            self.MONTH_DATE_PATTERN
            .search(
                text
            )
        ):

            return True

        if (
            self.NUMERIC_DATE_PATTERN
            .search(
                text
            )
        ):

            return True

        return False

    # ==========================================================
    # CANONICAL CITY MATCHING
    # ==========================================================

    def _contains_canonical_city(
        self,
        text: str,
    ) -> bool:
        """
        Search canonical city names through normal prose.

        Short aliases are deliberately excluded because airport
        codes can overlap ordinary English words.
        """

        for city in (
            self.KNOWN_CITIES
        ):

            if self._contains_phrase(
                text,
                city,
            ):

                return True

        return False

    # ==========================================================
    # LOCAL LOCATION RESOLUTION
    # ==========================================================

    def _is_local_location(
        self,
        candidate: str,
    ) -> bool:
        """
        Resolve an extracted candidate through local aliases.
        """

        normalized = (
            candidate
            .strip()
            .lower()
        )

        if not normalized:

            return False

        if normalized in (
            self.KNOWN_ALIASES
        ):

            return True

        if normalized in (
            self.KNOWN_CITIES
        ):

            return True

        resolved = resolve_city(
            candidate
        )

        return (
            resolved.lower()
            in self.KNOWN_CITIES
        )

    # ==========================================================
    # PHRASE MATCHING
    # ==========================================================

    @staticmethod
    def _contains_phrase(
        text: str,
        phrase: str,
    ) -> bool:
        """
        Match complete phrase boundaries.
        """

        pattern = (
            r"(?<![a-z])"
            + re.escape(
                phrase
            )
            + r"(?![a-z])"
        )

        return bool(
            re.search(
                pattern,
                text,
                re.IGNORECASE,
            )
        )

    # ==========================================================
    # LOCATION NORMALIZATION
    # ==========================================================

    def _normalize_location_candidate(
        self,
        candidate: str,
    ) -> str:
        """
        Normalize location candidate.

        Examples:

            visit paris
                -> paris

            travel to rio de janeiro
                -> rio de janeiro

            testopolis in
                -> testopolis
        """

        normalized = " ".join(
            candidate.split()
        )

        normalized = (
            normalized.strip(
                " .,'-\t\n"
            )
        )

        if not normalized:

            return ""

        # ------------------------------------------------------
        # Remove leading planning/action terms.
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Remove trailing connector words.
        #
        # Example:
        #
        # testopolis in
        #     ↓
        # testopolis
        # ------------------------------------------------------

        changed = True

        while changed:

            changed = False

            for suffix in (
                self.LOCATION_TRAILING_CONNECTORS
            ):

                if normalized.endswith(
                    suffix
                ):

                    normalized = (
                        normalized[
                            :-
                            len(
                                suffix
                            )
                        ]
                        .strip()
                    )

                    changed = True

                    break

        return normalized

    # ==========================================================
    # LOCATION EXTRACTION
    # ==========================================================

    def _extract_location_candidates(
        self,
        text: str,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Extract plausible locations.

        Examples:

            Can I visit Testopolis next week?
                -> testopolis

            Can I plant for Testopolis in upcoming week?
                -> testopolis

            Can I plan for Faketown next week?
                -> faketown
        """

        candidates: list[
            str
        ] = []

        for match in (
            self.LOCATION_PHRASE_PATTERN
            .finditer(
                text
            )
        ):

            candidate = (
                self._normalize_location_candidate(
                    match.group(1)
                )
            )

            if (
                len(candidate)
                < 2
            ):

                continue

            if (
                candidate
                in TIME_TERMS
            ):

                continue

            if (
                candidate
                not in candidates
            ):

                candidates.append(
                    candidate
                )

        return tuple(
            candidates
        )

    # ==========================================================
    # STANDARD FAILURE
    # ==========================================================

    def _outside_domain(
        self,
    ) -> ValidationResult:
        """
        Return standard weather-domain failure.
        """

        return (
            ValidationResult.failure(
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
        )