# Weather Intelligence Agent v2

> Production-style Agentic AI weather intelligence application built with Google ADK, Gemini, FastAPI, async Python, Docker, Kubernetes, Prometheus, Grafana, OpenTelemetry, deterministic guardrails, and HITL.

**Current release:** Phase 11 complete · **Automated tests:** 129 passed · **Phase 12:** Deferred

---


## 1. Project Overview


Weather Intelligence Agent v2 is an enterprise-style Generative AI and
Agentic AI application for conversational weather intelligence.

The project combines Google ADK, Gemini, FastAPI, asynchronous Python
services, external weather APIs, deterministic AI guardrails,
human-in-the-loop approval capabilities, Docker, Kubernetes, Prometheus,
Grafana, and OpenTelemetry.

The application accepts natural-language weather questions, executes an
agentic workflow, calls weather tools and external APIs when required,
and returns a validated natural-language response.

**Example request:**


```text
What is the current weather in Delhi?
```

**Example response:**


```text
The current weather in Delhi is overcast with a temperature of 33°C.
The wind is blowing at 2.5 km/h from the east-northeast.
```


## 2. High-Level Architecture


User / Client | v FastAPI | v WeatherChatService | +———————-+ | Input
Guardrail | +———————-+ | v Google ADK Runner | v Weather Intelligence
Agent | +———————-+ | Tool Guardrail | | HITL Approval | +———————-+ | v
Async Weather Services | v Open-Meteo APIs | v Agent Response | v Output
Guardrail | v FastAPI Response

**Observability:**

FastAPI / ADK / Tools / Weather APIs / Guardrails / HITL | +–>
Prometheus –> Grafana | +–> OpenTelemetry –> OTEL Collector | +–>
Application Logs

**Deployment:**

Application | v Docker Image | v Kubernetes / Minikube | +–> Deployment
+–> Service +–> ConfigMap +–> Secret +–> ServiceMonitor +–>
OpenTelemetry Collector


## 3. Core Technology Stack


Language: - Python 3.13

Agentic AI: - Google Agent Development Kit (Google ADK) - Gemini /
Google GenAI integration - ADK Runner - ADK session management - ADK
tool execution

API: - FastAPI - Uvicorn

Data validation and models: - Pydantic-based application models

Async processing: - asyncio - aiohttp

Weather provider: - Open-Meteo Geocoding API - Open-Meteo Forecast API

Security: - Input guardrails - Output guardrails - Tool guardrails -
Human-in-the-loop approval workflow

Containerization: - Docker - ARM64 image support

Orchestration: - Kubernetes - Minikube

Monitoring: - Prometheus - kube-prometheus-stack - Grafana

Observability: - OpenTelemetry - OTEL Collector - Prometheus metrics -
structured application logging - trace/log correlation

Testing: - pytest - asynchronous integration tests - guardrail tests -
API and integration tests


## 4. Important Application Components


4.1 Google ADK Agent

The root agent represents the primary conversational weather agent.

Google ADK provides: - agent orchestration - model interaction - tool
invocation - event streaming - conversation execution

WeatherChatService intentionally encapsulates ADK Runner access so that
the API and UI layers do not communicate directly with the ADK runtime.

4.2 WeatherChatService

WeatherChatService is the application service responsible for: - input
validation - ADK session management - ADK execution - final response
extraction - output validation - ADK tracing - ADK execution metrics -
guardrail metrics

**Typical execution flow:**


## 1. Receive Session Id And Message.


## 2. Validate The User Input.


## 3. Reject Invalid Input Before Model Execution.


## 4. Ensure An Adk Conversation Session Exists.


## 5. Increment Adk Execution Metrics.


## 6. Start An Opentelemetry Adk Span.


## 7. Execute The Root Agent.


## 8. Extract The Final Adk Response.


## 9. Record Adk Latency.


## 10. Validate The Generated Response.


## 11. Return The Validated Response Or Safe Fallback.


4.3 Async Weather Service

The asynchronous weather service communicates with external Open-Meteo
APIs.

The service supports: - location/geocoding lookup - current weather
retrieval - forecast retrieval - concurrent weather operations -
timeout/error handling - OpenTelemetry spans - Prometheus
request/failure/latency metrics

The asynchronous design allows multiple independent weather operations
to run without blocking the application’s event loop.

4.4 Async Weather Planning

The project includes asynchronous weather planning/orchestration capable
of coordinating weather operations across multiple cities.

Integration tests validate: - current weather - forecast - multi-city
weather - asynchronous weather planning


## 5. Ai Guardrails


The project uses deterministic guardrails instead of adding unnecessary
LLM calls for security decisions.

5.1 Input Guardrail

Input validation executes before Google ADK.

If validation fails: - ADK execution is prevented - InputValidationError
is raised - Prometheus input-block metric is incremented

**Metric:**


```text
weather_agent_input_guardrail_blocks_total
```

5.2 Output Guardrail

Output validation executes after the agent produces its final response
but before the response reaches the API/UI boundary.

If validation fails, the application returns a deterministic safe
fallback message.

**Metric:**


```text
weather_agent_output_guardrail_blocks_total
```

5.3 Tool Guardrail

ToolGuardrail uses fail-fast deterministic validation.

**Validation sequence:**


```text
ToolNameValidator
       |
       v
ToolArgumentValidator
```

If tool-name validation fails, argument validation is not executed.

Blocked tool operations are classified using low-cardinality
**validation-stage labels:**


```text
validation_stage="tool_name"
validation_stage="tool_arguments"
```

**Metric:**


```text
weather_agent_tool_guardrail_blocks_total
```


## 6. Human-In-The-Loop (Hitl)


ApprovalService provides an in-memory human approval workflow.

Supported operations: - create_request() - get_request() - approve() -
reject()

The implementation is intentionally lightweight for local development
and learning. A distributed persistence layer can replace the in-memory
store in a future production-hardening phase.

**Prometheus metrics:**


```text
weather_agent_hitl_approval_requests_total

weather_agent_hitl_approval_outcomes_total
```

**Outcome labels include:**


```text
status="approved"
status="rejected"
```

Sensitive request IDs and tool arguments are not exposed as Prometheus
labels.


## 7. Fastapi


FastAPI provides the HTTP application boundary.

**Validated endpoints during the project include:**

**Health:**


```text
GET /health
```

**Example:**


```text
curl http://localhost:8000/health
```

**Expected structure:**


```text
{
  "status": "UP",
  "application": "Weather Intelligence Agent",
  "version": "1.0.0"
}
```

**Weather conversation:**


```text
POST /weather/chat
```

**Example:**


```text
curl -X POST "http://localhost:8000/weather/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "weather-test-001",
    "message": "What is the current weather in Delhi?"
  }'
```

**Prometheus metrics:**


```text
GET /metrics
```

**Example:**


```text
curl http://localhost:8000/metrics
```


## 8. Prometheus Metrics


The application exposes operational metrics across several layers.

8.1 HTTP Metrics

**Examples include:**


```text
weather_agent_http_requests_total
weather_agent_http_errors_total
weather_agent_http_request_duration_seconds
```

These provide: - request volume - HTTP failures - request latency

8.2 ADK Metrics


```text
weather_agent_adk_executions_total
weather_agent_adk_execution_duration_seconds
```

These measure: - agent executions - ADK execution latency

8.3 Tool Metrics

**Examples include:**


```text
weather_agent_tool_calls_total
weather_agent_tool_failures_total
weather_agent_tool_execution_duration_seconds
```

These provide: - tool invocation count - tool failure count - tool
execution latency

8.4 External Weather API Metrics


```text
weather_agent_weather_api_requests_total
weather_agent_weather_api_failures_total
weather_agent_weather_api_duration_seconds
```

**Endpoint labels include:**


```text
endpoint="geocoding"
endpoint="forecast"
```

During validation, both geocoding and forecast requests were
successfully visible through the /metrics endpoint.

8.5 Security Metrics


```text
weather_agent_input_guardrail_blocks_total
weather_agent_output_guardrail_blocks_total
weather_agent_tool_guardrail_blocks_total
```

8.6 HITL Metrics


```text
weather_agent_hitl_approval_requests_total
weather_agent_hitl_approval_outcomes_total
```


## 9. Opentelemetry


OpenTelemetry provides distributed tracing across important application
boundaries.

Instrumentation implemented through Phase 11 covers: - incoming FastAPI
requests - Google ADK execution - tool execution - external weather API
operations - application logging correlation

**Conceptual trace:**


```text
HTTP request
    |
    v
FastAPI server span
    |
    v
adk.agent.execute
    |
    v
tool span
    |
    v
external weather API span
```

ADK span attributes include concepts such as: - genai.system -
genai.agent.name - genai.application.name - ADK event count - whether a
final response was generated

The project also includes OpenTelemetry Collector Kubernetes
configuration.


