

from fastapi.testclient import TestClient
from app.main import app

def test_predict_returns_valid_response_for_legitimate_url():
    with TestClient(app) as client:
        response = client.post("/predict", json={"url": "https://www.google.com"})

        assert response.status_code == 200

        data = response.json()
        assert data["url"] == "https://www.google.com"
        assert data["prediction"] in ("legitimate", "phishing")
        assert 0.0 <= data["risk_score"] <= 1.0
        assert "model_version" in data
        assert isinstance(data["top_signals"], list)

def test_predict_correctly_flags_suspicious_url():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"url": "http://192.168.1.1/paypal-login-verify-account"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["prediction"] == "phishing"
        assert data["risk_score"] > 0.5
        assert len(data["top_signals"]) > 0

def test_predict_response_matches_expected_schema():
    with TestClient(app) as client:
        response = client.post("/predict", json={"url": "https://example.com/login"})
        data = response.json()

        required_fields = {"url", "prediction", "risk_score", "model_version"}
        assert required_fields.issubset(data.keys())