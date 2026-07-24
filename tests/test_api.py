"""
API tests.
"""

from fastapi.testclient import TestClient

from weather_intelligence_agent_v2.api.app import (
    app,
)

client = TestClient(app)


def test_health() -> None:
    """
    Test health endpoint.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "UP"