## 10. Logging


Application logging is integrated with observability instrumentation.

Logs generated inside active spans can inherit trace/span identifiers,
supporting correlation between: - logs - traces - application operations

Examples of logged events include: - ADK execution started - ADK
execution completed - guardrail blocks

Sensitive prompt content should not be unnecessarily placed into logs or
metric labels.


## 11. Docker


The application is containerized with Docker.

**Final validated development image tag:**


```text
weather-intelligence-agent:v2.3-arm64
```

**Build:**


```text
docker build \
  --platform linux/arm64 \
  -t weather-intelligence-agent:v2.3-arm64 .
```

**Verify image architecture:**


```text
docker image inspect \
  weather-intelligence-agent:v2.3-arm64 \
  --format '{{.Architecture}}'
```

**Expected on the validated Mac/Minikube environment:**


```text
arm64
```


## 12. Kubernetes / Minikube


The application was deployed and validated on local Kubernetes using
Minikube.

Core Kubernetes resources include: - Deployment - Service - ConfigMap -
Secret - ServiceMonitor - OpenTelemetry Collector resources

**Example resource application:**


```text
kubectl apply -f k8s/
```

**Check pods:**


```text
kubectl get pods
```

**Expected application state:**


```text
READY 1/1
STATUS Running
```

**Check deployment:**


```text
kubectl get deployment weather-intelligence-agent
```

**Check service:**


```text
kubectl get service weather-intelligence-agent-service
```

12.1 Loading the Local Image into Minikube


```text
minikube image load weather-intelligence-agent:v2.3-arm64
```

**Verify:**


```text
minikube image ls | grep weather-intelligence-agent
```

12.2 Updating the Deployment Image


```text
kubectl set image \
  deployment/weather-intelligence-agent \
  weather-intelligence-agent=weather-intelligence-agent:v2.3-arm64
```

**Check rollout:**


```text
kubectl rollout status deployment/weather-intelligence-agent
```

12.3 Port Forwarding

**Application:**


```text
kubectl port-forward \
  service/weather-intelligence-agent-service \
  8081:8080
```

The application can then be accessed through localhost:8081.


## 13. Kubernetes Secrets


The project uses Kubernetes Secret resources for sensitive
configuration.

**IMPORTANT:**

Never commit real API keys to Git.

When defining a standard Kubernetes Secret using the data field, values
**must be base64 encoded. Invalid base64 values produce errors such as:**


```text
Secret in version "v1" cannot be handled as a Secret:
illegal base64 data
```

**Secrets can be inspected with:**


```text
kubectl get secret weather-intelligence-agent-secret
```

Do not expose decoded secret values in documentation, screenshots, logs,
or source control.

The local .env file should also remain excluded from Git.


## 14. Prometheus


Prometheus is deployed through kube-prometheus-stack.

The project uses a ServiceMonitor so Prometheus can discover and scrape
the Weather Intelligence Agent metrics endpoint.

**Verify Prometheus monitoring components:**


```text
kubectl get pods -n monitoring
```

**Prometheus port-forward:**


```text
kubectl port-forward \
  -n monitoring \
  service/monitoring-kube-prometheus-prometheus \
  9090:9090
```

**Example API query:**


```text
curl -sG \
  'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=weather_agent_adk_executions_total'
```

**Other useful queries:**


```text
weather_agent_tool_calls_total

weather_agent_weather_api_requests_total

up{service="weather-intelligence-agent-service"}
```

When manually calling the Prometheus HTTP API, URL encoding via
–data-urlencode is recommended for PromQL expressions containing braces,
quotes, or equals signs.


## 15. Grafana


Grafana is deployed as part of the monitoring stack.

**Port-forward:**


```text
kubectl port-forward \
  -n monitoring \
  service/monitoring-grafana \
  3000:80
```

**Default username:**


```text
admin
```

**Retrieve the generated administrator password:**


```text
kubectl get secret \
  -n monitoring \
  monitoring-grafana \
  -o jsonpath='{.data.admin-password}' \
  | base64 --decode
```

The percent sign sometimes displayed immediately after the password in
the terminal is the shell prompt, not part of the password.

15.1 Dashboard Structure

**The completed dashboard can be organized into these rows:**

Availability: - Weather Agent Status - Running Pods - Available
Replicas - Pod Restarts

HTTP: - HTTP Request Rate - HTTP Error Rate - FastAPI p95 Latency

Google ADK: - ADK Agent Executions - ADK p95 Latency

