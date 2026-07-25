"""
Conversational weather agent service.

This service encapsulates Google ADK runtime interaction,
conversation-session management, and deterministic AI guardrails.

The API and UI layers must not interact with the ADK Runner
directly.

Security boundaries:

1. Input validation occurs before Google ADK execution.
2. Output validation occurs after the final agent response is generated
   and before that response is returned to the API or UI.
"""

from __future__ import annotations

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


class WeatherChatService:
    """
    Application service for conversational weather intelligence.

    The service owns interaction with:

    - Google ADK Runner
    - ADK session management
    - Weather Intelligence root agent
    - deterministic input guardrails
    - deterministic output guardrails

    A single service instance is intended to be application scoped.

    Input validation protects the model boundary before execution.
    Output validation protects the application boundary after the
    final model response has been generated.
    """

    APP_NAME = "weather_intelligence_agent"
    USER_ID = "streamlit_user"

    def __init__(self) -> None:
        """
        Initialize the application-scoped ADK runtime and guardrails.

        The ADK session service and runner are created once for the
        application-scoped WeatherChatService instance.

        Both input and output guardrails are deterministic and therefore
        require no additional LLM calls.
        """

        self._session_service = InMemorySessionService()

        self._runner = Runner(
            agent=root_agent,
            app_name=self.APP_NAME,
            session_service=self._session_service,
        )

        # Phase 9.2 — Input Guardrails
        self._guardrail = InputGuardrail()

        # Phase 9.3 — Output Guardrails
        self._output_guardrail = OutputGuardrail()

    async def chat(
        self,
        session_id: str,
        message: str,
    ) -> str:
        """
        Send a user message to the weather intelligence agent.

        Execution flow:

        1. Validate user input.
        2. Reject unsafe or unsupported input before model execution.
        3. Ensure the ADK conversation session exists.
        4. Execute the Google ADK agent.
        5. Extract the final natural-language response.
        6. Validate the generated output.
        7. Return either the validated response or a safe fallback.

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
                If Phase 9.2 input validation rejects the user message.
        """

        # ------------------------------------------------------------
        # Phase 9.2 — Input validation
        # ------------------------------------------------------------

        input_validation = self._guardrail.validate(message)

        if not input_validation.is_valid:
            raise InputValidationError(
                input_validation.error_code,
                input_validation.message,
            )

        # ------------------------------------------------------------
        # ADK session handling
        # ------------------------------------------------------------

        await self._ensure_session(session_id)

        user_message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=message,
                )
            ],
        )

        final_response = ""

        # ------------------------------------------------------------
        # Google ADK execution
        # ------------------------------------------------------------

        async for event in self._runner.run_async(
            user_id=self.USER_ID,
            session_id=session_id,
            new_message=user_message,
        ):
            if (
                event.is_final_response()
                and event.content
                and event.content.parts
            ):
                final_response = "".join(
                    part.text or ""
                    for part in event.content.parts
                    if getattr(part, "text", None)
                )

        # ------------------------------------------------------------
        # Phase 9.3 — Output validation
        # ------------------------------------------------------------

        output_validation = self._output_guardrail.validate(
            final_response
        )

        if not output_validation.is_valid:
            return SAFE_OUTPUT_FALLBACK_MESSAGE

        return final_response

    async def _ensure_session(
        self,
        session_id: str,
    ) -> None:
        """
        Ensure an ADK conversation session exists.

        The existing session is reused when available. Otherwise,
        a new in-memory ADK session is created.

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

        await self._session_service.create_session(
            app_name=self.APP_NAME,
            user_id=self.USER_ID,
            session_id=session_id,
        )