# -*- coding: utf-8 -*-
"""ai_agent.py – Optional AI-Powered Analysis Layer
=================================================
Uses OpenAI GPT-4o-mini when OPENAI_API_KEY is configured.
Falls back seamlessly to an intelligent rule-based engine when not configured.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_JSON = os.path.join(RESULTS_DIR, "reconciliation_results.json")
EXCEPTIONS_JSON = os.path.join(RESULTS_DIR, "exceptions.json")


def _load(path: str) -> list:
    """Load JSON records from disk."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _summary(results: list) -> str:
    """Build formatted text summary for LLM prompt."""
    ledger_records = [r for r in results if r.get("status") != "DUPLICATE"]
    total = len(ledger_records)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    matched = counts.get("MATCHED", 0) + counts.get("FUZZY_MATCHED", 0)
    rate = round(matched / total * 100, 2) if total else 0.0

    lines = [
        f"Total Ledger Records: {total}",
        f"Exact Matches (100% confidence): {counts.get('MATCHED', 0)}",
        f"Fuzzy Vendor Matches: {counts.get('FUZZY_MATCHED', 0)}",
        f"Amount Mismatches: {counts.get('AMOUNT_MISMATCH', 0)}",
        f"Date Mismatches: {counts.get('DATE_MISMATCH', 0)}",
        f"Missing Bank Records: {counts.get('MISSING_BANK_RECORD', 0)}",
        f"Duplicate Bank Transactions: {counts.get('DUPLICATE', 0)}",
        f"Unresolved Exceptions: {counts.get('UNRESOLVED', 0)}",
        f"Overall Match Rate: {rate}%",
        "",
        "Key Exceptions Requiring Review:",
    ]
    for exc in [r for r in results if r.get("requires_human_review")][:6]:
        lines.append(
            f"  • [{exc['status']}] {exc['ledger_vendor']} | "
            f"Ledger: {exc['ledger_amount']} | Bank: {exc.get('bank_amount', 'N/A')} | "
            f"Confidence: {exc['confidence']}%"
        )
    return "\n".join(lines)


def _rule_answer(question: str, results: list) -> str:
    """Rule-based analyzer for answering financial inquiries without external APIs."""
    q = question.lower()
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    ledger_records = [r for r in results if r.get("status") != "DUPLICATE"]
    total = len(ledger_records)
    matched = counts.get("MATCHED", 0) + counts.get("FUZZY_MATCHED", 0)
    rate = round(matched / total * 100, 2) if total else 0.0

    if any(k in q for k in ["match rate", "how many matched", "percentage", "rate"]):
        return (
            f"The reconciliation match rate is {rate}%. "
            f"{matched} out of {total} internal ledger transactions were successfully matched "
            f"({counts.get('MATCHED', 0)} exact matches + {counts.get('FUZZY_MATCHED', 0)} fuzzy matches)."
        )

    if any(k in q for k in ["exception", "problem", "issue", "review"]):
        exc = sum([
            counts.get('AMOUNT_MISMATCH', 0),
            counts.get('DATE_MISMATCH', 0),
            counts.get('MISSING_BANK_RECORD', 0),
            counts.get('DUPLICATE', 0),
            counts.get('UNRESOLVED', 0)
        ])
        return (
            f"There are {exc} exception records requiring human review: "
            f"{counts.get('AMOUNT_MISMATCH', 0)} amount mismatches, "
            f"{counts.get('DATE_MISMATCH', 0)} date mismatches, "
            f"{counts.get('MISSING_BANK_RECORD', 0)} missing bank records, "
            f"{counts.get('DUPLICATE', 0)} duplicate bank entries, "
            f"and {counts.get('UNRESOLVED', 0)} unresolved transactions."
        )

    if "duplicate" in q:
        return (
            f"Identified {counts.get('DUPLICATE', 0)} duplicate bank transactions "
            f"sharing identical description, amount, and date. Flagged for review."
        )

    if "missing" in q:
        return (
            f"{counts.get('MISSING_BANK_RECORD', 0)} internal ledger transactions have no "
            f"corresponding record in the bank statement."
        )

    if "amount mismatch" in q or "amount" in q:
        mis = [r for r in results if r["status"] == "AMOUNT_MISMATCH"]
        if not mis:
            return "No amount mismatches detected."
        detail = ", ".join(f"{r['ledger_vendor']} (diff: ₹{r.get('amount_difference', 0)})" for r in mis)
        return f"Found {len(mis)} amount mismatch(es): {detail}."

    if "date mismatch" in q or "date" in q:
        mis = [r for r in results if r["status"] == "DATE_MISMATCH"]
        if not mis:
            return "No date mismatches detected."
        detail = ", ".join(f"{r['ledger_vendor']} (gap: {r.get('date_difference_days', 0)} days)" for r in mis)
        return f"Found {len(mis)} date mismatch(es): {detail}."

    return (
        f"FinRecon AI processed {total} ledger transactions with an overall match rate of {rate}%. "
        f"You can ask specifically about: 'match rate', 'exceptions', 'amount mismatches', 'date mismatches', "
        f"'duplicates', or 'missing transactions'."
    )


def ask_ai(question: str) -> dict:
    """Analyze the reconciliation report and answer user questions."""
    results = _load(RESULTS_JSON)
    if not results:
        return {
            "question": question,
            "answer": "No reconciliation results found on disk. Please run /reconcile first.",
            "model_used": None,
        }

    # If OpenAI API Key is missing or placeholder, use intelligent rule engine
    if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-your") or len(OPENAI_API_KEY) < 20:
        return {
            "question": question,
            "answer": _rule_answer(question, results),
            "model_used": "rule-based-controller",
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        summary_text = _summary(results)

        system_prompt = (
            "You are FinRecon AI, an autonomous financial controller and reconciliation specialist. "
            "Provide concise, precise, and auditable answers based solely on the provided reconciliation report. "
            "Clearly distinguish between exact matches, fuzzy matches, and exceptions."
        )
        user_prompt = f"Reconciliation Summary:\n{summary_text}\n\nQuestion: {question}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        return {
            "question": question,
            "answer": response.choices[0].message.content.strip(),
            "model_used": "gpt-4o-mini",
        }
    except Exception as exc:
        return {
            "question": question,
            "answer": f"[Notice: OpenAI API unavailable ({exc})] {_rule_answer(question, results)}",
            "model_used": "rule-based-controller",
        }
