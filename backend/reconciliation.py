# -*- coding: utf-8 -*-
"""reconciliation.py – Core Reconciliation Engine
================================================
Compares records across:
1. Internal Ledger
2. Bank Statement
3. Payment Gateway Settlement Records

Matching levels:
- LEVEL 1: EXACT MATCH (Confidence 95–100)
- LEVEL 2: FUZZY MATCH (Confidence 75–94)
- LEVEL 3: AMOUNT MISMATCH (Confidence 50–74)
- LEVEL 4: DATE MISMATCH (Confidence 50–74)
- LEVEL 5: MISSING BANK RECORD (Confidence < 50)
- LEVEL 6: DUPLICATE DETECTION (Confidence < 50)
- LEVEL 7: UNRESOLVED (Confidence < 50)
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from rapidfuzz import fuzz

FUZZY_THRESHOLD = 75     # Minimum score to qualify as fuzzy match
DATE_TOLERANCE = 3       # Allowed date tolerance in days
AMOUNT_TOLERANCE = 0.01  # 1% tolerance for exact match amount comparison

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

LEDGER_CSV = os.path.join(DATA_DIR, "internal_ledger.csv")
BANK_CSV = os.path.join(DATA_DIR, "bank_statement.csv")
GATEWAY_CSV = os.path.join(DATA_DIR, "payment_gateway.csv")
RESULTS_JSON = os.path.join(RESULTS_DIR, "reconciliation_results.json")
EXCEPTIONS_JSON = os.path.join(RESULTS_DIR, "exceptions.json")

EXCEPTION_STATUSES = {
    "AMOUNT_MISMATCH",
    "DATE_MISMATCH",
    "MISSING_BANK_RECORD",
    "DUPLICATE",
    "UNRESOLVED",
}


def normalize_vendor(text: str) -> str:
    """Normalize vendor names by expanding standard abbreviations and stripping legal noise."""
    if not text:
        return ""
    t = str(text).upper().replace("*", " ").replace(".", " ")
    substitutions = [
        (r"\bMS AZURE\b", "MICROSOFT AZURE"),
        (r"\bAMAZON WEB SERVICES\b", "AWS"),
        (r"\bTATA COMM\b", "TATA COMMUNICATIONS"),
        (r"\bPAY INDIA\b", "INDIA"),
        (r"\bPAY\b", ""),
        (r"\bONLINE\b", ""),
        (r"\bSERVICES\b", ""),
        (r"\bTRIP\b", ""),
        (r"\bLTD\b", ""),
        (r"\bINC\b", ""),
        (r"\bCO\b", ""),
        (r"\bPVTLTD\b", ""),
        (r"\bSUBSCRIPTION\b", ""),
        (r"\bCREATIVE\b", ""),
        (r"\bSOFTWARE\b", ""),
    ]
    for pattern, repl in substitutions:
        t = re.sub(pattern, repl, t)
    return " ".join(t.split())


def calculate_similarity(v1: str, v2: str) -> float:
    """Compute normalized token-set similarity between two vendor strings."""
    s1, s2 = str(v1).upper().strip(), str(v2).upper().strip()
    if s1 == s2:
        return 100.0
    raw_sim = fuzz.token_set_ratio(s1, s2)
    norm_sim = fuzz.token_set_ratio(normalize_vendor(s1), normalize_vendor(s2))
    if norm_sim == 100.0 and raw_sim < 100.0:
        return round(80.0 + (raw_sim / 100.0) * 14.0, 1)
    return float(max(raw_sim, norm_sim))


def days_difference(d1: str, d2: str) -> int:
    """Return absolute calendar day difference between two dates."""
    try:
        fmt = "%Y-%m-%d"
        return abs((datetime.strptime(str(d1), fmt) - datetime.strptime(str(d2), fmt)).days)
    except Exception:
        return 999


def amounts_match(a1: float, a2: float) -> bool:
    """Return True if amounts match within allowed tolerance."""
    if a1 == 0:
        return a2 == 0
    return abs(a1 - a2) / a1 <= AMOUNT_TOLERANCE


def get_confidence(status: str, sim_score: float = 100.0) -> float:
    """Calculate confidence score (0-100) according to match category."""
    if status == "MATCHED":
        # Exact Match: 95–100
        return round(min(100.0, 95.0 + (sim_score - 95.0)), 1)
    elif status == "FUZZY_MATCHED":
        # Fuzzy Match: 75–94
        return round(max(75.0, min(94.0, 75.0 + (sim_score - 75.0) * 0.95)), 1)
    elif status == "AMOUNT_MISMATCH":
        # Partial Match: 50–74
        return round(max(50.0, min(74.0, sim_score * 0.72)), 1)
    elif status == "DATE_MISMATCH":
        # Partial Match: 50–74
        return round(max(50.0, min(74.0, sim_score * 0.75)), 1)
    elif status == "MISSING_BANK_RECORD":
        # Below 50
        return 30.0
    elif status == "DUPLICATE":
        # Below 50
        return 20.0
    else:  # UNRESOLVED
        # Below 50
        return 35.0


def run_reconciliation() -> Dict[str, Any]:
    """Execute reconciliation across internal ledger, bank statements, and payment gateway."""
    ledger = pd.read_csv(LEDGER_CSV)
    bank = pd.read_csv(BANK_CSV)
    gateway = pd.read_csv(GATEWAY_CSV)

    ledger["amount"] = ledger["amount"].astype(float)
    bank["amount"] = bank["amount"].astype(float)
    gateway["gross_amount"] = gateway["gross_amount"].astype(float)
    gateway["net_amount"] = gateway["net_amount"].astype(float)

    # Fast map for gateway records by transaction_reference
    gw_map = {
        str(row["transaction_reference"]): row.to_dict()
        for _, row in gateway.iterrows()
    }

    # Detect duplicate bank transactions by description + amount + date
    bank["_dup_key"] = (
        bank["description"].astype(str).str.upper().str.strip() + "|" +
        bank["amount"].astype(str) + "|" +
        bank["date"].astype(str)
    )
    dup_keys = set(bank[bank.duplicated("_dup_key", keep=False)]["_dup_key"].unique())

    ledger_rows = ledger.to_dict("records")
    bank_rows = bank.to_dict("records")
    bank_used = [False] * len(bank_rows)

    # Prioritized match candidate extraction
    # Candidate levels:
    # Level 1: EXACT MATCH (Exact vendor name, identical date & amount)
    # Level 2: FUZZY MATCH (Vendor similarity >= 75%, amount match & date tolerance <= 3)
    # Level 3: AMOUNT MISMATCH (Vendor >= 75%, date <= 3, amount differs)
    # Level 4: DATE MISMATCH (Vendor >= 75%, amount match, date > 3)
    # Level 5: UNRESOLVED (Vendor >= 75%, both amount & date mismatch)
    candidates = []
    for li, lr in enumerate(ledger_rows):
        l_vendor = str(lr["vendor"]).strip()
        l_amt = float(lr["amount"])
        l_date = str(lr["date"])

        for bi, br in enumerate(bank_rows):
            b_desc = str(br["description"]).strip()
            b_amt = float(br["amount"])
            b_date = str(br["date"])

            s = calculate_similarity(l_vendor, b_desc)
            if s < FUZZY_THRESHOLD:
                continue

            amt_ok = amounts_match(l_amt, b_amt)
            d_diff = days_difference(l_date, b_date)
            date_ok = d_diff <= DATE_TOLERANCE
            is_exact_str = (l_vendor.upper() == b_desc.upper())

            if amt_ok and date_ok:
                if is_exact_str and d_diff == 0:
                    lvl = 1  # EXACT MATCH
                else:
                    lvl = 2  # FUZZY MATCH
            elif not amt_ok and date_ok:
                lvl = 3      # AMOUNT MISMATCH
            elif amt_ok and not date_ok:
                lvl = 4      # DATE MISMATCH
            else:
                lvl = 5      # UNRESOLVED

            amt_diff = abs(l_amt - b_amt)
            candidates.append((lvl, -s, d_diff, amt_diff, li, bi))

    # Sort candidates by level ascending, highest similarity first, smallest date/amount difference
    candidates.sort()

    ledger_assigned = [None] * len(ledger_rows)
    for lvl, neg_s, d_diff, amt_diff, li, bi in candidates:
        if ledger_assigned[li] is None and not bank_used[bi]:
            s = -neg_s
            lr = ledger_rows[li]
            br = bank_rows[bi]

            if lvl == 1:
                st = "MATCHED"
                diff_a, diff_d = None, None
                notes = None
            elif lvl == 2:
                st = "FUZZY_MATCHED"
                diff_a, diff_d = None, None
                notes = f"Fuzzy matched vendor with similarity {s}%."
            elif lvl == 3:
                st = "AMOUNT_MISMATCH"
                diff_a, diff_d = round(amt_diff, 2), None
                notes = f"Ledger: {lr['amount']}, Bank: {br['amount']}, Difference: {diff_a}"
            elif lvl == 4:
                st = "DATE_MISMATCH"
                diff_a, diff_d = None, d_diff
                notes = f"Ledger date: {lr['date']}, Bank date: {br['date']}, Difference: {diff_d} days"
            else:
                st = "UNRESOLVED"
                diff_a, diff_d = round(amt_diff, 2), d_diff
                notes = "Vendor matched but both amount and date differ significantly."

            conf = get_confidence(st, s)
            req_review = st in EXCEPTION_STATUSES

            ledger_assigned[li] = {
                "bank_idx": bi,
                "status": st,
                "confidence": conf,
                "requires_human_review": req_review,
                "amount_difference": diff_a,
                "date_difference_days": diff_d,
                "fuzzy_score": s,
                "notes": notes
            }
            bank_used[bi] = True

    # Assemble all results
    results: List[Dict[str, Any]] = []

    for li, lr in enumerate(ledger_rows):
        tid = str(lr["transaction_id"])
        gw = gw_map.get(tid, {})

        assigned = ledger_assigned[li]
        if assigned:
            br = bank_rows[assigned["bank_idx"]]
            b_vendor = br["description"]
            b_amount = float(br["amount"])
            b_date = str(br["date"])
            status = assigned["status"]
            conf = assigned["confidence"]
            req_review = assigned["requires_human_review"]
            amt_diff = assigned["amount_difference"]
            date_diff = assigned["date_difference_days"]
            fuzzy_s = assigned["fuzzy_score"]
            notes = assigned["notes"]
        else:
            b_vendor = None
            b_amount = None
            b_date = None
            status = "MISSING_BANK_RECORD"
            conf = get_confidence(status)
            req_review = True
            amt_diff = None
            date_diff = None
            fuzzy_s = None
            notes = "Transaction in ledger has no matching record in bank statement."

        results.append({
            "transaction_id": tid,
            "ledger_vendor": lr["vendor"],
            "ledger_amount": float(lr["amount"]),
            "ledger_date": str(lr["date"]),
            "bank_vendor": b_vendor,
            "bank_amount": b_amount,
            "bank_date": b_date,
            "gateway_merchant": gw.get("merchant"),
            "gateway_net_amount": float(gw["net_amount"]) if "net_amount" in gw else None,
            "gateway_settlement_date": gw.get("settlement_date"),
            "status": status,
            "confidence": conf,
            "requires_human_review": req_review,
            "amount_difference": amt_diff,
            "date_difference_days": date_diff,
            "fuzzy_score": fuzzy_s,
            "notes": notes
        })

    # Unmatched duplicate transactions from the bank side
    for bi, br in enumerate(bank_rows):
        if br["_dup_key"] in dup_keys and not bank_used[bi]:
            results.append({
                "transaction_id": f"DUP-{br['bank_reference']}",
                "ledger_vendor": "(no ledger match)",
                "ledger_amount": float(br["amount"]),
                "ledger_date": str(br["date"]),
                "bank_vendor": br["description"],
                "bank_amount": float(br["amount"]),
                "bank_date": str(br["date"]),
                "gateway_merchant": None,
                "gateway_net_amount": None,
                "gateway_settlement_date": None,
                "status": "DUPLICATE",
                "confidence": get_confidence("DUPLICATE"),
                "requires_human_review": True,
                "amount_difference": None,
                "date_difference_days": None,
                "fuzzy_score": None,
                "notes": f"Duplicate transaction identified in bank statement ({br['bank_reference']})"
            })

    # Calculate system metrics
    total_records = len(ledger_rows)
    exact_matches = sum(1 for r in results if r["status"] == "MATCHED")
    fuzzy_matches = sum(1 for r in results if r["status"] == "FUZZY_MATCHED")
    matched_records = exact_matches + fuzzy_matches
    amount_mismatches = sum(1 for r in results if r["status"] == "AMOUNT_MISMATCH")
    date_mismatches = sum(1 for r in results if r["status"] == "DATE_MISMATCH")
    missing_records = sum(1 for r in results if r["status"] == "MISSING_BANK_RECORD")
    duplicates = sum(1 for r in results if r["status"] == "DUPLICATE")
    unresolved_exceptions = sum(1 for r in results if r["status"] == "UNRESOLVED")
    match_rate = round((matched_records / total_records) * 100.0, 2) if total_records else 0.0

    metrics = {
        "total_records": total_records,
        "exact_matches": exact_matches,
        "fuzzy_matches": fuzzy_matches,
        "matched_records": matched_records,
        "amount_mismatches": amount_mismatches,
        "date_mismatches": date_mismatches,
        "missing_records": missing_records,
        "duplicates": duplicates,
        "unresolved_exceptions": unresolved_exceptions,
        "match_rate": match_rate
    }

    exceptions = [r for r in results if r["status"] in EXCEPTION_STATUSES]

    # Save to disk
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    with open(EXCEPTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(exceptions, f, indent=2, default=str)

    print(f"[Reconciliation Engine] Processed {total_records} records. Match rate: {match_rate}%")
    return {
        "metrics": metrics,
        "results": results,
        "exceptions": exceptions
    }


if __name__ == "__main__":
    run_reconciliation()
