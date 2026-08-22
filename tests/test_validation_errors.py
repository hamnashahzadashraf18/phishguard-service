"""
Tests that the API correctly rejects bad input instead of crashing,
and always returns our structured error format:
{"error": {"code": ..., "message": ...}}
"""

from fastapi.testclient import TestClient
from app.main import app


def test_predict_rejects_missing_url_field():
    with TestClient(app) as client:
        response = client.post("/predict", json={})

        assert response.status_code == 422

        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]


def test_predict_rejects_empty_url():
    with TestClient(app) as client:
        response = client.post("/predict", json={"url": ""})

        assert response.status_code == 422
        assert "error" in response.json()


def test_predict_rejects_invalid_json_body():
    """
    Sends a body that isn't valid JSON at all -- not just missing
    fields, but genuinely broken syntax. The API should still
    respond cleanly, not crash or leak a raw parser error.
    """
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            content="this is not json{{{",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422
        assert "error" in response.json()


def test_error_response_never_leaks_internals():
    """
    Confirms the error response never exposes things like file
    paths or raw Python exception text -- only our clean message.
    """
    with TestClient(app) as client:
        response = client.post("/predict", json={"url": ""})
        body_text = response.text.lower()

        assert "traceback" not in body_text
        assert ".py" not in body_text
        assert "c:\\" not in body_text