"""
Application entry point.
"""

import truststore

truststore.inject_into_ssl()

import uvicorn

from weather_intelligence_agent_v2.api.app import (
    app,
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )