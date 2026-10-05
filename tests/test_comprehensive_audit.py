"""
Comprehensive Audit & Adversarial Test Suite for Vireo Refund Analysis
======================================================================
Verifies financial correctness, schema validation, policy compliance,
edge cases, and cross-report reconciliations.
"""

import csv
import os
from decimal import Decimal
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "data")
output_dir = os.path.join(project_root, "output")

@pytest.fixture(scope="module")
def loaded_data():
    with open(os.path.join(data_dir, "tickets.csv"), "r", encoding="utf-8") as f:
        raw_tickets = list(csv.DictReader(f))
    with open(os.path.join(data_dir, "agents.csv"), "r", encoding="utf-8") as f:
        raw_agents = list(csv.DictReader(f))
    with open(os.path.join(data_dir, "orders.csv"), "r", encoding="utf-8") as f:
        raw_orders = list(csv.DictReader(f))
    with open(os.path.join(data_dir, "customers.csv"), "r", encoding="utf-8") as f:
        raw_customers = list(csv.DictReader(f))
    with open(os.path.join(data_dir, "products.csv"), "r", encoding="utf-8") as f:
        raw_products = list(csv.DictReader(f))
    with open(os.path.join(output_dir, "clean_tickets.csv"), "r", encoding="utf-8") as f:
        clean_tickets = list(csv.DictReader(f))
    with open(os.path.join(output_dir, "enriched_tickets.csv"), "r", encoding="utf-8") as f:
        enriched_tickets = list(csv.DictReader(f))
    with open(os.path.join(output_dir, "duplicate_audit.csv"), "r", encoding="utf-8") as f:
        dup_audit = list(csv.DictReader(f))
    return {
        "raw_tickets": raw_tickets,
        "raw_agents": raw_agents,
        "raw_orders": raw_orders,
        "raw_customers": raw_customers,
        "raw_products": raw_products,
        "clean_tickets": clean_tickets,
        "enriched_tickets": enriched_tickets,
        "dup_audit": dup_audit
    }

# 1. Schema Validation
def test_raw_schemas(loaded_data):
    assert len(loaded_data["raw_tickets"]) == 12238
    assert len(loaded_data["raw_agents"]) == 44
    assert len(loaded_data["raw_orders"]) == 15000
    assert len(loaded_data["raw_customers"]) == 9500
    assert len(loaded_data["raw_products"]) == 14

# 2. Duplicate Detection & Pairing
def test_duplicate_pairing(loaded_data):
    raw = loaded_data["raw_tickets"]
    from collections import Counter
    counts = Counter(r["ticket_id"] for r in raw)
    dup_ids = [tid for tid, count in counts.items() if count > 1]
    assert len(dup_ids) == 638, f"Expected 638 duplicate ticket IDs, found {len(dup_ids)}"
    for tid, count in counts.items():
        assert count in (1, 2), f"Ticket {tid} appeared {count} times (expected 1 or 2)"

# 3. Duplicate Audit Schema and Logic
def test_duplicate_audit_schema_and_logic(loaded_data):
    audit = loaded_data["dup_audit"]
    assert len(audit) == 12238
    expected_fields = {"ticket_id", "duplicate_group", "source_system", "classification", "retained_or_excluded", "reason"}
    assert set(audit[0].keys()) == expected_fields
    excluded = [r for r in audit if r["retained_or_excluded"] == "EXCLUDED"]
    assert len(excluded) == 638
    for r in excluded:
        assert r["source_system"] == "legacy_fd"

# 4. Clean Dataset Integrity
def test_clean_dataset_size(loaded_data):
    clean = loaded_data["clean_tickets"]
    assert len(clean) == 11600
    clean_ids = set(r["ticket_id"] for r in clean)
    assert len(clean_ids) == 11600

# 5. Financial Reconciliation: Raw, Deduplicated, Normalized
def test_financial_reconciliation(loaded_data):
    clean = loaded_data["clean_tickets"]
    refund_rows = [r for r in clean if r["refund_amount_inr_normalized"] != ""]
    assert len(refund_rows) == 2340
    total_refund = sum(Decimal(r["refund_amount_inr_normalized"]) for r in refund_rows)
    assert total_refund == Decimal("6709932.00")
    quarterly_avg = total_refund / Decimal(6)
    assert quarterly_avg == Decimal("1118322.00")

