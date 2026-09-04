# -*- coding: utf-8 -*-
"""data_generator.py – Synthetic Financial Data Generator
=======================================================
Generates realistic financial records across three sources:
1. internal_ledger.csv (60 records)
2. bank_statement.csv (59 records)
3. payment_gateway.csv (55 records)

Intentionally includes:
- 40 exact matches
- 8 vendor name variations
- 4 amount mismatches
- 3 missing bank transactions
- 2 duplicate bank transactions
- 3 date mismatches
- 2 unresolved records
"""

import os
import random
from datetime import date, timedelta
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEDGER_CSV = os.path.join(DATA_DIR, "internal_ledger.csv")
BANK_CSV = os.path.join(DATA_DIR, "bank_statement.csv")
GATEWAY_CSV = os.path.join(DATA_DIR, "payment_gateway.csv")

os.makedirs(DATA_DIR, exist_ok=True)
random.seed(42)

# Standard canonical vendors
EXACT_VENDORS = [
    ("Amazon India",        "Amazon India",           "Amazon India"),
    ("Microsoft Azure",     "Microsoft Azure",        "Microsoft Azure"),
    ("Google Cloud",        "Google Cloud",           "Google Cloud"),
    ("Swiggy",              "Swiggy",                 "Swiggy"),
    ("Uber",                "Uber",                   "Uber"),
    ("Zomato",              "Zomato",                 "Zomato"),
    ("Adobe Systems",       "Adobe Systems",          "Adobe Systems"),
    ("Netflix",             "Netflix",                "Netflix"),
    ("AWS",                 "AWS",                    "AWS"),
    ("Razorpay",            "Razorpay",               "Razorpay"),
    ("Office Supplies Co",  "Office Supplies Co",     "Office Supplies Co"),
    ("Tata Communications", "Tata Communications",   "Tata Communications"),
]

# 8 Realistic vendor variations for bank statements
FUZZY_PAIRS = [
    ("Amazon India",        "AMAZON PAY INDIA",       "Amazon India"),
    ("Microsoft Azure",     "MS AZURE SERVICES",      "Microsoft Azure"),
    ("Google Cloud",        "GOOGLE *CLOUD",          "Google Cloud"),
    ("Swiggy",              "SWIGGY ONLINE",          "Swiggy"),
    ("Uber",                "UBER* TRIP",             "Uber"),
    ("Zomato",              "ZOMATO LTD",             "Zomato"),
    ("Adobe Systems",       "ADOBE INC",              "Adobe Systems"),
    ("Netflix",             "NETFLIX.COM",            "Netflix"),
]

CATEGORIES = {
    "Amazon India": "E-Commerce",
    "Microsoft Azure": "Cloud",
    "Google Cloud": "Cloud",
    "Swiggy": "Food",
    "Uber": "Travel",
    "Zomato": "Food",
    "Adobe Systems": "Software",
    "Netflix": "Entertainment",
    "AWS": "Cloud",
    "Razorpay": "Finance",
    "Office Supplies Co": "Office",
    "Tata Communications": "Telecom",
}

BASE_AMOUNTS = {
    "Amazon India": 5000,
    "Microsoft Azure": 12000,
    "Google Cloud": 8000,
    "Swiggy": 800,
    "Uber": 650,
    "Zomato": 950,
    "Adobe Systems": 3500,
    "Netflix": 649,
    "AWS": 9500,
    "Razorpay": 2500,
    "Office Supplies Co": 1800,
    "Tata Communications": 4500,
}

START_DATE = date(2026, 8, 1)
END_DATE = date(2026, 8, 31)


def _amount(vendor: str, jitter: float = 0.15) -> float:
    base = BASE_AMOUNTS.get(vendor, 2000)
    return round(base * (1 + random.uniform(-jitter, jitter)), 2)


