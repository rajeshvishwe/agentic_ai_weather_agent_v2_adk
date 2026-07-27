# 🌦️ Weather Intelligence Agent v2

A production-oriented **Agentic AI Weather Intelligence Platform** built with **Google ADK, Gemini, FastAPI, Streamlit, Open-Meteo, Docker, Kubernetes, Prometheus, Grafana, and OpenTelemetry**.

The project demonstrates how a conversational Generative AI application can move beyond a basic LLM chatbot into a structured, observable, guarded, containerized, and deployable AI system.

---

## 1. Project Overview

Weather Intelligence Agent v2 provides two complementary user experiences:

### 📊 Weather Dashboard

A structured weather intelligence dashboard supporting:

* Current weather
* 7-day temperature forecast
* Daily forecast
* Rain probability visualization
* Weather analytics
* AI weather intelligence and recommendations

### 💬 AI Assistant

A conversational weather assistant supporting:

* Natural-language weather questions
* Current weather
* Weather forecasts
* Multi-city comparisons
* Weather-related planning
* Multi-turn conversational context
* Contextual follow-up questions such as:

  * `What about tomorrow?`
  * `What about Mumbai?`

The application uses **FastAPI as the backend boundary**, while the Streamlit frontend communicates with the backend through a dedicated API client.

---

## 2. High-Level Architecture

```text
┌───────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│                                                           │
│     📊 Weather Dashboard        💬 AI Assistant           │
└──────────────────────────┬────────────────────────────────┘
                           │
                           │ HTTP
                           ▼
┌───────────────────────────────────────────────────────────┐
│                       FastAPI                             │
│                                                           │
│   Health │ Metrics │ Weather Planning │ Chat │ HITL       │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                  Application Services                     │
│                                                           │
│   Weather Chat │ Async Weather │ Planning │ Analytics     │
└───────────────┬───────────────────────────┬───────────────┘
                │                           │
                ▼                           ▼
┌──────────────────────────┐    ┌───────────────────────────┐
│        Guardrails        │    │        Google ADK         │
│                          │    │                           │
│ Input Validation         │    │ Root Weather Agent        │
│ Prompt Injection         │    │ Session Management        │
│ Weather Domain           │    │ Tool Orchestration        │
│ Tool Validation          │    │ Multi-turn Context        │
│ Output Validation        │    │                           │
│ HITL                     │    └──────────────┬────────────┘
└──────────────────────────┘                   │
                                               ▼
                                    ┌──────────────────────┐
                                    │        Gemini        │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │    Weather Tools     │
                                    │                      │
                                    │ Current Weather      │
                                    │ Forecast             │
                                    │ Analytics            │
                                    │ Planning             │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │      Open-Meteo      │
                                    │  External Weather API│
                                    └──────────────────────┘
```

---

## 3. Technology Stack

| Layer               | Technology              |
| ------------------- | ----------------------- |
| Agent Framework     | Google ADK              |
| LLM                 | Google Gemini           |
| Backend API         | FastAPI                 |
| Frontend            | Streamlit               |
| Weather Provider    | Open-Meteo              |
| Validation          | Pydantic                |
| Async HTTP          | aiohttp                 |
| Containerization    | Docker                  |
| Orchestration       | Kubernetes / Minikube   |
| Metrics             | Prometheus              |
| Dashboarding        | Grafana                 |
| Distributed Tracing | OpenTelemetry           |
| Testing             | pytest / pytest-asyncio |
| Language            | Python 3.13             |

---

## 4. Core Capabilities

### Agentic AI

The application uses Google ADK to provide:

* Agent execution
* Tool orchestration
* Gemini integration
* Session-aware conversations
* Multi-turn context
* Controlled tool execution
* Agent observability

### Weather Intelligence

The backend supports:

* Current weather retrieval
* Forecast retrieval
* Forecast analytics
* Weather insights
* Rain analysis
* Weather planning
* Multi-city conversational comparison
* Structured dashboard responses

### Conversational Intelligence

Example:

```text
User:
What is the current weather in Delhi?

Assistant:
The current weather in Delhi...

User:
What about tomorrow?

Assistant:
Tomorrow in Delhi...
```

