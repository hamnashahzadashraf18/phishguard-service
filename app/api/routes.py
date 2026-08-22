"""
The actual API endpoints. Kept thin on purpose -- each route just
handles the HTTP side of things and hands off the real work to
model_service.
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.prediction import (
    PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse,
)
from app.services.model_service import model_service

logger = logging.getLogger("phishguard")
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "healthy" if model_service.loaded else "degraded",
        "model_loaded": model_service.loaded,
    }


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    logger.info("Received prediction request")

    if not model_service.loaded:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "MODEL_UNAVAILABLE",
                    "message": "The model is not currently loaded.",
                }
            },
        )

    try:
        result = model_service.predict(request.url)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "PREDICTION_FAILED",
                    "message": "Could not generate a prediction for this URL.",
                }
            },
        )

    logger.info(f"Prediction result: {result['prediction']}")
    return result


@router.get("/model", response_model=ModelInfoResponse)
def model_info():
    if not model_service.loaded:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "MODEL_UNAVAILABLE",
                    "message": "The model is not currently loaded.",
                }
            },
        )

    meta = model_service.metadata
    return {
        "model": meta.get("model", "unknown"),
        "version": meta.get("version", "unknown"),
        "features": meta.get("features", []),
        "training_date": meta.get("training_date", "unknown"),
        "metrics": meta.get("metrics", {}),
    }
