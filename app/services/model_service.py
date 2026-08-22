
import json
import logging
import joblib
from pathlib import Path

from app.core.config import MODEL_PATH, MODEL_METADATA_PATH
from ml.features.extractor import extract_features, feature_names, explain_top_signals

logger = logging.getLogger("phishguard")

LABEL_MAP = {1: "legitimate", 0: "phishing"}


class ModelService:
    """
    Wraps the trained model so it's loaded exactly once (at app
    startup) and reused for every request, instead of reloading
    the file from disk on every single prediction.
    """

    def __init__(self):
        self.model = None
        self.metadata = None
        self.loaded = False

    def load(self):
        model_path = Path(MODEL_PATH)
        metadata_path = Path(MODEL_METADATA_PATH)

        if not model_path.exists():
            logger.error(f"Model file not found at {model_path}")
            self.loaded = False
            return

        try:
            self.model = joblib.load(model_path)
            with open(metadata_path) as f:
                self.metadata = json.load(f)
            self.loaded = True
            logger.info(f"Model loaded: {self.metadata.get('model')} v{self.metadata.get('version')}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.loaded = False

    def predict(self, url: str) -> dict:
        if not self.loaded:
            raise RuntimeError("Model is not loaded")

        features = extract_features(url)
        ordered_values = [[features[name] for name in feature_names()]]

        prediction_label = self.model.predict(ordered_values)[0]
        probabilities = self.model.predict_proba(ordered_values)[0]

        phishing_index = list(self.model.classes_).index(0)
        risk_score = round(float(probabilities[phishing_index]), 4)

        return {
            "url": url,
            "prediction": LABEL_MAP.get(int(prediction_label), "unknown"),
            "risk_score": risk_score,
            "model_version": self.metadata.get("version", "unknown"),
            "top_signals": explain_top_signals(features),
        }
model_service = ModelService()
