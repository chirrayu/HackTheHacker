import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "HACK THE HACKER"
    assert "version" in data
    assert data["status"] == "operational"

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "uptime_seconds" in data
    assert "virtualbox" in data
    assert "active_threats" in data