Tools: - Tool Calls - Tool Failures - Tool p95 Latency

Weather API: - Weather API Requests - Weather API Failures - Weather API
p95 Latency

Security / HITL: - Input Guardrail Blocks - Output Guardrail Blocks -
Tool Guardrail Blocks - HITL Approval Requests - HITL Outcomes

Kubernetes Resources: - Pod CPU - Pod Memory


## 16. Example Grafana / Promql Queries


**HTTP request rate:**


```text
sum(
  rate(
    weather_agent_http_requests_total[5m]
  )
)
```

**HTTP error rate:**


```text
sum(
  rate(
    weather_agent_http_errors_total[5m]
  )
)
```

**FastAPI p95 latency:**


```text
histogram_quantile(
  0.95,
  sum by (le) (
    rate(
      weather_agent_http_request_duration_seconds_bucket[5m]
    )
  )
)
```

**ADK executions:**


```text
sum(
  weather_agent_adk_executions_total
)
```

**ADK p95 latency:**


```text
histogram_quantile(
  0.95,
  sum by (le) (
    rate(
      weather_agent_adk_execution_duration_seconds_bucket[5m]
    )
  )
)
```

**Tool calls:**


```text
sum by (tool_name) (
  weather_agent_tool_calls_total
)
```

**Weather API requests:**


```text
sum by (endpoint) (
  weather_agent_weather_api_requests_total
)
```

**Weather API p95 latency:**


```text
histogram_quantile(
  0.95,
  sum by (endpoint, le) (
    rate(
      weather_agent_weather_api_duration_seconds_bucket[5m]
    )
  )
)
```

**Tool guardrail blocks:**


```text
sum by (validation_stage) (
  weather_agent_tool_guardrail_blocks_total
)
```

**HITL outcomes:**


```text
sum by (status) (
  weather_agent_hitl_approval_outcomes_total
)
```


## 17. Metrics Server


**Kubernetes resource commands such as:**


```text
kubectl top pods
kubectl top nodes
```

require Metrics Server.

**If the Metrics API is unavailable, verify:**


```text
kubectl get pods -n kube-system | grep metrics-server
```

A newly started Metrics Server may need time before metrics become
available.


## 18. Testing


**The final validated regression result through Phase 11 was:**


```text
129 passed
```

**Full test command from the GenAI_Projects parent directory:**


```text
weather_intelligence_agent_v2/.venv/bin/python \
  -m pytest weather_intelligence_agent_v2/tests -q
```

**Validated result:**


```text
129 passed
```

The test suite includes coverage for multiple application layers,
including: - weather models/services - asynchronous weather operations -
planning - guardrails - tool guardrails - ADK tool-guardrail callback
behavior - HITL integration - approval routes - API/application
integration

18.1 Async Integration Tests

The Phase 7.4 integration tests make real calls to Open-Meteo.

They validate: - current weather - seven-day forecast - multi-city
weather - async weather planning

Because these tests call HTTPS services, local certificate configuration
can affect them.


## 19. Macos / Python Ssl Note


During development, Python 3.13 initially failed to validate the
**Open-Meteo certificate chain:**


```text
CERTIFICATE_VERIFY_FAILED
unable to get local issuer certificate
```

The installed truststore package was validated successfully.

**Example diagnostic:**


```text
import truststore
truststore.inject_into_ssl()
```

After injecting the native system trust store, an HTTPS request to the
Open-Meteo geocoding API returned HTTP 200.

This was an environment/certificate trust issue rather than an
Open-Meteo application failure.

Do not disable SSL certificate verification as a permanent workaround.


## 20. Local Development


**Typical setup:**


```text
cd /Users/rajeshvishwe/GenAI_Projects/weather_intelligence_agent_v2
```

**Activate the virtual environment:**


```text
source .venv/bin/activate
```

Install dependencies using the dependency file maintained by the
repository.

**Ensure the required environment configuration is available in:**


```text
.env
```

Never commit real API credentials.


## 21. Start Fastapi Locally


**From the parent project directory:**


```text
cd /Users/rajeshvishwe/GenAI_Projects
```

**Run:**


```text
weather_intelligence_agent_v2/.venv/bin/python \
  -m uvicorn weather_intelligence_agent_v2.api.app:app \
  --host 0.0.0.0 \
  --port 8000
```

**Health check:**


```text
curl http://localhost:8000/health
```

**Metrics:**


```text
curl http://localhost:8000/metrics
```

**Weather chat:**