The second question does not explicitly repeat the city.

Conversation context is maintained by the backend session rather than by duplicating weather reasoning inside Streamlit.

---

## 5. Streamlit User Interface

The frontend is located under:

```text
ui/
├── api_client.py
├── config.py
├── streamlit_app.py
└── components/
    ├── weather_chat.py
    └── weather_dashboard.py
```

The application provides two main views.

### 📊 Weather Dashboard

The dashboard contains:

```text
🌤️ Current Weather
📈 7-Day Temperature Forecast
📅 Daily Forecast
🌧️ Rain Probability
📊 Weather Analytics
🧠 AI Weather Intelligence
```

A user enters a city and the frontend requests structured weather intelligence from FastAPI.

The Streamlit layer remains presentation-focused and does not directly call Open-Meteo or Google ADK.

### 💬 AI Assistant

The conversational interface provides a ChatGPT-style weather experience.

Example questions:

```text
What is the current weather in Delhi?

Give me the 7-day forecast for Mumbai.

Compare the weather in Delhi and London.

Is it a good day for outdoor activities in Bengaluru?

What about tomorrow?
```

---

## 6. Request Flow

A typical conversational request follows this sequence:

```text
User
 ↓
Streamlit AI Assistant
 ↓
WeatherApiClient
 ↓
FastAPI
 ↓
Input Guardrail
 ↓
Conversation Session
 ↓
Google ADK Root Agent
 ↓
Gemini
 ↓
Weather Tool
 ↓
Open-Meteo
 ↓
Tool Result
 ↓
Gemini Response
 ↓
Output Guardrail
 ↓
FastAPI Response
 ↓
Streamlit
 ↓
User
```

A structured dashboard request follows:

```text
City
 ↓
Streamlit Weather Dashboard
 ↓
WeatherApiClient
 ↓
FastAPI Weather Planning API
 ↓
Weather Services
 ↓
Open-Meteo
 ↓
Analytics / Intelligence
 ↓
Structured Response
 ↓
Dashboard Visualizations
```

---

## 7. Google ADK Architecture

The project uses Google ADK as the agent orchestration layer.

The agent is responsible for:

* Understanding user weather intent
* Maintaining conversational context
* Selecting appropriate tools
* Calling weather functionality
* Interpreting tool results
* Producing natural-language responses

The ADK execution path is wrapped with observability and guardrail controls.

Conceptually:

```text
Input
 ↓
Input Guardrail
 ↓
ADK Session
 ↓
Root Agent
 ↓
Gemini
 ↓
Tool Selection
 ↓
Tool Guardrail
 ↓
Weather Tool
 ↓
External Weather API
 ↓
Agent Response
 ↓
Output Guardrail
 ↓
Final Response
```

---

## 8. AI Guardrails

The project contains a dedicated guardrail layer under:

```text
guardrails/
```

The implementation includes:

* Input guardrails
* Prompt-injection detection
* Weather-domain validation
* Contextual weather follow-up validation
* Tool-name validation
* Tool-argument validation
* Output guardrails
* Response-integrity validation
* Leakage validation
* Human-in-the-loop controls

### Input Validation

Requests are validated before model execution.

The goal is to prevent:

* Unsupported requests
* Prompt injection
* Invalid characters/input structures
* Out-of-domain requests

### Contextual Follow-ups

A contextual validator allows weather-related follow-up questions when a valid weather conversation already exists.

Example:

```text
What is the weather in Delhi?
What about tomorrow?
```

### Tool Guardrails

Tool execution is validated independently from model generation.

This reduces the risk of:

* Unauthorized tool names
* Invalid tool arguments
* Unexpected tool execution

### Output Guardrails

Generated model responses are validated before they are returned to the caller.

---

## 9. Human-in-the-Loop

The project contains HITL components including:

```text
guardrails/
├── approval_models.py
├── approval_service.py
├── hitl_guardrail.py
└── config/
    └── hitl_policy.py
```

FastAPI also exposes approval-related routes.

The architecture supports:

```text
Agent Tool Request
       ↓
HITL Policy
       ↓
Approval Required?
   ┌───┴────┐
   │        │
  No       Yes
   │        │
Execute   Pending Approval
            │
       ┌────┴────┐
       │         │
    Approve    Reject
```

This pattern provides a foundation for controlling sensitive agent actions.

---

## 10. FastAPI

FastAPI provides the application boundary between clients and AI/weather services.

Important API capabilities include:

```text
GET  /health
GET  /metrics

GET  /weather/plan/{city}
POST /weather/plan
POST /weather/chat
```

The project also contains HITL approval routes for retrieving and responding to approval requests.

### Health Check

Example:

```bash
curl http://localhost:8080/health
```

Example response:

```json
{
  "status": "UP",
  "application": "Weather Intelligence Agent",
  "version": "1.0.0"
}
```

---

## 11. Project Structure

```text
weather_intelligence_agent_v2/
│
├── agent.py
├── architecture.md
├── Dockerfile
├── README.md
├── requirements.txt
│
├── analytics/
│   ├── forecast_analytics.py
│   ├── insight_engine.py
│   ├── weather_analytics.py
│   └── weather_intelligence.py
│
├── api/
│   ├── app.py
│   ├── approval_routes.py
│   └── routes.py
│
├── benchmarks/
│   └── benchmark.py
│
├── config/
│   ├── city_aliases.py
│   ├── city_resolver.py
│   ├── constants.py
│   └── prompts.py
│
├── core/
│   ├── dependencies.py
│   └── settings.py
│
├── docs/
│   ├── architecture.md
│   └── eval.text
│
├── formatters/
│   └── formatter.py
│
├── guardrails/
│   ├── adk_tool_guardrail_callback.py
│   ├── approval_models.py
│   ├── approval_service.py
│   ├── hitl_guardrail.py
│   ├── input_guardrail.py
│   ├── models.py
│   ├── output_guardrail.py
│   ├── tool_guardrail.py
│   ├── weather_domain_validator.py
│   │
│   ├── config/
│   │   ├── hitl_policy.py
│   │   ├── intent_vocabulary.py
│   │   ├── output_policy.py
│   │   ├── prompt_patterns.py
│   │   ├── prompt_policy.py
│   │   └── tool_policy.py
│   │
│   └── validators/
│       ├── base_validator.py
│       ├── character_validator.py
│       ├── contextual_weather_followup_validator.py
│       ├── leakage_validator.py
│       ├── length_validator.py
│       ├── output_length_validator.py
│       ├── pipeline.py
│       ├── prompt_injection_validator.py
│       ├── response_integrity_validator.py
│       ├── tool_argument_validator.py
│       ├── tool_name_validator.py
│       └── weather_intent_validator.py
│
├── k8s/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── otel-collector-config.yaml
│   ├── otel-collector.yaml
│   ├── secret.yaml
│   ├── service.yaml
│   └── servicemonitor.yaml
│
├── observability/
│   ├── agent_metrics.py
│   ├── http_metrics.py
│   ├── logging.py
│   ├── security_metrics.py
│   ├── tool_metrics.py
│   ├── tool_tracing.py
│   ├── tracing.py
│   └── weather_api_metrics.py
│
├── services/
│   └── ...
│
├── tools/
│   └── ...
│
├── ui/
│   ├── api_client.py
│   ├── config.py
│   ├── streamlit_app.py
│   │
│   └── components/
│       ├── weather_chat.py
│       └── weather_dashboard.py
│
└── tests/
    ├── conftest.py
    ├── test_api.py
    ├── test_async_phase_7_4.py
    │
    └── guardrails/
        ├── test_adk_tool_guardrail_callback.py
        ├── test_approval_routes.py
        ├── test_approval_routes_app_integration.py
        ├── test_approval_service.py
        ├── test_hitl_approval_request_integration.py
        ├── test_hitl_callback_integration.py
        ├── test_hitl_guardrail.py
        ├── test_input_guardrail.py
        ├── test_output_guardrail.py
        ├── test_output_guardrail_api.py
        ├── test_output_guardrail_integration.py
        ├── test_prompt_injection_validator.py
        ├── test_tool_argument_validator.py
        ├── test_tool_guardrail.py
        ├── test_tool_guardrail_agent_integration.py
        ├── test_tool_name_validator.py
        └── test_weather_chat_contextual_followup.py
```

