"""
File:
weather_intelligence_agent_v2/agent.py

Purpose:
Root Google ADK agent with enterprise tool registration,
deterministic tool guardrails, and Human-in-the-Loop approval.
"""

from __future__ import annotations

import truststore

from google.adk.agents import Agent

from weather_intelligence_agent_v2.config.prompts import (
    WEATHER_AGENT_INSTRUCTION,
)
from weather_intelligence_agent_v2.guardrails.adk_tool_guardrail_callback import (
    weather_before_tool_callback,
)
from weather_intelligence_agent_v2.tools.analytics_tools import (
    analyze_weather,
)
from weather_intelligence_agent_v2.tools.forecast_tools import (
    get_forecast,
)
from weather_intelligence_agent_v2.tools.intelligence_tools import (
    get_weather_intelligence,
)
from weather_intelligence_agent_v2.tools.planning_tools import (
    get_weather_plan,
)
from weather_intelligence_agent_v2.tools.reminder_tools import (
    create_weather_reminder,
)
from weather_intelligence_agent_v2.tools.weather_tools import (
    get_current_weather,
)


truststore.inject_into_ssl()


root_agent = Agent(
    name=(
        "weather_intelligence_agent"
    ),
    model=(
        "gemini-3.1-flash-lite"
    ),
    description=(
        "Production Weather Intelligence "
        "Agent built using Google ADK."
    ),
    instruction=(
        WEATHER_AGENT_INSTRUCTION
    ),
    tools=[
        get_current_weather,
        get_forecast,
        analyze_weather,
        get_weather_intelligence,
        get_weather_plan,
        create_weather_reminder,
    ],
    before_tool_callback=(
        weather_before_tool_callback
    ),
)