```text
curl -X POST "http://localhost:8000/weather/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "local-test-001",
    "message": "What is the current weather in Delhi?"
  }'
```


## 22. Environment Loading


The project .env resides inside the weather_intelligence_agent_v2
project directory.

During debugging it was confirmed that importing the application loaded
the GOOGLE_API_KEY into the application process even when the shell
itself did not already contain that variable.

**This distinction is important:**

Shell environment: os.getenv(…) may initially be empty.

Application environment: application startup can load values from the
project .env.

Do not print complete API keys while debugging.


## 23. Project Structure


The exact repository may contain additional files, but the major
**structure implemented through Phase 11 follows this organization:**


```text
weather_intelligence_agent_v2/
|
+-- agent.py
|
+-- api/
|   +-- app.py
|   +-- approval_routes.py
|
+-- services/
|   +-- weather_chat_service.py
|   +-- async_weather_service.py
|   +-- async_weather_planning_service.py
|
+-- models/
|   +-- weather models
|   +-- weather_planning.py
|
+-- guardrails/
|   +-- input_guardrail.py
|   +-- output_guardrail.py
|   +-- tool_guardrail.py
|   +-- adk_tool_guardrail_callback.py
|   +-- approval_service.py
|   +-- approval_models.py
|   +-- exceptions.py
|   +-- config/
|   +-- validators/
|
+-- observability/
|   +-- tracing.py
|   +-- agent_metrics.py
|   +-- weather_api_metrics.py
|   +-- security_metrics.py
|   +-- additional tracing/metrics modules
|
+-- tests/
|   +-- guardrails/
|   +-- test_async_phase_7_4.py
|   +-- additional unit/integration tests
|
+-- k8s/
|   +-- deployment.yaml
|   +-- service.yaml
|   +-- configmap.yaml
|   +-- secret.yaml (local/sensitive)
|   +-- servicemonitor.yaml
|   +-- OpenTelemetry Collector configuration
|
+-- Dockerfile
+-- .env
+-- dependency/configuration files
```


## 24. Observability Coverage


**Implemented and validated through Phase 11:**

HTTP request count: COMPLETE

HTTP latency: COMPLETE

HTTP errors: COMPLETE

ADK executions: COMPLETE

ADK latency: COMPLETE

Tool calls: COMPLETE

Tool latency: COMPLETE

Tool failures: COMPLETE

External weather API request count: COMPLETE

External weather API latency: COMPLETE

External weather API failures: COMPLETE

Input guardrail blocks: COMPLETE

Output guardrail blocks: COMPLETE

Tool guardrail blocks: COMPLETE

HITL requests: COMPLETE

HITL outcomes: COMPLETE

Pod CPU: COMPLETE

Pod memory: COMPLETE

Pod restarts: COMPLETE

Replica count: COMPLETE

FastAPI tracing: COMPLETE

ADK tracing: COMPLETE

Tool spans: COMPLETE

Weather API spans: COMPLETE

OpenTelemetry Collector: COMPLETE

Trace/log correlation: COMPLETE


## 25. Optional Future Observability


Two advanced metrics were intentionally not treated as required for the
**Phase 11 completion point:**

-   isolated Gemini-specific call/latency metrics
-   explicit Gemini token-usage metrics

ADK execution metrics currently provide aggregate agent-level
visibility.

Future work can extract model-level telemetry from the Gemini/ADK
execution layer where usage metadata is available.


## 26. Security Principles


**The project follows several useful production-oriented principles:**


## 1. Validate User Input Before Model Execution.



## 2. Validate Model Output Before Returning It.



## 3. Validate Tool Names Before Tool Arguments.



## 4. Use Deterministic Security Policies Where Possible.



## 5. Keep Human Approval Available For Sensitive Tool Operations.



## 6. Never Expose Secrets Through Metrics.



## 7. Avoid High-Cardinality Metric Labels.



## 8. Do Not Use Session Ids As Prometheus Labels.



## 9. Do Not Use Raw Prompts As Prometheus Labels.



## 10. Do Not Use Tool Arguments As Prometheus Labels.



## 11. Keep Api Credentials Outside Source Control.



## 12. Keep Tls Certificate Verification Enabled.



## 13. Design Principles



```text
Separation of concerns:
```

API layer: HTTP transport

WeatherChatService: conversational application orchestration

Google ADK: agent execution

Weather services: weather-domain operations

Guardrails: deterministic security boundaries

ApprovalService: HITL workflow

