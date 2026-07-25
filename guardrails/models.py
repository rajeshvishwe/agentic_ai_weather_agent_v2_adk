"""
Shared models used by the guardrail pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ValidationSeverity(str, Enum):
    """
    Severity assigned to validation failures.
    """

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class ValidationResult:
    """
    Result produced by a validator.
    """

    is_valid: bool

    error_code: Optional[str] = None

    message: Optional[str] = None

    validator: Optional[str] = None

    category: Optional[str] = None

    severity: ValidationSeverity = ValidationSeverity.ERROR

    @classmethod
    def success(cls) -> "ValidationResult":

        return cls(is_valid=True)

    @classmethod
    def failure(
        cls,
        *,
        error_code: str,
        message: str,
        validator: str,
        category: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "ValidationResult":

        return cls(
            is_valid=False,
            error_code=error_code,
            message=message,
            validator=validator,
            category=category,
            severity=severity,
        )