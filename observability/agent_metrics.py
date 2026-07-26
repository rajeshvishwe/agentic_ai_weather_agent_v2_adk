"""
Prometheus metrics for Google ADK agent execution.

This module exposes low-cardinality metrics for:

- ADK execution count
- ADK execution latency
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram


ADK_EXECUTIONS_TOTAL = Counter(
    "weather_agent_adk_executions_total",
    "Total Google ADK agent executions.",
)

ADK_EXECUTION_DURATION_SECONDS = Histogram(
    "weather_agent_adk_execution_duration_seconds",
    "Google ADK agent execution duration in seconds.",
    buckets=(
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        20.0,
        30.0,
        60.0,
    ),
)