Observability: metrics, traces, and logging

Kubernetes: runtime orchestration

Prometheus/Grafana: monitoring and visualization

This separation makes individual components easier to test and replace.


## 28. Troubleshooting


Problem: Metrics API not available

**Check:**


```text
kubectl get pods -n kube-system | grep metrics-server
```

Wait for Metrics Server to become ready before retrying kubectl top.

Problem: Helm says release name is already in use

**Example:**


```text
cannot reuse a name that is still in use
```

**Check existing releases:**


```text
helm list -A
```

Do not reinstall an already installed monitoring release unnecessarily.

Problem: Kubernetes Secret reports illegal base64 data

Ensure values under Secret.data are correctly base64 encoded, or use an
appropriate string-based Secret definition when intentionally supported
by the manifest design.

Problem: /weather/chat returns Internal Server Error

Check: - Uvicorn logs - environment loading - GOOGLE_API_KEY
availability - weather API connectivity - Gemini/ADK errors

Problem: Weather response says connection error

Check Open-Meteo connectivity and local SSL certificate trust.

Problem: Prometheus query containing labels fails to parse

**Use:**


```text
curl -sG URL \
  --data-urlencode 'query=<PromQL>'
```

instead of manually constructing an incorrectly encoded query string.

Problem: Metrics do not appear after code changes

Restart the FastAPI/Uvicorn process so the new instrumentation is
loaded.

Remember that Prometheus client metrics are process-local. Traffic
generated in a separate short-lived Python process does not increment
the counters of the running Uvicorn process.

Problem: Grafana password appears to have an extra % character

The % shown immediately after decoded output on some shells is the
prompt indicator. It is not part of the decoded password.


## 29. Interview-Ready Project Explanation


**A concise explanation:**

“I built a production-style Agentic AI Weather Intelligence application
using Google ADK and Gemini. FastAPI exposes the conversational API,
while a dedicated WeatherChatService encapsulates ADK execution and
session management.

The agent uses asynchronous weather services backed by Open-Meteo for
geocoding, current weather, forecasts, and multi-city planning. I
implemented deterministic input, output, and tool guardrails, along with
a human-in-the-loop approval workflow for controlled tool execution.

For observability, I instrumented the HTTP, ADK, tool, and external API
layers with Prometheus metrics and OpenTelemetry traces. Prometheus and
Grafana provide request, error, latency, tool, weather API, security,
HITL, CPU, memory, restart, and replica dashboards.

I containerized the application with Docker and deployed it on
Kubernetes using Minikube, with ConfigMaps, Secrets,
ServiceMonitor-based Prometheus discovery, and an OpenTelemetry
Collector. The final regression suite contains 129 passing tests.”


## 30. Key Learning Outcomes


This project demonstrates hands-on understanding of: - Agentic AI
architecture - Google ADK - Gemini integration - agent/tool separation -
asynchronous Python - FastAPI - API/service-layer architecture -
deterministic AI guardrails - human-in-the-loop workflows - Prometheus
metrics - Grafana dashboards - OpenTelemetry distributed tracing -
trace/log correlation - Docker - ARM64 container builds - Kubernetes -
Minikube - ConfigMaps and Secrets - ServiceMonitor - Kubernetes resource
monitoring - integration testing - observability-driven debugging


## 31. Current Release Boundary


The current documented release ends after Phase 11.

Phase 12 production hardening was intentionally deferred.

Potential future Phase 12 topics include: - deployment/YAML consistency
audit - namespace isolation - non-root containers - Kubernetes
SecurityContext - pod security hardening - graceful shutdown - explicit
rolling-update strategy - PodDisruptionBudget - Horizontal Pod
Autoscaling - secret-management improvements - NetworkPolicy -
deployment automation - production cloud deployment - CI/CD hardening -
final GitHub packaging


## 32. Final Validation


**Final validated state through Phase 11:**


```text
Automated tests:
    129 passed

FastAPI:
    PASS

Google ADK:
    PASS

Weather API:
    PASS

Input/output/tool guardrails:
    PASS

HITL:
    PASS

Docker:
    PASS

Kubernetes / Minikube:
    PASS

Prometheus:
    PASS

Grafana:
    PASS

OpenTelemetry:
    PASS

Trace/log correlation:
    PASS
```

PROJECT

Weather Intelligence Agent v2

Release: Phase 11 Complete

Phase 12: Deferred

Purpose: Learning, portfolio demonstration, architecture practice, and
production-style Agentic AI engineering.
