"""
Enterprise validation pipeline.

Validators are executed sequentially.
The first validation failure immediately stops execution.
"""

from __future__ import annotations

from collections.abc import Iterable

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)
from weather_intelligence_agent_v2.guardrails.validators.base_validator import (
    BaseValidator,
)


class ValidationPipeline:
    """
    Executes deterministic validators in sequence.

    The pipeline follows a fail-fast strategy. As soon as a validator
    returns an invalid result, execution stops and that result is
    returned to the caller.
    """

    def __init__(
        self,
        validators: Iterable[BaseValidator],
        *,
        debug: bool = False,
    ) -> None:
        """
        Initialise the validation pipeline.

        Args:
            validators:
                Ordered collection of validators.

            debug:
                Print validator execution details.
        """

        self._validators = list(validators)
        self._debug = debug

    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Execute validators sequentially.

        Args:
            message:
                User input.

        Returns:
            ValidationResult
        """

        if self._debug:
            print("\n========== Validation Pipeline ==========")

        for validator in self._validators:

            result = validator.validate(message)

            if self._debug:
                print(
                    f"{validator.__class__.__name__:<30}"
                    f"is_valid={result.is_valid:<5} "
                    f"error_code={result.error_code}"
                )

            if not result.is_valid:

                if self._debug:
                    print("Pipeline stopped.\n")

                return result

        if self._debug:
            print("Pipeline completed successfully.\n")

        return ValidationResult.success()