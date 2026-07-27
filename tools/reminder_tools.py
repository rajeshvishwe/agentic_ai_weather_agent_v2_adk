"""
Weather reminder tool exposed to Google ADK.

This tool exists primarily to demonstrate Human-in-the-Loop
approval for a user-action operation.

Unlike read-only weather tools, creating a reminder represents
an action requested on behalf of the user and therefore requires
human confirmation.

Important:

The current implementation is intentionally side-effect free.

It returns a structured reminder payload but does not yet create
an operating-system, calendar, email, or external notification.

The Google ADK before-tool callback prevents execution until
human approval is provided.

Automatic continuation after approval will be introduced in the
next HITL phase.
"""

from __future__ import annotations

from weather_intelligence_agent_v2.observability.tool_tracing import (
    trace_tool,
)


@trace_tool(
    "create_weather_reminder"
)
def create_weather_reminder(
    city: str,
    reminder_time: str,
    message: str,
) -> dict[str, str | bool]:
    """
    Create a weather-reminder payload.

    Use this tool when the user explicitly asks the assistant to
    create, set, or prepare a weather reminder.

    Examples:

    - Remind me to check Delhi weather tomorrow morning.
    - Create a weather reminder for Mumbai tomorrow.
    - Set a weather reminder for Manali this weekend.

    Args:
        city:
            Location associated with the reminder.

        reminder_time:
            User-requested reminder time.

            Examples:

            tomorrow morning
            tonight
            Saturday morning
            2 August at 8 AM

        message:
            Reminder message that should be shown to the user.

    Returns:
        Structured reminder payload.

    Notes:
        This function is side-effect free during the current HITL
        demonstration phase.
    """

    return {
        "success": True,
        "status": "created",
        "city": city,
        "reminder_time": (
            reminder_time
        ),
        "message": message,
    }