# 🌦 Weather Agent using Google ADK

## Overview

Weather Agent is a Google ADK application that answers weather-related questions using the Open-Meteo public REST API.

This project demonstrates how to build an AI Agent capable of calling external APIs using custom tools.

---

# Features

- Google ADK Agent
- Gemini Model
- Custom Tool
- REST API Integration
- JSON Parsing
- Error Handling
- Corporate SSL Support
- Open-Meteo API

---

# Tech Stack

- Python 3.12
- Google ADK
- Gemini 3.1 Flash Lite
- Requests
- Truststore
- Open-Meteo API

---

# Project Structure

```text
weather_agent/
│
├── agent.py
├── tools.py
├── test.py
├── requirements.txt
├── README.md
├── architecture.md
├── __init__.py
└── .env
```

---

# Installation

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.\.venv\Scripts\activate
```

Install packages

```bash
pip install -r requirements.txt
```

---

# Required Packages

```text
google-adk
google-genai
requests
truststore
python-dotenv
```

---

# Running the Agent

From project root

```bash
adk web
```

Open

```
http://127.0.0.1:8000
```

Select

```
weather_agent
```

---

# Example Questions

```
Weather in Delhi

Weather in Gurgaon

What's the weather in London?

Current weather in Tokyo
```

---

# Example Response

```text
## 🌍 Weather Report

- City: Delhi, India
- Temperature: 29°C
- Wind Speed: 12 km/h
- Wind Direction: 264°
- Observation Time: 2026-07-13 00:30
```

---

# APIs Used

## Geocoding API

```
https://geocoding-api.open-meteo.com/v1/search
```

Converts

City

↓

Latitude & Longitude

---

## Weather API

```
https://api.open-meteo.com/v1/forecast
```

Returns

- Temperature
- Wind Speed
- Wind Direction
- Observation Time

---

# SSL Support

When running on BT/Openreach corporate VPN, HTTPS requests may fail due to SSL inspection.

Install

```bash
pip install truststore
```

Initialize

```python
import truststore

truststore.inject_into_ssl()
```

This allows Python to use the Windows Certificate Store.

---

# Error Handling

The project handles

- Invalid city
- API failure
- Network issues
- SSL issues
- Unexpected exceptions

---

# Learning Outcomes

This project demonstrates:

- Google ADK Fundamentals
- AI Agent Development
- Custom Tool Development
- REST API Integration
- JSON Processing
- Corporate SSL Configuration
- Exception Handling
- Prompt Engineering

---

# Future Improvements

- Weather Forecast
- Weather Icons
- Weather Conditions
- Air Quality
- Humidity
- Sunrise/Sunset
- Rain Probability
- Vertex AI Deployment
- Docker Support
- GKE Deployment

---

# Author

Rajesh Kumar Vishwakarma

Google ADK Learning Series