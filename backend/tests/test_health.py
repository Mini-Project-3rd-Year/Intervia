"""
tests/test_health.py
Phase 0 — Health endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """Tests for GET /api/v1/health"""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint must return HTTP 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client: TestClient):
        """Response must include all required fields."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "environment" in data

    def test_health_status_is_ok(self, client: TestClient):
        """Status field must be 'ok'."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_service_name(self, client: TestClient):
        """Service name must identify this as the Intervia API."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["service"] == "intervia-api"

    def test_health_version_present(self, client: TestClient):
        """Version must be a non-empty string."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_health_content_type_json(self, client: TestClient):
        """Response Content-Type must be application/json."""
        response = client.get("/api/v1/health")
        assert "application/json" in response.headers.get("content-type", "")

    def test_health_response_matches_spec(self, client: TestClient):
        """Full response matches the documented specification."""
        response = client.get("/api/v1/health")
        data = response.json()
        # As per project spec: { "status": "ok", "service": "intervia-api" }
        assert data["status"] == "ok"
        assert data["service"] == "intervia-api"
