"""
Configuration policy for deterministic output guardrails.

This module contains security and response-validation constants used by
Phase 9.3 output validators.

The policy is intentionally deterministic. It does not require an
additional LLM call, which keeps validation predictable, testable,
auditable, and inexpensive.
"""

from __future__ import annotations


# Maximum number of characters allowed in a final conversational response.
#
# Weather responses should normally remain well below this value.
# The limit primarily protects against accidental runaway generation,
# malformed responses, excessive payload sizes, and UI/logging pressure.
MAX_OUTPUT_LENGTH = 8_000


# Deterministic message that may later be returned to the user when an
# unsafe model response is rejected by the output guardrail.
SAFE_OUTPUT_FALLBACK_MESSAGE = (
    "I couldn't safely process the generated weather response. "
    "Please try your weather request again."
)


# Patterns indicating possible disclosure of internal model instructions.
#
# These deliberately focus on explicit disclosure-style language rather
# than generic words such as "system" or "instructions", which could
# otherwise produce unnecessary false positives.
INSTRUCTION_LEAKAGE_PATTERNS: tuple[str, ...] = (
    r"\bmy\s+system\s+prompt\b",
    r"\bthe\s+system\s+prompt\s+(?:is|says|contains)\b",
    r"\bsystem\s+prompt\s*:",
    r"\bmy\s+developer\s+(?:prompt|instructions?)\b",
    r"\bdeveloper\s+(?:prompt|instructions?)\s*:",
    r"\bmy\s+hidden\s+instructions?\b",
    r"\bhidden\s+instructions?\s*:",
    r"\bmy\s+internal\s+instructions?\b",
    r"\binternal\s+instructions?\s*:",
)


# Patterns indicating attempted disclosure of private reasoning.
REASONING_LEAKAGE_PATTERNS: tuple[str, ...] = (
    r"\bmy\s+chain[-\s]of[-\s]thought\b",
    r"\bchain[-\s]of[-\s]thought\s*:",
    r"\bmy\s+internal\s+reasoning\b",
    r"\binternal\s+reasoning\s*:",
    r"\bmy\s+private\s+reasoning\b",
    r"\bprivate\s+reasoning\s*:",
)


# Patterns indicating common secret or credential disclosure formats.
#
# These patterns intentionally target assignment or authorization formats
# rather than simply detecting the words "API key" or "token".
SECRET_LEAKAGE_PATTERNS: tuple[str, ...] = (
    r"\bGOOGLE_API_KEY\s*=\s*[^\s]+",
    r"\bGEMINI_API_KEY\s*=\s*[^\s]+",
    r"\bOPENAI_API_KEY\s*=\s*[^\s]+",
    r"\bANTHROPIC_API_KEY\s*=\s*[^\s]+",
    r"\bSERPER_API_KEY\s*=\s*[^\s]+",
    r"\bAPI_KEY\s*=\s*[^\s]+",
    r"\bSECRET_KEY\s*=\s*[^\s]+",
    r"\bACCESS_TOKEN\s*=\s*[^\s]+",
    r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}",
)