---

## 12. Local Development

### Prerequisites

Recommended environment:

```text
Python 3.13
Docker
kubectl
Minikube
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install backend dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The current Streamlit UI also requires Streamlit and Pandas. If they are not already present in the environment:

```bash
pip install streamlit pandas
```

> Note: these UI dependencies should be added to the project's dependency manifest before distributing the Streamlit frontend as part of a clean installation.

---

## 13. Environment Configuration

Create a local `.env` file.

Example:

```text
GOOGLE_API_KEY=your_google_api_key_here
```

Do not commit real API keys.

The repository's `.env.example` should contain placeholders only.

Recommended:

```text
GOOGLE_API_KEY=your_google_api_key_here
```

---

## 14. Start FastAPI Locally

From the parent directory containing the `weather_intelligence_agent_v2` package:

```bash
PYTHONPATH=/path/to/GenAI_Projects \
uvicorn weather_intelligence_agent_v2.api.app:app \
  --host 0.0.0.0 \
  --port 8080 \
  --reload
```

Verify:

```bash
curl http://localhost:8080/health
```

---

## 15. Start Streamlit

The Streamlit frontend uses the FastAPI backend.

Example:

```bash
PYTHONPATH=/path/to/GenAI_Projects \
WEATHER_API_BASE_URL=http://localhost:8080 \
python -m streamlit run \
weather_intelligence_agent_v2/ui/streamlit_app.py \
--server.port 8501
```

Open:

```text
http://localhost:8501
```

The application provides centrally accessible views for:

```text
📊 Weather Dashboard
💬 AI Assistant
```

---

## 16. Docker

The backend is containerized using Python 3.13.

Build:

```bash
docker build \
  -t weather-intelligence-agent:latest .
```

Run:

```bash
docker run -d \
  --name weather-intelligence-agent \
  -p 8081:8080 \
  --env-file .env \
  weather-intelligence-agent:latest
```

Verify:

```bash
curl http://localhost:8081/health
```

Check containers:

```bash
docker ps
```

---

## 17. Kubernetes / Minikube

Kubernetes manifests are stored under:

```text
k8s/
```

Start Minikube if required:

```bash
minikube start
```

Load the locally built image:

```bash
minikube image load \
  weather-intelligence-agent:latest
```

Apply Kubernetes resources as appropriate for the environment.

Example:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Restart after rebuilding a local image:

```bash
kubectl rollout restart \
  deployment/weather-intelligence-agent
```

Check rollout:

```bash
kubectl rollout status \
  deployment/weather-intelligence-agent
```

Check pods:

```bash
kubectl get pods
```

Check services:

```bash
kubectl get svc
```

The application service is:

```text
weather-intelligence-agent-service
```

Port-forward it:

```bash
kubectl port-forward \
  svc/weather-intelligence-agent-service \
  8083:8080
```

Verify:

```bash
curl http://localhost:8083/health
```

---

## 18. Kubernetes Secrets

Never commit production credentials directly into Kubernetes manifests.

A safe repository pattern is:

```yaml
apiVersion: v1
kind: Secret

metadata:
  name: weather-intelligence-agent-secret

type: Opaque

stringData:
  GOOGLE_API_KEY: replace-at-deployment-time
```

For real production environments, prefer a dedicated secrets-management solution.

Also remember:

> Kubernetes base64-encoded Secret values are encoding, not encryption.

---

## 19. Observability Architecture

The application includes observability at multiple layers.

```text
Weather Intelligence Agent
        │
        ├── Structured Logging
        │
        ├── Prometheus Metrics
        │       ├── HTTP
        │       ├── Agent
        │       ├── Tools
        │       ├── Weather APIs
        │       └── Security / Guardrails
        │
        └── OpenTelemetry
                ├── FastAPI
                ├── Agent execution
                ├── Tool execution
                └── External operations
