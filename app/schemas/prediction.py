
from pydantic import BaseModel, Field
from typing import List


class PredictRequest(BaseModel):
    url: str = Field(..., min_length=1, description="The URL to check")


class PredictResponse(BaseModel):
    url: str
    prediction: str
    risk_score: float
    model_version: str
    top_signals: List[str] = []


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model: str
    version: str
    features: List[str]
    training_date: str
    metrics: dict


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
