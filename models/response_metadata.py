"""
File:
weather_intelligence_agent_v2/models/response_metadata.py

Phase:
6.9 – Structured Outputs

Purpose:
Metadata associated with a generated weather planning
response.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class ResponseMetadata:
    """
    Metadata describing a generated response.
    """

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    version: str = "1.0"