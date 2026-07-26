"""
Prometheus metrics for application security guardrails and HITL approvals.

This module exposes low-cardinality operational metrics for:

- input guardrail blocks
- output guardrail blocks
- tool guardrail blocks
- HITL approval requests
- HITL approval outcomes

Sensitive user content, prompts, tool arguments, approval request IDs,
session identifiers, and other high-cardinality values are deliberately
excluded from metric labels.
"""

from __future__ import annotations

from prometheus_client import Counter


INPUT_GUARDRAIL_BLOCKS_TOTAL = Counter(
    "weather_agent_input_guardrail_blocks_total",
    "Total requests blocked by the input guardrail.",
)


OUTPUT_GUARDRAIL_BLOCKS_TOTAL = Counter(
    "weather_agent_output_guardrail_blocks_total",
    "Total responses blocked by the output guardrail.",
)


TOOL_GUARDRAIL_BLOCKS_TOTAL = Counter(
    "weather_agent_tool_guardrail_blocks_total",
    "Total tool execution requests blocked by tool guardrails.",
    labelnames=(
        "validation_stage",
    ),
)


HITL_APPROVAL_REQUESTS_TOTAL = Counter(
    "weather_agent_hitl_approval_requests_total",
    "Total HITL approval requests created.",
    labelnames=(
        "approval_level",
    ),
)


HITL_APPROVAL_OUTCOMES_TOTAL = Counter(
    "weather_agent_hitl_approval_outcomes_total",
    "Total HITL approval outcomes.",
    labelnames=(
        "status",
    ),
)