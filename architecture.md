--to start backend server & trigger UI:

--To start server: (in parent directory) in mac-os

PYTHONPATH=/Users/rajeshvishwe/GenAI_Projects \
uvicorn weather_intelligence_agent_v2.api.app:app \
--host 0.0.0.0 \
--port 8082 \
--reload

--To start UI:

PYTHONPATH=/Users/rajeshvishwe/GenAI_Projects \
WEATHER_API_BASE_URL=http://localhost:8082 \
streamlit run weather_intelligence_agent_v2/ui/streamlit_app.py
2026-07-26 19:27:58.537 Uvicorn server started on :::8501

in windows : (parent directory - main folder)

to server: 
uvicorn weather_intelligence_agent_v2.api.app:app --host 0.0.0.0 --port 8082 --reload

to UI: 
1) python -m streamlit run weather_intelligence_agent_v2\ui\streamlit_app.py

2) 
$env:PYTHONPATH="C:\p\google_adk_projects"
$env:WEATHER_API_BASE_URL="http://localhost:8082"

python -m streamlit run weather_intelligence_agent_v2\ui\streamlit_app.py

Phase 13.1 — Final Architecture Summary

┌───────────────────────────────────────────────┐
│              Streamlit Frontend               │
│                                               │
│   📊 Weather Dashboard   💬 AI Assistant      │
└──────────────────────┬────────────────────────┘
                       │ HTTP
                       ▼
┌───────────────────────────────────────────────┐
│                 FastAPI Layer                 │
│                                               │
│  /health   /metrics   weather APIs   chat API │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│             Application Services              │
│                                               │
│  WeatherChatService                           │
│  AsyncWeatherService                          │
│  Weather Planning / Analytics Services        │
└───────────────┬───────────────────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐   ┌──────────────────────────┐
│  Guardrails  │   │       Google ADK         │
│              │   │                          │
│ Input        │   │ Root Weather Agent       │
│ Injection    │   │ Session Management       │
│ Domain       │   │ Multi-turn Context       │
│ Output       │   │ Tool Orchestration       │
└──────────────┘   └─────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Gemini LLM         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Weather Tools       │
                    │                         │
                    │ Current Weather         │
                    │ 7-Day Forecast          │
                    │ Weather Analytics       │
                    │ Planning Intelligence   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Open-Meteo        │
                    │   External Weather API  │
                    └─────────────────────────┘

Production/LLMops Layer:

Application
     │
     ├── OpenTelemetry
     │       └── traces / instrumentation
     │
     ├── Prometheus
     │       ├── HTTP metrics
     │       ├── ADK execution count
     │       ├── ADK execution latency
     │       └── Guardrail metrics
     │
     └── Grafana
             └── operational dashboards

Deployment:


Source Code
    ↓
Docker Image
    ↓
Kubernetes / Minikube
    ↓
Service
    ↓
Prometheus ServiceMonitor
    ↓
Grafana


Major capabilities completed

Agentic AI

Google ADK agent orchestration
Gemini integration
Tool calling
Stateful multi-turn conversations
Contextual follow-ups such as What about tomorrow?

Weather intelligence

Current conditions
7-day forecast
Temperature trend visualization
Daily forecast
Rain probability
Weather analytics
AI-generated planning recommendations
Multi-city conversational comparisons

Enterprise safeguards

Input validation
Prompt-injection protection
Domain guardrails
Output validation
Safe fallback responses

Production engineering

FastAPI service layer
Async weather services
Docker
Kubernetes
Prometheus
Grafana
OpenTelemetry
Structured logging
Automated tests