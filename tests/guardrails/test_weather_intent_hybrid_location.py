"""
Tests for hybrid local-alias and global-location weather intent
validation.

No test in this file calls the real internet.

The global location lookup is injected so tests remain deterministic
and are unaffected when CITY_ALIASES grows in the future.
"""

from weather_intelligence_agent_v2.guardrails.validators.weather_intent_validator import (
    WeatherIntentValidator,
)


def test_short_alias_uses_local_resolution() -> None:
    """
    BLR must resolve locally.
    """

    external_queries: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return False

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        "Can I travel to BLR next week?"
    )

    assert result.is_valid

    assert external_queries == []


def test_known_canonical_city_uses_local_resolution() -> None:
    """
    Delhi should resolve locally.
    """

    external_queries: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return False

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        "Can I visit Delhi next week?"
    )

    assert result.is_valid

    assert external_queries == []


def test_global_single_word_location_uses_fallback() -> None:
    """
    Synthetic place name verifies the fallback mechanism itself.

    Using a synthetic value prevents this test from breaking when
    the production alias dictionary later adds another real city.
    """

    queried: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        queried.append(
            candidate
        )

        return (
            candidate
            == "testopolis"
        )

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        (
            "Can I visit Testopolis "
            "next week?"
        )
    )

    assert result.is_valid

    assert queried == [
        "testopolis"
    ]


def test_global_multi_word_location_uses_fallback() -> None:
    """
    Multi-word location must remain a single lookup candidate.
    """

    queried: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        queried.append(
            candidate
        )

        return (
            candidate
            == "sample valley"
        )

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        (
            "Which day is better "
            "for Sample Valley?"
        )
    )

    assert result.is_valid

    assert queried == [
        "sample valley"
    ]


def test_to_visit_candidate_is_cleaned() -> None:
    """
    'to visit Demo City' must resolve to 'demo city'.
    """

    queried: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        queried.append(
            candidate
        )

        return (
            candidate
            == "demo city"
        )

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        (
            "Which day is better "
            "to visit Demo City?"
        )
    )

    assert result.is_valid

    assert queried == [
        "demo city"
    ]


def test_global_location_with_plan_typo_is_allowed() -> None:
    """
    Typo in 'plan' should not affect clear location + time intent.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "testopolis"
            )
        )
    )

    result = validator.validate(
        (
            "Can I plant for Testopolis "
            "in upcoming week?"
        )
    )

    assert result.is_valid


def test_numeric_calendar_date_is_supported() -> None:
    """
    Numeric date must be recognized as planning context.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "testopolis"
            )
        )
    )

    result = validator.validate(
        (
            "Trip to Testopolis "
            "on 02/08/2026"
        )
    )

    assert result.is_valid


def test_fake_global_location_is_blocked() -> None:
    """
    Critical regression:

    CAN must not be interpreted as Guangzhou from the normal word
    'Can' at the beginning of the sentence.
    """

    queried: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        queried.append(
            candidate
        )

        return False

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        (
            "Can I plan for Faketown "
            "next week?"
        )
    )

    assert not result.is_valid

    assert (
        result.error_code
        == "OUTSIDE_WEATHER_DOMAIN"
    )

    assert queried == [
        "faketown"
    ]


def test_can_word_is_not_guangzhou_alias() -> None:
    """
    Regression test for CAN airport-code collision.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        (
            "Can I plan for Faketown "
            "next week?"
        )
    )

    assert not result.is_valid


def test_unrelated_request_does_not_call_geocoding() -> None:
    """
    Non-weather prompts must not create external lookups.
    """

    external_queries: list[str] = []

    def lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return True

    validator = WeatherIntentValidator(
        location_lookup=lookup
    )

    result = validator.validate(
        "Write a Python program."
    )

    assert not result.is_valid

    assert external_queries == []


def test_weather_activity_with_time_without_city_is_allowed() -> None:
    """
    Location-free weather-sensitive planning remains supported.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        "Can I go trekking tomorrow?"
    )

    assert result.is_valid


def test_compare_known_cities_is_allowed() -> None:
    """
    Known-city comparison remains supported.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        (
            "Compare Bengaluru and Mumbai "
            "for outdoor activities."
        )
    )

    assert result.is_valid


def test_generic_comparison_is_blocked() -> None:
    """
    Generic comparisons must remain outside weather domain.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        "Compare Python and Java."
    )

    assert not result.is_valid