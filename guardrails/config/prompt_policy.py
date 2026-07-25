"""
Prompt security policy.

Business policies controlling prompt validation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptSecurityPolicy:
    """
    Prompt validation configuration.
    """

    max_prompt_length: int = 1000

    allow_markdown: bool = True

    allow_code_blocks: bool = True

    allow_multiple_blank_lines: bool = False

    max_consecutive_blank_lines: int = 2

    max_whitespace_ratio: float = 0.60

    reject_non_printable_characters: bool = True


DEFAULT_PROMPT_POLICY = PromptSecurityPolicy()