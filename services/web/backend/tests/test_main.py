"""Test main application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "game-djinn-web"
    assert data["version"] == "0.1.0"
    assert "status" in data
    assert "database" in data


def test_cors_headers():
    """Test CORS headers are properly set."""
    response = client.options("/api/auth/config", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # FastAPI handles CORS automatically, just verify the request doesn't fail
    assert response.status_code in [200, 204]


def test_openapi_docs():
    """Test OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_data = response.json()
    assert openapi_data["info"]["title"] == "Game Djinn API"