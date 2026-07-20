import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "VietTTS Studio" in response.json()["message"]

def test_analyze_endpoint():
    response = client.post("/api/analyze", json={
        "text": "Chào mừng 2026!",
        "config": {"ai": {"enabled": False}}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "rule_based"
    assert not data["is_ai_assisted"]

def test_voices_endpoint():
    response = client.get("/api/voices")
    assert response.status_code == 200
    assert "voices" in response.json()

def test_settings_endpoint():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert "settings" in response.json()
    assert "pause_rules" in response.json()
