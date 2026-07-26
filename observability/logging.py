"""
OpenTelemetry log-correlation configuration.

This module enriches standard Python logging records with the active
OpenTelemetry trace context.

When a log message is emitted inside an active trace/span, OpenTelemetry
injects:

- trace ID
- span ID
- service name
- trace sampling state

The module does not export logs. Existing application logs continue to flow
through the configured Python logging handlers and container stdout/stderr.
"""

from __future__ import annotations

from opentelemetry.instrumentation.logging import (
    LoggingInstrumentor,
)


_LOGGING_CONFIGURED = False


def configure_log_correlation() -> None:
    """
    Enable OpenTelemetry trace-context injection into Python log records.

    The instrumentation configures a log format containing OpenTelemetry
    correlation fields and installs the logging record instrumentation.

    Repeated calls are ignored so application startup remains idempotent.
    """

    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    LoggingInstrumentor().instrument(
        set_logging_format=True,
        logging_format=(
            "%(asctime)s "
            "%(levelname)s "
            "[%(name)s] "
            "[trace_id=%(otelTraceID)s "
            "span_id=%(otelSpanID)s "
            "service=%(otelServiceName)s "
            "sampled=%(otelTraceSampled)s] "
            "%(message)s"
        ),
    )

    _LOGGING_CONFIGURED = True