"""
Conversational weather agent service.

This service encapsulates Google ADK runtime interaction,
conversation-session management, deterministic AI guardrails,
OpenTelemetry tracing, and Prometheus metrics for Google ADK execution.

The API and UI layers must not interact with the ADK Runner
directly.

Security boundaries:

1. Input validation occurs before Google ADK execution.
2. Output validation occurs after the final agent response is generated
   and before that response is returned to the API or UI.

Observability boundaries:

1. FastAPI creates the incoming HTTP server span.
2. WeatherChatService creates the Google ADK execution span.
3. WeatherChatService records ADK execution count and latency metrics.
4. WeatherChatService records input and output guardrail block metrics.
5. Tool and external API spans are created by lower-level instrumentation.
6. Application logs emitted inside active spans inherit OpenTelemetry
   trace and span identifiers through logging instrumentation.
"""

from __future__ import annotations

import logging
from time import perf_counter

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from weather_intelligence_agent_v2.agent import root_agent
from weather_intelligence_agent_v2.guardrails.config.output_policy import (
    SAFE_OUTPUT_FALLBACK_MESSAGE,
)
from weather_intelligence_agent_v2.guardrails.exceptions import (
    InputValidationError,
)
from weather_intelligence_agent_v2.guardrails.input_guardrail import (
    InputGuardrail,
)
from weather_intelligence_agent_v2.guardrails.output_guardrail import (
    OutputGuardrail,
)
from weather_intelligence_agent_v2.observability.agent_metrics import (
    ADK_EXECUTION_DURATION_SECONDS,
    ADK_EXECUTIONS_TOTAL,
)
from weather_intelligence_agent_v2.observability.security_metrics import (
    INPUT_GUARDRAIL_BLOCKS_TOTAL,
    OUTPUT_GUARDRAIL_BLOCKS_TOTAL,
)
from weather_intelligence_agent_v2.observability.tracing import (
    get_tracer,
)


TRACER = get_tracer(__name__)
LOGGER = logging.getLogger(__name__)


class WeatherChatService:
    """
    Application service for conversational weather intelligence.

    The service owns interaction with:

    - Google ADK Runner
    - ADK session management
    - Weather Intelligence root agent
    - deterministic input guardrails
    - deterministic output guardrails
    - OpenTelemetry ADK execution tracing
    - Prometheus ADK execution metrics
    - Prometheus guardrail block metrics

    A single service instance is intended to be application scoped.

    Input validation protects the model boundary before execution.

    Output validation protects the application boundary after the
    final model response has been generated.
    """

    APP_NAME = "weather_intelligence_agent"
    USER_ID = "streamlit_user"

    def __init__(
        self,
    ) -> None:
        """
        Initialize the application-scoped ADK runtime and guardrails.

        The ADK session service and runner are created once for the
        application-scoped WeatherChatService instance.

        Both input and output guardrails are deterministic and therefore
        require no additional LLM calls.
        """

        self._session_service = (
            InMemorySessionService()
        )

        self._runner = Runner(
            agent=root_agent,
            app_name=self.APP_NAME,
            session_service=self._session_service,
        )

        self._guardrail = InputGuardrail()

        self._output_guardrail = (
            OutputGuardrail()
        )

        # A session becomes eligible for narrow contextual follow-ups
        # only after it has successfully completed Google ADK execution.
        #
        # This remains instance-local and therefore follows the same
        # lifecycle as the existing InMemorySessionService.
        self._established_weather_sessions: set[
            str
        ] = set()

    async def chat(
        self,
        session_id: str,
        message: str,
    ) -> str:
        """
        Send a user message to the weather intelligence agent.

        Execution flow:

        1. Determine whether this session already has weather context.
        2. Validate user input.
        3. Record and reject unsafe or unsupported input.
        4. Ensure the ADK conversation session exists.
        5. Record ADK execution count and start timing.
        6. Execute the Google ADK agent inside an OpenTelemetry span.
        7. Extract the final natural-language response.
        8. Mark the session as an established weather conversation.
        9. Record ADK execution latency.
        10. Validate the generated output.
        11. Record output guardrail blocks when applicable.
        12. Return either the validated response or a safe fallback.

        Args:
            session_id:
                Conversation session identifier.

            message:
                User message.

        Returns:
            A validated natural-language response.

            If output validation fails, a deterministic safe fallback
            message is returned instead of the original model response.

        Raises:
            InputValidationError:
                If deterministic input validation rejects the user message.
        """

        allow_contextual_followup = (
            session_id
            in self._established_weather_sessions
        )

        input_validation = (
            self._guardrail.validate(
                message,
                allow_contextual_followup=(
                    allow_contextual_followup
                ),
            )
        )

        if not input_validation.is_valid:

            INPUT_GUARDRAIL_BLOCKS_TOTAL.inc()

            LOGGER.warning(
                "Input guardrail blocked a user request."
            )

            raise InputValidationError(
                input_validation.error_code,
                input_validation.message,
            )

        await self._ensure_session(
            session_id
        )

        user_message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=message,
                )
            ],
        )

        final_response = ""

        ADK_EXECUTIONS_TOTAL.inc()

        adk_start_time = perf_counter()

        try:

            with TRACER.start_as_current_span(
                "adk.agent.execute"
            ) as span:

                span.set_attribute(
                    "genai.system",
                    "google_adk",
                )

                span.set_attribute(
                    "genai.agent.name",
                    root_agent.name,
                )

                span.set_attribute(
                    "genai.application.name",
                    self.APP_NAME,
                )

                LOGGER.info(
                    "Google ADK agent execution started."
                )

                event_count = 0

                async for event in (
                    self._runner.run_async(
                        user_id=self.USER_ID,
                        session_id=session_id,
                        new_message=user_message,
                    )
                ):

                    event_count += 1

                    if (
                        event.is_final_response()
                        and event.content
                        and event.content.parts
                    ):

                        final_response = "".join(
                            part.text or ""
                            for part
                            in event.content.parts
                            if getattr(
                                part,
                                "text",
                                None,
                            )
                        )

                span.set_attribute(
                    "genai.adk.event_count",
                    event_count,
                )

                span.set_attribute(
                    "genai.response.generated",
                    bool(
                        final_response
                    ),
                )

                LOGGER.info(
                    "Google ADK agent execution completed."
                )

                self._established_weather_sessions.add(
                    session_id
                )

        finally:

            ADK_EXECUTION_DURATION_SECONDS.observe(
                perf_counter()
                - adk_start_time
            )

        output_validation = (
            self._output_guardrail.validate(
                final_response
            )
        )

        if not output_validation.is_valid:

            OUTPUT_GUARDRAIL_BLOCKS_TOTAL.inc()

            LOGGER.warning(
                "Output guardrail blocked an agent response."
            )

            return (
                SAFE_OUTPUT_FALLBACK_MESSAGE
            )

        return final_response

    async def _ensure_session(
        self,
        session_id: str,
    ) -> None:
        """
        Ensure an ADK conversation session exists.

        The existing session is reused when available.

        Otherwise, a new in-memory ADK session is created.

        Args:
            session_id:
                Conversation session identifier.
        """

        existing_session = (
            await self._session_service.get_session(
                app_name=self.APP_NAME,
                user_id=self.USER_ID,
                session_id=session_id,
            )
        )

        if existing_session is not None:
            return

        await (
            self._session_service.create_session(
                app_name=self.APP_NAME,
                user_id=self.USER_ID,
                session_id=session_id,
            )
        )