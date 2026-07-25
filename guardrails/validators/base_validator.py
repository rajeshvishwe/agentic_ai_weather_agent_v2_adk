"""
Base validator contract.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from weather_intelligence_agent_v2.guardrails.models import (
    ValidationResult,
)


class BaseValidator(ABC):
    """
    Base class for every deterministic validator.

    Each validator has one responsibility only.
    """

    @abstractmethod
    def validate(
        self,
        message: str,
    ) -> ValidationResult:
        """
        Validate user input.

        Args:
            message:
                User message.

        Returns:
            ValidationResult
        """
        raise NotImplementedError