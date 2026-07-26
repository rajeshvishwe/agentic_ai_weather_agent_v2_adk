"""
OpenTelemetry tracing and Prometheus metrics for Google ADK tool execution.

This module provides a reusable decorator that instruments both
synchronous and asynchronous Google ADK tool functions.

Each tool invocation:

- creates an OpenTelemetry child span
- increments the Prometheus tool-call counter
- records execution latency
- records failures when exceptions occur
- records unsuccessful structured tool results where available

Tool arguments and complete responses are intentionally excluded from
telemetry because they may contain sensitive or high-cardinality data.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any, ParamSpec, TypeVar, cast

from opentelemetry.trace import Status, StatusCode

from weather_intelligence_agent_v2.observability.tool_metrics import (
    TOOL_CALLS_TOTAL,
    TOOL_EXECUTION_DURATION_SECONDS,
    TOOL_FAILURES_TOTAL,
)
from weather_intelligence_agent_v2.observability.tracing import (
    get_tracer,
)


_P = ParamSpec("_P")
_R = TypeVar("_R")

_TRACER = get_tracer(__name__)


def _enrich_success_span(
    span: Any,
    tool_name: str,
    result: Any,
) -> bool:
    """
    Add safe execution metadata to a completed tool span.

    Args:
        span:
            Active OpenTelemetry span.

        tool_name:
            Stable logical ADK tool name.

        result:
            Tool result.

    Returns:
        bool:
            True when the tool result represents success.
            False when a structured result explicitly reports failure.
    """

    span.set_attribute(
        "genai.operation.name",
        "execute_tool",
    )

    span.set_attribute(
        "genai.tool.name",
        tool_name,
    )

    span.set_attribute(
        "genai.tool.executed",
        True,
    )

    tool_succeeded = True

    if isinstance(
        result,
        dict,
    ):
        success = result.get(
            "success"
        )

        if isinstance(
            success,
            bool,
        ):
            tool_succeeded = success

            span.set_attribute(
                "genai.tool.success",
                success,
            )

            if not success:
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        "Tool returned unsuccessful result.",
                    )
                )

    return tool_succeeded


def _record_tool_exception(
    span: Any,
    tool_name: str,
    exc: Exception,
) -> None:
    """
    Record an exception on a tool span.

    Args:
        span:
            Active OpenTelemetry span.

        tool_name:
            Stable logical ADK tool name.

        exc:
            Exception raised by the tool.
    """

    span.set_attribute(
        "genai.operation.name",
        "execute_tool",
    )

    span.set_attribute(
        "genai.tool.name",
        tool_name,
    )

    span.set_attribute(
        "genai.tool.executed",
        True,
    )

    span.set_attribute(
        "genai.tool.success",
        False,
    )

    span.record_exception(
        exc
    )

    span.set_status(
        Status(
            StatusCode.ERROR,
            str(exc),
        )
    )


def trace_tool(
    tool_name: str,
) -> Callable[
    [Callable[_P, _R]],
    Callable[_P, _R],
]:
    """
    Trace and measure execution of a Google ADK tool function.

    The decorator supports both synchronous and asynchronous tools.

    Args:
        tool_name:
            Stable logical name of the Google ADK tool.

    Returns:
        Callable:
            Decorator that instruments the supplied function.
    """

    def decorator(
        func: Callable[_P, _R],
    ) -> Callable[_P, _R]:

        if inspect.iscoroutinefunction(
            func
        ):

            @wraps(func)
            async def async_wrapper(
                *args: _P.args,
                **kwargs: _P.kwargs,
            ) -> Any:

                TOOL_CALLS_TOTAL.labels(
                    tool_name=tool_name,
                ).inc()

                start_time = perf_counter()

                try:
                    with _TRACER.start_as_current_span(
                        f"tool.{tool_name}"
                    ) as span:

                        try:
                            result = await func(
                                *args,
                                **kwargs,
                            )

                            succeeded = _enrich_success_span(
                                span=span,
                                tool_name=tool_name,
                                result=result,
                            )

                            if not succeeded:
                                TOOL_FAILURES_TOTAL.labels(
                                    tool_name=tool_name,
                                ).inc()

                            return result

                        except Exception as exc:
                            TOOL_FAILURES_TOTAL.labels(
                                tool_name=tool_name,
                            ).inc()

                            _record_tool_exception(
                                span=span,
                                tool_name=tool_name,
                                exc=exc,
                            )

                            raise

                finally:
                    TOOL_EXECUTION_DURATION_SECONDS.labels(
                        tool_name=tool_name,
                    ).observe(
                        perf_counter()
                        - start_time
                    )

            return cast(
                Callable[_P, _R],
                async_wrapper,
            )

        @wraps(func)
        def sync_wrapper(
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Any:

            TOOL_CALLS_TOTAL.labels(
                tool_name=tool_name,
            ).inc()

            start_time = perf_counter()

            try:
                with _TRACER.start_as_current_span(
                    f"tool.{tool_name}"
                ) as span:

                    try:
                        result = func(
                            *args,
                            **kwargs,
                        )

                        succeeded = _enrich_success_span(
                            span=span,
                            tool_name=tool_name,
                            result=result,
                        )

                        if not succeeded:
                            TOOL_FAILURES_TOTAL.labels(
                                tool_name=tool_name,
                            ).inc()

                        return result

                    except Exception as exc:
                        TOOL_FAILURES_TOTAL.labels(
                            tool_name=tool_name,
                        ).inc()

                        _record_tool_exception(
                            span=span,
                            tool_name=tool_name,
                            exc=exc,
                        )

                        raise

            finally:
                TOOL_EXECUTION_DURATION_SECONDS.labels(
                    tool_name=tool_name,
                ).observe(
                    perf_counter()
                    - start_time
                )

        return cast(
            Callable[_P, _R],
            sync_wrapper,
        )

    return decorator