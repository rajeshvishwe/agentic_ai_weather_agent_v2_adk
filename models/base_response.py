"""
File:
weather_intelligence_agent_v2/models/base_response.py

Phase:
6.9 – Structured Outputs

Purpose:
Base response model shared by all structured
AI response models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class BaseResponse:
    """
    Base class for structured AI responses.
    """

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    status: str = "SUCCESS"

    version: str = "1.0"