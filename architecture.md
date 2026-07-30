## ADK
terminal: adk web
url: http://127.0.0.1:8000 

## UI app (macos)

# terminal 1: (FastAPI server)
cd /Users/rajeshvishwe/GenAI_Projects/climate_tech
source /Users/rajeshvishwe/GenAI_Projects/.venv/bin/activate

PYTHONPATH=/Users/rajeshvishwe/GenAI_Projects/climate_tech \
uvicorn weather_intelligence_agent_v2.api.app:app \
  --host 0.0.0.0 \
  --port 8082 \
  --reload

# terminal 2: 
cd /Users/rajeshvishwe/GenAI_Projects/climate_tech
source /Users/rajeshvishwe/GenAI_Projects/.venv/bin/activate

PYTHONPATH=/Users/rajeshvishwe/GenAI_Projects/climate_tech \
WEATHER_API_BASE_URL=http://localhost:8082 \
python -m streamlit run \
  weather_intelligence_agent_v2/ui/streamlit_app.py \
  --server.port 8501

## Example:
1) How windy is Delhi today?
2) How much rainfall is expected in Hyderabad this week?
3) Give me the 5-day weather forecast for Pune.
4) Is tomorrow a good day for trekking in Manali?
## HITL (Human Approval)
1) create a reminder to walking tomorrow in delhi
2) when rain is high in Delhi, create reminder tomorrow ?

# windows : (parent directory - main folder)
to server: 
uvicorn weather_intelligence_agent_v2.api.app:app --host 0.0.0.0 --port 8082 --reload
to UI: 
1) python -m streamlit run weather_intelligence_agent_v2\ui\streamlit_app.py
2) 
$env:PYTHONPATH="C:\p\google_adk_projects"
$env:WEATHER_API_BASE_URL="http://localhost:8082"
python -m streamlit run weather_intelligence_agent_v2\ui\streamlit_app.py


### Observability (logging,monitoring,latency,tracing,metrics)

## open Grafana: 

# terminal: 
kubectl port-forward \
-n monitoring \
svc/monitoring-grafana \
3000:80
# url:
http://localhost:3000

## then select dashboard created by me

userid: admin
pwd: pxhuQdfLRJ3FhP15vB1bmMgyOaxldp3ZEpa21WEf

## Open Prometheus
# terminal:
kubectl port-forward \
-n monitoring \
svc/monitoring-kube-prometheus-prometheus \
9090:9090
# url
http://localhost:9090

# sample query:
rate(container_cpu_usage_seconds_total[5m])
kube_pod_status_phase{phase="Running"}
100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

## Final Architecture Summary

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

## Production/LLMops Layer:

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

## Deployment:
Source Code
    ↓
Docker Image (containarization)
    ↓
Kubernetes / Minikube (code deployed)
    ↓
Service
    ↓
Prometheus ServiceMonitor (for PromQL query)
    ↓
Grafana (web analytics dashboard)