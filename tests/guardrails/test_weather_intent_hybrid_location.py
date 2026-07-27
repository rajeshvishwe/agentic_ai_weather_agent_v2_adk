"""
Tests for hybrid local-alias and global-location weather
intent validation.

These tests never call the internet.

Global location lookup is injected into WeatherIntentValidator
so the test suite remains deterministic.
"""

from weather_intelligence_agent_v2.guardrails.validators.weather_intent_validator import (
    WeatherIntentValidator,
)


def test_short_alias_uses_local_resolution() -> None:
    """
    BLR should resolve locally without external geocoding.
    """

    external_queries: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return False

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        "Can I travel to BLR next week?"
    )

    assert result.is_valid

    assert external_queries == []


def test_global_single_word_city_is_allowed() -> None:
    """
    Cities absent from CITY_ALIASES can be accepted
    through global geocoding.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "dehradun"
            )
        )
    )

    result = validator.validate(
        (
            "Can I plan for Dehradun "
            "visit for next week?"
        )
    )

    assert result.is_valid


def test_global_city_with_plan_typo_is_allowed() -> None:
    """
    A minor typo in plan should not block clear city/time intent.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "dehradun"
            )
        )
    )

    result = validator.validate(
        (
            "Can I plant for Dehradun "
            "in upcoming week?"
        )
    )

    assert result.is_valid


def test_multi_word_global_city_is_extracted_correctly() -> None:
    """
    Multi-word global cities should remain one candidate.
    """

    queried_locations: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        queried_locations.append(
            candidate
        )

        return (
            candidate
            == "rio de janeiro"
        )

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        (
            "Which day is better "
            "for Rio de Janeiro?"
        )
    )

    assert result.is_valid

    assert (
        "rio de janeiro"
        in queried_locations
    )


def test_existing_activity_plus_time_rule_does_not_require_geocoding() -> None:
    """
    Existing activity + time behavior must remain unchanged.
    """

    external_queries: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return True

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        (
            "Should I travel to "
            "Rio de Janeiro tomorrow?"
        )
    )

    assert result.is_valid

    assert external_queries == []


def test_best_day_uses_global_city() -> None:
    """
    Comparative planning should work with global cities.
    """

    queried_locations: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        queried_locations.append(
            candidate
        )

        return (
            candidate
            == "reykjavik"
        )

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        (
            "Which day is better "
            "to visit Reykjavik?"
        )
    )

    assert result.is_valid

    assert queried_locations == [
        "reykjavik"
    ]


def test_named_calendar_date_is_supported() -> None:
    """
    Natural calendar dates should count as time context.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "dehradun"
            )
        )
    )

    result = validator.validate(
        "Dehradun trip for 2nd August"
    )

    assert result.is_valid


def test_numeric_calendar_date_is_supported() -> None:
    """
    Common numeric calendar dates should be supported.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: (
                candidate
                == "dehradun"
            )
        )
    )

    result = validator.validate(
        "Trip to Dehradun on 02/08/2026"
    )

    assert result.is_valid


def test_fake_global_location_is_blocked() -> None:
    """
    Invented locations must remain outside the domain.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        "Can I plan for Faketown next week?"
    )

    assert not result.is_valid

    assert (
        result.error_code
        == "OUTSIDE_WEATHER_DOMAIN"
    )


def test_unrelated_request_does_not_call_geocoding() -> None:
    """
    Clearly unrelated prompts should not trigger
    global location lookup.
    """

    external_queries: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        external_queries.append(
            candidate
        )

        return True

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        "Write a Python program."
    )

    assert not result.is_valid

    assert external_queries == []


def test_to_visit_location_candidate_is_cleaned() -> None:
    """
    'to visit Paris' must extract Paris rather than visit Paris.
    """

    queried_locations: list[str] = []

    def location_lookup(
        candidate: str,
    ) -> bool:

        queried_locations.append(
            candidate
        )

        return candidate == "paris"

    validator = WeatherIntentValidator(
        location_lookup=location_lookup
    )

    result = validator.validate(
        "Which day is better to visit Paris?"
    )

    assert result.is_valid

    assert queried_locations == [
        "paris"
    ]


def test_compare_two_local_cities_for_outdoor_activities() -> None:
    """
    Multi-city weather comparison must be treated as a valid
    weather-intelligence request.
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


def test_compare_two_local_cities() -> None:
    """
    Explicit comparison between known cities should be allowed.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        "Compare Delhi and Mumbai."
    )

    assert result.is_valid


def test_which_city_is_better_for_outdoor_activity() -> None:
    """
    Comparative planning wording should be accepted when
    a known city is present.
    """

    validator = WeatherIntentValidator(
        location_lookup=(
            lambda candidate: False
        )
    )

    result = validator.validate(
        (
            "Which is better for outdoor activities, "
            "Delhi or Mumbai?"
        )
    )

    assert result.is_valid


def test_generic_comparison_without_location_remains_blocked() -> None:
    """
    Adding comparison vocabulary must not turn unrelated
    comparison requests into weather requests.
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

    assert (
        result.error_code
        == "OUTSIDE_WEATHER_DOMAIN"
    )