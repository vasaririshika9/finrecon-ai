# -*- coding: utf-8 -*-
"""main.py – FinRecon AI FastAPI Application
==========================================
Autonomous AI Finance Controller backend.

Endpoints:
    GET  /health          - Liveness probe
    POST /generate-data   - Automatically generate synthetic CSV files
    POST /reconcile       - Run full reconciliation engine & save results
    GET  /results         - Return complete reconciliation report
    GET  /exceptions      - Return only exceptions requiring review
    POST /ask             - Natural-language financial question answering
"""
import os
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import (
    ReconciliationResult,
    ExceptionRecord,
    MetricsResponse,
    ReconcileResponse,
    GenerateDataResponse,
    AskRequest,
    AskResponse,
)

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FinRecon AI – Autonomous AI Finance Controller",
    description="Intelligent multi-source financial transaction reconciliation system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)








BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_JSON = os.path.join(RESULTS_DIR, "reconciliation_results.json")
EXCEPTIONS_JSON = os.path.join(RESULTS_DIR, "exceptions.json")


@app.on_event("startup")
def startup_event():
    """Ensure data files and initial reconciliation results exist on server boot."""
    try:
        from data_generator import generate_data
        from reconciliation import run_reconciliation
        if not os.path.exists(RESULTS_JSON):
            generate_data()
            run_reconciliation()
            print("[Startup] Initial synthetic data & reconciliation results ready.")
    except Exception as e:
        print(f"[Startup Warning] Could not pre-generate data: {e}")


@app.get("/health", tags=["System"])
def health_check():
    """Liveness health check endpoint."""
    return {"status": "ok", "message": "FinRecon AI backend is running"}


@app.post("/generate-data", response_model=GenerateDataResponse, tags=["Data Generation"])
def generate_data_endpoint():
    """
    Automatically generate synthetic financial data:
    - internal_ledger.csv (~60 records)
    - bank_statement.csv (~58-62 records)
    - payment_gateway.csv (~55-60 records)
    """
    try:
        from data_generator import generate_data
        counts = generate_data()
        return GenerateDataResponse(
            message="Synthetic financial data generated successfully.",
            ledger_records=counts["ledger"],
            bank_records=counts["bank"],
            gateway_records=counts["gateway"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Data generation failed: {exc}")


@app.post("/reconcile", response_model=ReconcileResponse, tags=["Reconciliation"])
def reconcile_endpoint():
    """
    Run multi-level reconciliation engine across Ledger, Bank, and Gateway.
    Saves results and exceptions to the results/ directory.
    """
    try:
        from reconciliation import run_reconciliation
        output = run_reconciliation()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data files not found ({exc}). Please invoke /generate-data first."
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reconciliation process failed: {exc}")

    metrics_obj = MetricsResponse(**output["metrics"])
    return ReconcileResponse(
        message="Reconciliation batch processed successfully.",
        metrics=metrics_obj,
        summary=metrics_obj,
        results_saved_to=RESULTS_JSON,
        exceptions_saved_to=EXCEPTIONS_JSON,
    )


@app.get("/results", response_model=List[ReconciliationResult], tags=["Reconciliation"])
def get_results_endpoint():
    """Return all reconciled transaction records with confidence scores and details."""
    if not os.path.exists(RESULTS_JSON):
        raise HTTPException(
            status_code=404,
            detail="Reconciliation results not found. Please call /reconcile first."
        )
    try:
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed reading results: {exc}")


@app.get("/exceptions", response_model=List[ExceptionRecord], tags=["Reconciliation"])
def get_exceptions_endpoint():
    """
    Return unresolved transaction exceptions:
    - AMOUNT_MISMATCH
    - DATE_MISMATCH
    - MISSING_BANK_RECORD
    - DUPLICATE
    - UNRESOLVED
    """
    if not os.path.exists(EXCEPTIONS_JSON):
        raise HTTPException(
            status_code=404,
            detail="Exceptions record file not found. Please call /reconcile first."
        )
    try:
        with open(EXCEPTIONS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed reading exceptions: {exc}")


@app.post("/ask", response_model=AskResponse, tags=["AI Analysis"])
def ask_endpoint(request: AskRequest):
    """Ask natural-language questions to the Autonomous AI Finance Controller."""
    try:
        from ai_agent import ask_ai
        res = ask_ai(request.question)
        return AskResponse(**res)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI query failed: {exc}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8888))
    print(f"==================================================")
    print(f" Starting FinRecon AI on http://localhost:{port}")
    print(f" Swagger API Docs: http://localhost:{port}/docs")
    print(f"==================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