```

---

## 20. Prometheus

Prometheus metrics are exposed through:

```text
/metrics
```

Example:

```bash
curl http://localhost:8083/metrics
```

The project contains metrics for areas such as:

* HTTP requests
* Agent execution
* Agent latency
* Tool execution
* Weather API activity
* Guardrail/security activity

A Kubernetes `ServiceMonitor` is provided:

```text
k8s/servicemonitor.yaml
```

---

## 21. Prometheus in Kubernetes

Inspect monitoring services:

```bash
kubectl get svc -n monitoring
```

Port-forward Prometheus:

```bash
kubectl port-forward \
  -n monitoring \
  svc/monitoring-kube-prometheus-prometheus \
  9090:9090
```

Open:

```text
http://localhost:9090
```

Basic health query:

```promql
up
```

Additional metric names should be selected from the actual `/metrics` output produced by the running application.

---

## 22. Grafana

Inspect monitoring services:

```bash
kubectl get svc -n monitoring
```

Port-forward Grafana:

```bash
kubectl port-forward \
  -n monitoring \
  svc/monitoring-grafana \
  3000:80
```

Open:

```text
http://localhost:3000
```

Grafana can visualize:

* Application health
* HTTP traffic
* Agent execution
* Agent latency
* Tool activity
* Weather API behavior
* Guardrail/security metrics

---

## 23. OpenTelemetry

OpenTelemetry instrumentation is implemented under:

```text
observability/
```

Relevant components include:

```text
tracing.py
tool_tracing.py
```

Kubernetes also includes:

```text
k8s/otel-collector.yaml
k8s/otel-collector-config.yaml
```

The observability design allows application execution to be traced across important AI and service boundaries.

Conceptually:

```text
HTTP Request
 ↓
FastAPI Span
 ↓
ADK Execution Span
 ↓
Tool Span
 ↓
Weather API
```

---

## 24. Logging

The project includes application logging configuration under:

```text
observability/logging.py
```

Logging and metrics are deliberately separated:

```text
Logs
→ detailed operational events

Metrics
→ aggregated operational measurements

Traces
→ request/execution path across components
```

---

## 25. Testing

Run the complete test suite:

```bash
pytest -q weather_intelligence_agent_v2/tests
```

Latest validated result:

```text
139 passed
```

The suite covers areas including:

* FastAPI
* Async weather planning
* Input guardrails
* Output guardrails
* Prompt-injection validation
* Tool-name validation
* Tool-argument validation
* ADK tool callbacks
* HITL
* Approval services
* Approval API routes
* Contextual conversational follow-ups

---

## 26. Example Questions

### Current Weather

```text
What is the current weather in Delhi?
```

### Forecast

```text
Give me the 7-day forecast for Mumbai.
```

### Follow-up

```text
What is the current weather in Delhi?

