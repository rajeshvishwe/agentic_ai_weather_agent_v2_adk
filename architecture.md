--to start backend server & trigger UI:

--To start server: (in parent directory)

source weather_intelligence_agent_v2/.venv/bin/activate

uvicorn weather_intelligence_agent_v2.api.app:app \
  --host 0.0.0.0 \
  --port 8082 \
  --reload

--To start UI:

PYTHONPATH=/Users/rajeshvishwe/GenAI_Projects \
WEATHER_API_BASE_URL=http://localhost:8082 \
streamlit run weather_intelligence_agent_v2/ui/streamlit_app.py
2026-07-26 19:27:58.537 Uvicorn server started on :::8501



                    Weather Intelligence Agent v2

                         FastAPI Application
                         api/app.py
                              |
             +----------------+----------------+
             |                |                |
         /health          /metrics         API Routers
                                              |
                         +--------------------+------------------+
                         |                                       |
                  /weather/*                              HITL approval APIs
                         |
             +-----------+------------+
             |                        |
       /weather/plan              /weather/chat
             |                        |
 AsyncWeatherPlanningService     WeatherChatService
                                      |
                       +--------------+--------------+
                       |                             |
                 InputGuardrail              ADK Runtime
                                                    |
                                              ADK Runner
                                                    |
                                               root_agent
                                                    |
                                                 Gemini
                                                    |
                                      before_tool_callback
                                                    |
                                  ToolGuardrail → HITLGuardrail
                                                    |
                                               ADK Tools
                                                    |
                                      Weather/service layers
                                                    |
                                               Open-Meteo
                                                    |
                                           Agent final response
                                                    |
                                            OutputGuardrail
                                                    |
                                                 Client