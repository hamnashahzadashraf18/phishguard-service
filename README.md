PhishGuard Service
A small production-style AI risk-scoring service that takes a URL and predicts whether it is legitimate, suspicious, or phishing. Built for the Digitalsofts Junior/Aspiring ML Engineer technical assessment.
The service extracts features directly from a raw URL string, runs them through a trained XGBoost classifier, and returns a prediction, a risk score, and a plain-language explanation of the signals behind the decision.
Tech Stack
Python 3.11
FastAPI — REST API framework
Uvicorn — ASGI server
Pydantic — request/response validation
Scikit-learn — Logistic Regression, Random Forest, model evaluation
XGBoost — final selected model
Pandas / NumPy — data handling
Joblib — model persistence
Pytest / HTTPX — testing
Docker / Docker Compose — containerization
phishguard-service/
Project Structure
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/routes.py        # /health, /predict, /model endpoints
│   ├── services/             # Model loading + prediction logic
│   ├── schemas/               # Pydantic request/response models
│   └── core/config.py         # Environment-based settings
├── ml/
│   ├── data/                  # Training dataset (not committed - see below)
│   ├── features/extractor.py  # URL feature extraction (shared by training + API)
│   ├── training/train.py      # Trains and compares 3 models
│   └── artifacts/              # Saved model + metadata
├── tests/                     # Pytest test suite (10 tests)
├── docs/
│   ├── TECHNICAL_DECISIONS.md
│   └── ENGINEERING_NOTES.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
Local Setup:
git clone https://github.com/hamnashahzadahraf18/phishguard-service.git
cd phishguard-service
Install dependencies:
pip install -r requirements.txt
Run the API:
uvicorn app.main:app --reload
Open the interactive docs
http://127.0.0.1:8000/docs
Docker Setup
The project is fully containerized. From the project root:
docker compose up --build
Environment variables (see .env.example):
APP_ENV=production
MODEL_PATH=ml/artifacts/model.joblib
MODEL_METADATA_PATH=ml/artifacts/model_metadata.json
LOG_LEVEL=INFO
API Examples:
GET /health
{
  "status": "healthy",
  "model_loaded": true
}
POST /predict:
{ "url": "http://192.168.1.1/paypal-login-verify-account" }
Response:
{
  "url": "http://192.168.1.1/paypal-login-verify-account",
  "prediction": "phishing",
  "risk_score": 1.0,
  "model_version": "1.0",
  "top_signals": [
    "IP address used instead of domain name",
    "Not using HTTPS",
    "Contains suspicious keyword"
  ]
GET /model
{
  "model": "xgboost",
  "version": "1.0",
  "features": ["url_length", "num_dots", "num_hyphens", "..."],
  "training_date": "2026-08-21T...",
  "metrics": {
    "accuracy": 0.9643,
    "precision": 0.9485,
    "recall": 0.982,
    "f1": 0.965
  }
}
}
Error format:
{
  "error": {
    "code": "INVALID_URL",
    "message": "The provided URL is not valid."
  }
}
ML Results

Three models were trained on the same feature set and compared:

Model	Accuracy	Precision	Recall	F1
Logistic Regression	0.951	0.925	0.982	0.953
Random Forest	0.961	0.949	0.973	0.961
XGBoost (selected)	0.964	0.949	0.982	0.965

XGBoost was selected because it tied for the highest recall (0.982) and outperformed the other two on every other metric. Full reasoning is in docs/TECHNICAL_DECISIONS.md.

Dataset: PhiUSIIL Phishing URL Dataset (134,850 legitimate / 100,945 phishing URLs). A balanced sample of 15,000 URLs was used for training. Features were computed from raw URL text using this project's own ml/features/extractor.py, not the dataset's pre-computed columns, so training and live inference use identical feature logic.
Testing:
pytest tests/ -v
Limitations
The model is trained on a sample of one dataset and may not generalize perfectly to phishing patterns outside that dataset's distribution.
Features are computed from the URL string alone — the service does not visit or analyze the actual destination page content, so it cannot catch phishing pages that use a clean-looking URL with malicious page content.
The free/local deployment setup has not been load-tested; behavior under high concurrent traffic is unverified.
top_signals explanations are rule-based on feature values, not a formal model-explainability technique like SHAP.
Deployment to a public cloud platform (Render/Koyeb) was blocked by a payment-verification requirement I was unable to complete before the deadline. The Docker setup (Dockerfile + docker-compose.yml) was verified locally and runs correctly; see docs/ENGINEERING_NOTES.md for details.
Future Improvements
Deploy to a public URL once payment verification is resolved
Add API key authentication and rate limiting
Add prediction history storage (SQLite/PostgreSQL)
Migrate FastAPI startup handling from @app.on_event to the newer lifespan handler pattern
Expand the feature set with redirect-chain analysis (would require fetching the destination URL)
AI Assistance
Tools used: Claude (Anthropic)
How AI was used: Used as a coding and debugging assistant throughout the project — generating initial drafts of the feature extractor, training script, FastAPI service, tests, and Docker configuration, then reviewing, testing, and adjusting each piece myself. Also used to help debug environment setup issues (Git, PowerShell execution policy, Docker/WSL2 configuration).
What was personally designed/implemented: The feature selection and justification, the model selection reasoning (including the recall/F1 tie-break logic), all reflection question answers in TECHNICAL_DECISIONS.md, and all engineering decisions were reviewed and understood before being included in this submission. All code was tested and run locally before committing.