What about tomorrow?
```

### Comparison

```text
Compare the weather in Delhi and London.
```

### Outdoor Planning

```text
Is it a good day for outdoor activities in Bengaluru?
```

---

## 27. Security Principles

The project follows several production-oriented AI security principles:

1. Validate user input before model execution.
2. Detect prompt-injection attempts.
3. Restrict unsupported domains.
4. Validate tool names.
5. Validate tool arguments.
6. Validate model output before returning it.
7. Support human approval for sensitive operations.
8. Keep credentials outside source control.
9. Do not expose secrets through metrics or logs.
10. Avoid raw prompts as Prometheus labels.
11. Avoid session IDs as high-cardinality metric labels.
12. Avoid tool arguments as Prometheus labels.
13. Keep TLS certificate verification enabled.
14. Use deterministic security controls where possible.

---

## 28. Important Design Decisions

### FastAPI as the application boundary

Streamlit does not call Google ADK or weather providers directly.

This provides:

* Separation of concerns
* API reuse
* Easier testing
* Independent frontend evolution
* Better production architecture

### Backend-owned conversation context

Conversation context remains authoritative in the backend.

This allows contextual questions such as:

```text
What about tomorrow?
```

without forcing the frontend to reconstruct weather intent.

### Presentation-only Streamlit components

The dashboard visualizes structured backend responses.

It does not duplicate:

* Weather calculations
* Analytics logic
* Guardrails
* Agent execution

### Independent guardrail layer

Security and validation are not delegated entirely to the LLM.

Deterministic validators provide predictable controls around the probabilistic AI layer.

### Observability as an application capability

Metrics, tracing, and logging are integrated into the architecture rather than treated only as deployment infrastructure.

---

## 29. Current Limitations

The current implementation remains intentionally weather-focused.

For example, general travel operations such as hotel booking, flight booking, or complete tourism itinerary generation are outside the current weather-agent scope.

Weather-aware travel-planning intent can be expanded further in the guardrail vocabulary in a future iteration.

The Streamlit frontend also introduces UI dependencies such as Streamlit and Pandas that should be explicitly included in the project's dependency strategy for clean installation/deployment.

---

## 30. Future Enhancements

Potential next iterations include:

* Expanded weather-aware travel intent
* Production cloud deployment
* GKE deployment
* Cloud Run deployment where appropriate
* Managed secrets integration
* Persistent production conversation storage
* Distributed trace backend
* Alerting
* SLO/SLA dashboards
* Load testing
* CI/CD deployment automation
* Authentication and authorization
* Rate limiting
* Caching
* Cost/token observability
* LLM evaluation pipeline
* Advanced weather risk scoring
* Additional weather providers/fallbacks

---

## 31. Interview-Ready Project Explanation

A concise explanation:

> Weather Intelligence Agent v2 is a production-oriented Agentic AI application I built using Google ADK and Gemini. FastAPI acts as the backend application boundary, while Streamlit provides both a structured weather dashboard and conversational AI interface.
>
> The agent can understand natural-language weather requests, maintain multi-turn session context, select weather tools, retrieve external weather data, and generate contextual responses.
>
> I added deterministic input, prompt-injection, domain, tool, and output guardrails around the probabilistic LLM layer. The architecture also contains human-in-the-loop approval capabilities for controlled agent actions.
>
> From an LLMOps perspective, I instrumented the application with Prometheus metrics, Grafana dashboards, structured logging, and OpenTelemetry tracing. The application is containerized with Docker and deployed locally on Kubernetes using Minikube.
>
> The final implementation includes current weather, 7-day forecasting, analytics, rain probability, AI weather intelligence, conversational follow-ups, Docker/Kubernetes deployment, and observability. The automated regression suite currently passes 139 tests.

---

## 32. Production Engineering Concepts Demonstrated

This project demonstrates practical experience with:

```text
Agentic AI
Google ADK
Gemini
Tool Calling
Multi-turn Conversations
Session Management
FastAPI
Async Python
REST APIs
Guardrails
Prompt Injection Protection
Tool Security
Output Validation
Human-in-the-Loop
Streamlit
Weather Analytics
Docker
Kubernetes
Prometheus
Grafana
OpenTelemetry
Structured Logging
Automated Testing
LLMOps
Production AI Architecture
```

---

## 33. Final Validation Status

```text
Google ADK                  ✅
Gemini Integration          ✅
Weather Tools               ✅
FastAPI                     ✅
Async Weather Services      ✅
Input Guardrails            ✅
Prompt Injection Protection ✅
Tool Guardrails             ✅
Output Guardrails           ✅
HITL                        ✅
Contextual Follow-ups       ✅
Streamlit AI Assistant      ✅
Weather Dashboard           ✅
7-Day Forecast              ✅
Weather Analytics           ✅
Docker                      ✅
Kubernetes / Minikube       ✅
Prometheus                  ✅
Grafana                     ✅
OpenTelemetry               ✅
Automated Tests             ✅
```

Latest regression result:

```text
139 passed
```

---

## 34. Project Goal

The purpose of Weather Intelligence Agent v2 is not simply to demonstrate an LLM answering weather questions.

It demonstrates how to engineer an **end-to-end Agentic AI system** with:

```text
LLM
+
Agent Framework
+
Tools
+
External APIs
+
Conversation Context
+
Guardrails
+
Human Oversight
+
API Layer
+
User Interface
+
Containerization
+
Orchestration
+
Metrics
+
Tracing
+
Logging
+
Testing
```

That combination turns a simple AI prototype into a much more production-oriented Generative AI application.
