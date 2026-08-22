import os
from pathlib import Path
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MODEL_PATH = os.getenv("MODEL_PATH", "ml/artifacts/model.joblib")
MODEL_METADATA_PATH = os.getenv(
    "MODEL_METADATA_PATH", "ml/artifacts/model_metadata.json"
)
MAX_URL_LENGTH = int(os.getenv("MAX_URL_LENGTH", "2048"))