def _date(start: date = START_DATE, end: date = END_DATE) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def generate_data() -> dict:
    """Generate internal_ledger.csv, bank_statement.csv, and payment_gateway.csv."""
    ledger_rows, bank_rows, gateway_rows = [], [], []
    txn = 1
    bnk = 1001
    sett = 1

    # 1. ~40 Exact Matches
    for _ in range(40):
        vl, vb, vg = EXACT_VENDORS[random.randint(0, len(EXACT_VENDORS) - 1)]
        amt = _amount(vl)
        d = _date()
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": d.isoformat(),
            "vendor": vl,
            "amount": amt,
            "category": CATEGORIES[vl],
            "status": "Paid"
        })
        bank_rows.append({
            "bank_reference": f"BNK{bnk}",
            "date": d.isoformat(),
            "description": vb,
            "amount": amt,
            "transaction_type": "Debit"
        })
        gateway_rows.append({
            "settlement_id": f"SET{sett:03d}",
            "transaction_reference": tid,
            "settlement_date": (d + timedelta(days=1)).isoformat(),
            "merchant": vg,
            "gross_amount": amt,
            "fee": round(amt * 0.01, 2),
            "net_amount": round(amt * 0.99, 2)
        })
        txn += 1
        bnk += 1
        sett += 1

    # 2. ~8 Vendor Variations (Fuzzy Matches)
    for vl, vb, vg in FUZZY_PAIRS:
        amt = _amount(vl)
        d = _date()
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": d.isoformat(),
            "vendor": vl,
            "amount": amt,
            "category": CATEGORIES[vl],
            "status": "Paid"
        })
        bank_rows.append({
            "bank_reference": f"BNK{bnk}",
            "date": d.isoformat(),
            "description": vb,
            "amount": amt,
            "transaction_type": "Debit"
        })
        gateway_rows.append({
            "settlement_id": f"SET{sett:03d}",
            "transaction_reference": tid,
            "settlement_date": (d + timedelta(days=1)).isoformat(),
            "merchant": vg,
            "gross_amount": amt,
            "fee": round(amt * 0.01, 2),
            "net_amount": round(amt * 0.99, 2)
        })
        txn += 1
        bnk += 1
        sett += 1

    # 3. ~4 Amount Mismatches
    amt_mismatch_vendors = [
        ("Microsoft Azure", "MS AZURE SERVICES", "Microsoft Azure"),
        ("Google Cloud", "GOOGLE *CLOUD", "Google Cloud"),
        ("AWS", "AMAZON WEB SERVICES", "AWS"),
        ("Tata Communications", "TATA COMM LTD", "Tata Communications"),
    ]
    for vl, vb, vg in amt_mismatch_vendors:
        l_amt = _amount(vl)
        b_amt = round(l_amt + random.choice([-150.0, 150.0, -200.0, 250.0]), 2)
        d = _date()
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": d.isoformat(),
            "vendor": vl,
            "amount": l_amt,
            "category": CATEGORIES[vl],
            "status": "Paid"
        })
        bank_rows.append({
            "bank_reference": f"BNK{bnk}",
            "date": d.isoformat(),
            "description": vb,
            "amount": b_amt,
            "transaction_type": "Debit"
        })
        gateway_rows.append({
            "settlement_id": f"SET{sett:03d}",
            "transaction_reference": tid,
            "settlement_date": (d + timedelta(days=1)).isoformat(),
            "merchant": vg,
            "gross_amount": l_amt,
            "fee": round(l_amt * 0.01, 2),
            "net_amount": round(l_amt * 0.99, 2)
        })
        txn += 1
        bnk += 1
        sett += 1

    # 4. ~3 Date Mismatches
    date_mismatch_vendors = [
        ("Razorpay", "Razorpay", "Razorpay"),
        ("Office Supplies Co", "Office Supplies Co", "Office Supplies Co"),
        ("Adobe Systems", "Adobe Systems", "Adobe Systems"),
    ]
    for vl, vb, vg in date_mismatch_vendors:
        amt = _amount(vl)
        l_date = _date(end=END_DATE - timedelta(days=12))
        b_date = l_date + timedelta(days=random.randint(6, 10))
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": l_date.isoformat(),
            "vendor": vl,
            "amount": amt,
            "category": CATEGORIES[vl],
            "status": "Paid"
        })
        bank_rows.append({
            "bank_reference": f"BNK{bnk}",
            "date": b_date.isoformat(),
            "description": vb,
            "amount": amt,
            "transaction_type": "Debit"
        })
        gateway_rows.append({
            "settlement_id": f"SET{sett:03d}",
            "transaction_reference": tid,
            "settlement_date": (b_date + timedelta(days=1)).isoformat(),
            "merchant": vg,
            "gross_amount": amt,
            "fee": round(amt * 0.01, 2),
            "net_amount": round(amt * 0.99, 2)
        })
        txn += 1
        bnk += 1
        sett += 1

    # 5. ~3 Missing Bank Transactions (Ledger only)
    for vl in ["Netflix", "Zomato", "Swiggy"]:
        amt = _amount(vl)
        d = _date()
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": d.isoformat(),
            "vendor": vl,
            "amount": amt,
            "category": CATEGORIES[vl],
            "status": "Paid"
        })
        txn += 1

    # 6. ~2 Duplicate Transactions in Bank
    dup_src1 = bank_rows[0]
    dup_src2 = bank_rows[1]
    bank_rows.append({
        "bank_reference": f"BNK{bnk}",
        "date": dup_src1["date"],
        "description": dup_src1["description"],
        "amount": dup_src1["amount"],
        "transaction_type": "Debit"
    })
    bnk += 1
    bank_rows.append({
        "bank_reference": f"BNK{bnk}",
        "date": dup_src2["date"],
        "description": dup_src2["description"],
        "amount": dup_src2["amount"],
        "transaction_type": "Debit"
    })
    bnk += 1

    # 7. Unresolved Transactions (vendor match, but both amount and date mismatch)
    unresolved_vendors = [
        ("Google Cloud", "GOOGLE *CLOUD", "Google Cloud"),
        ("Tata Communications", "TATA COMM LTD", "Tata Communications"),
    ]
    for vl, vb, vg in unresolved_vendors:
        l_amt = _amount(vl)
        b_amt = round(l_amt + 500.0, 2)
        l_date = _date(end=END_DATE - timedelta(days=12))
        b_date = l_date + timedelta(days=15)
        tid = f"TXN{txn:03d}"
        ledger_rows.append({
            "transaction_id": tid,
            "date": l_date.isoformat(),
            "vendor": vl,
            "amount": l_amt,
            "category": CATEGORIES[vl],
            "status": "Pending"
        })
        bank_rows.append({
            "bank_reference": f"BNK{bnk}",
            "date": b_date.isoformat(),
            "description": vb,
            "amount": b_amt,
            "transaction_type": "Debit"
        })
        txn += 1
        bnk += 1

    # Save to CSV files
    pd.DataFrame(ledger_rows).to_csv(LEDGER_CSV, index=False)
    pd.DataFrame(bank_rows).to_csv(BANK_CSV, index=False)
    pd.DataFrame(gateway_rows).to_csv(GATEWAY_CSV, index=False)

    counts = {
        "ledger": len(ledger_rows),
        "bank": len(bank_rows),
        "gateway": len(gateway_rows)
    }
    print(f"[DataGenerator] Ledger: {counts['ledger']}, Bank: {counts['bank']}, Gateway: {counts['gateway']}")
    return counts


if __name__ == "__main__":
    generate_data()
