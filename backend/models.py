# -*- coding: utf-8 -*-
"""models.py – Pydantic Data Models for FinRecon AI
===================================================
Defines schemas for reconciliation results, exceptions, metrics, and AI queries.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class ReconciliationResult(BaseModel):
    """Schema for a single reconciled transaction record."""
    transaction_id: str
    ledger_vendor: str
    ledger_amount: float
    ledger_date: str
    bank_vendor: Optional[str] = None
    bank_amount: Optional[float] = None
    bank_date: Optional[str] = None
    gateway_merchant: Optional[str] = None
    gateway_net_amount: Optional[float] = None
    gateway_settlement_date: Optional[str] = None
    status: str
    confidence: float
    requires_human_review: bool = False
    amount_difference: Optional[float] = None
    date_difference_days: Optional[int] = None
    fuzzy_score: Optional[float] = None
    notes: Optional[str] = None


class ExceptionRecord(BaseModel):
    """Schema for an unresolved exception transaction requiring review."""
    transaction_id: str
    status: str
    ledger_vendor: str
    ledger_amount: float
    ledger_date: str
    bank_vendor: Optional[str] = None
    bank_amount: Optional[float] = None
    bank_date: Optional[str] = None
    amount_difference: Optional[float] = None
    date_difference_days: Optional[int] = None
    confidence: float
    requires_human_review: bool
    notes: Optional[str] = None


class MetricsResponse(BaseModel):
    """Summary metrics of reconciliation batch."""
    total_records: int
    exact_matches: int
    fuzzy_matches: int
    matched_records: int
    amount_mismatches: int
    date_mismatches: int
    missing_records: int
    duplicates: int
    unresolved_exceptions: int
    match_rate: float


class ReconcileResponse(BaseModel):
    """Response returned upon completion of reconciliation."""
    message: str
    metrics: MetricsResponse
    summary: MetricsResponse
    results_saved_to: str
    exceptions_saved_to: str


class GenerateDataResponse(BaseModel):
    """Response returned by data generator endpoint."""
    message: str
    ledger_records: int
    bank_records: int
    gateway_records: int


class AskRequest(BaseModel):
    """Natural-language question payload for AI analysis."""
    question: str = Field(..., description="Financial inquiry regarding reconciliation report")


class AskResponse(BaseModel):
    """AI agent response payload."""
    question: str
    answer: str
    model_used: Optional[str] = None