# 6. Legacy Money Empirical Ratio (100x)
def test_legacy_money_100x_ratio(loaded_data):
    raw = loaded_data["raw_tickets"]
    by_id = {}
    for r in raw:
        by_id.setdefault(r["ticket_id"], []).append(r)
    
    paired_with_refunds = []
    for tid, rows in by_id.items():
        if len(rows) == 2:
            hd = next(r for r in rows if r["source_system"] == "helpdesk")
            leg = next(r for r in rows if r["source_system"] == "legacy_fd")
            if hd["refund_amount_inr"] and leg["refund_amount_inr"]:
                paired_with_refunds.append((Decimal(hd["refund_amount_inr"]), Decimal(leg["refund_amount_inr"])))
    
    assert len(paired_with_refunds) == 125
    for hd_val, leg_val in paired_with_refunds:
        assert leg_val == hd_val * 100, f"Expected 100x ratio, got {leg_val} vs {hd_val}"

# 7. Dual Benefit Policy Rule Check
def test_dual_benefit_count_and_isolation(loaded_data):
    clean = loaded_data["clean_tickets"]
    dual = [r for r in clean if r["refund_amount_inr_normalized"] and Decimal(r["refund_amount_inr_normalized"]) > 0 and r["replacement_issued"] == "Y"]
    assert len(dual) == 166, f"Expected 166 dual benefit tickets in clean dataset, got {len(dual)}"
    for r in dual:
        assert "REFUND_AND_REPLACEMENT_CONFLICT" in r["quality_flags"]

# 8. Goodwill Cap Rule Check (Rs 500)
def test_goodwill_cap_flagging(loaded_data):
    clean = loaded_data["clean_tickets"]
    gw_over_500 = [
        r for r in clean
        if r["refund_reason_code"] == "GW-OTHER"
        and r["refund_amount_inr_normalized"]
        and Decimal(r["refund_amount_inr_normalized"]) > Decimal("500.00")
    ]
    assert len(gw_over_500) == 879
    for r in gw_over_500:
        assert "GOODWILL_EXCEEDS_500_CAP" in r["quality_flags"]

# 9. Fallback Order Join Check
def test_fallback_order_join(loaded_data):
    raw = loaded_data["raw_tickets"]
    raw_blank = [r for r in raw if r["order_id"] == ""]
    assert len(raw_blank) == 4127, "Raw tickets with blank order_id must be 4127"

    enriched = loaded_data["enriched_tickets"]
    blank_orig = [r for r in enriched if r["order_id"] == ""]
    assert len(blank_orig) == 3899, "Clean tickets with blank order_id must be 3899"
    matched_fallback = [r for r in blank_orig if r["order_join_method"] == "FALLBACK_CUST_SKU"]
    assert len(matched_fallback) == 3899, "100% of blank order_id clean tickets must match via customer_id + sku"

# 10. Agent Attribution & Roster Date Matching
def test_agent_roster_integrity(loaded_data):
    enriched = loaded_data["enriched_tickets"]
    for r in enriched:
        assert r["agent_name"] != "", f"Agent name missing for ticket {r['ticket_id']}"
        assert r["agent_team"] != "", f"Agent team missing for ticket {r['ticket_id']}"
        assert r["agent_tier"] in ("1", "2"), f"Invalid agent tier for ticket {r['ticket_id']}"

# 11. CSAT Blank Handling
def test_csat_blank_vs_zero(loaded_data):
    clean = loaded_data["clean_tickets"]
    valid_scores = [float(r["csat_score"]) for r in clean if r["csat_score"] != ""]
    blank_scores = [r for r in clean if r["csat_score"] == ""]
    assert len(valid_scores) == 5237
    assert len(blank_scores) == 6363
    avg_csat = sum(valid_scores) / len(valid_scores)
    assert 3.4 <= avg_csat <= 3.6
    # If blanks were incorrectly converted to 0:
    wrong_avg = sum(valid_scores) / len(clean)
    assert wrong_avg < 2.0, "Zero-treated CSAT would artificially depress average below 2.0"

# 12. Cross-Report Reconciliation Check
def test_cross_report_reconciliation(loaded_data):
    from scripts.independent_verify import run_independent_verification
    res = run_independent_verification()
    expected_total = Decimal("6709932.00")
    assert res["clean_refund_sum"] == expected_total
    assert sum(res["monthly_totals"].values()) == expected_total
    assert sum(res["quarterly_totals"].values()) == expected_total
    assert sum(res["reason_totals"].values()) == expected_total
    assert sum(res["agent_totals"].values()) == expected_total

# 13. Idempotent Execution Check
def test_pipeline_idempotence():
    from scripts.run_pipeline import run_pipeline
    run_pipeline()
    clean_path = os.path.join(output_dir, "clean_tickets.csv")
    with open(clean_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 11600
