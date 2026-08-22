"""
Entry point for the API. Creates the FastAPI app, loads the model
once at startup, and wires up the routes.

Run with: uvicorn app.main:app --reload   (from the project root)
"""

import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import APP_ENV, LOG_LEVEL
from app.services.model_service import model_service
from app.api.routes import router

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phishguard")

app = FastAPI(
    title="PhishGuard Risk Scoring Service",
    description="Predicts whether a URL is legitimate, suspicious, or phishing.",
    version="1.0",
)


@app.on_event("startup")
def startup_event():
    logger.info(f"Starting PhishGuard service (env={APP_ENV})")
    model_service.load()
    if not model_service.loaded:
        logger.warning("Service started without a loaded model -- /predict will fail")



@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "The request body is missing required fields or is malformed.",
            }
        },
    )


# Catch-all so an unexpected error never leaks a raw Python
# stack trace to the client.
@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong processing your request.",
            }
        },
    )


app.include_router(router)
