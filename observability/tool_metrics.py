"""
Prometheus metrics for Google ADK tool execution.

This module exposes low-cardinality operational metrics for:

- tool invocation count
- tool execution duration
- tool failures

The only metric label is the stable tool name.
Tool arguments, cities, prompts, responses, and session identifiers
are deliberately excluded to avoid high-cardinality metrics.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram


TOOL_CALLS_TOTAL = Counter(
    "weather_agent_tool_calls_total",
    "Total Google ADK tool invocations.",
    labelnames=(
        "tool_name",
    ),
)


TOOL_FAILURES_TOTAL = Counter(
    "weather_agent_tool_failures_total",
    "Total failed Google ADK tool invocations.",
    labelnames=(
        "tool_name",
    ),
)


TOOL_EXECUTION_DURATION_SECONDS = Histogram(
    "weather_agent_tool_execution_duration_seconds",
    "Google ADK tool execution duration in seconds.",
    labelnames=(
        "tool_name",
    ),
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        20.0,
        30.0,
    ),
)