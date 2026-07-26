FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/weather_intelligence_agent_v2

EXPOSE 8080

CMD ["sh", "-c", "python -m uvicorn weather_intelligence_agent_v2.api.app:app --host 0.0.0.0 --port ${PORT}"]