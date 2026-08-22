"""
Tests that the trained model artifact actually loads correctly.

This matters because a broken or missing model.joblib file would
otherwise fail silently at runtime -- this test catches that early,
before the API even starts.
"""

from app.services.model_service import ModelService


def test_model_loads_successfully():
    service = ModelService()
    service.load()

    assert service.loaded is True
    assert service.model is not None


def test_model_metadata_loads_successfully():
    service = ModelService()
    service.load()

    assert service.metadata is not None
    assert "model" in service.metadata
    assert "version" in service.metadata
    assert "features" in service.metadata


def test_model_can_actually_predict():
    """
    Loading isn't enough on its own -- confirm the loaded model
    object can actually run a prediction without crashing.
    """
    service = ModelService()
    service.load()

    result = service.predict("https://www.google.com")

    assert result["prediction"] in ("legitimate", "phishing")
    assert 0.0 <= result["risk_score"] <= 1.0