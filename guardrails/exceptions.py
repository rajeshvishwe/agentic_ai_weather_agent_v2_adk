"""
Custom exceptions for enterprise guardrails.
"""

from __future__ import annotations


class InputValidationError(ValueError):
    """
    Raised when deterministic validation fails.
    """

    def __init__(
        self,
        error_code: str,
        message: str,
    ) -> None:

        super().__init__(message)

        self.error_code = error_code
        self.message = message