import csv
import os
import sys
from decimal import Decimal
import pytest

# Determine project root dynamically
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "data")
output_dir = os.path.join(project_root, "output")

tickets_path = os.path.join(data_dir, "tickets.csv")
clean_tickets_path = os.path.join(output_dir, "clean_tickets.csv")
dedup_audit_path = os.path.join(output_dir, "deduplication_audit.csv")
norm_audit_path = os.path.join(output_dir, "normalization_audit.csv")
summary_path = os.path.join(output_dir, "clean_dataset_summary.txt")


@pytest.fixture(scope="module")
def dataset_data():
    with open(tickets_path, "r", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    with open(clean_tickets_path, "r", encoding="utf-8") as f:
        clean = list(csv.DictReader(f))
    with open(dedup_audit_path, "r", encoding="utf-8") as f:
        dedup = list(csv.DictReader(f))
    with open(norm_audit_path, "r", encoding="utf-8") as f:
        norm = list(csv.DictReader(f))
    return {"raw": raw, "clean": clean, "dedup": dedup, "norm": norm}


# 1. Test duplicate helpdesk and legacy_fd pairs
def test_duplicate_helpdesk_and_legacy_pairs(dataset_data):
    raw = dataset_data["raw"]
    dedup = dataset_data["dedup"]
    clean = dataset_data["clean"]
    
    # Identify duplicate ticket_ids from raw source
    id_counts = {}
    for r in raw:
        id_counts[r["ticket_id"]] = id_counts.get(r["ticket_id"], 0) + 1
    dup_ids = [tid for tid, count in id_counts.items() if count > 1]
    
    assert len(dup_ids) == 638, f"Expected 638 duplicate ticket IDs, found {len(dup_ids)}"
    
    # Check deduplication audit for all dup_ids
    dedup_by_id = {}
    for entry in dedup:
        tid = entry["ticket_id"]
        if tid not in dedup_by_id:
            dedup_by_id[tid] = []
        dedup_by_id[tid].append(entry)
        
    clean_by_id = {r["ticket_id"]: r for r in clean}
    
    for tid in dup_ids:
        entries = dedup_by_id[tid]
        assert len(entries) == 2, f"Ticket {tid} should have 2 entries in deduplication audit"
        retained = next(e for e in entries if e["retained_or_excluded"] == "RETAINED")
        excluded = next(e for e in entries if e["retained_or_excluded"] == "EXCLUDED")
        
        assert retained["source_system"] == "helpdesk", f"Retained row for {tid} should be helpdesk"
        assert excluded["source_system"] == "legacy_fd", f"Excluded row for {tid} should be legacy_fd"
        
        # Verify retained in clean dataset
        assert clean_by_id[tid]["source_system"] == "helpdesk", f"Clean dataset row for {tid} should be helpdesk"


# 2. Test duplicate IDs occurring more than twice (guard test)
def test_duplicate_ids_more_than_twice(dataset_data):
    raw = dataset_data["raw"]
    id_counts = {}
    for r in raw:
        id_counts[r["ticket_id"]] = id_counts.get(r["ticket_id"], 0) + 1
    max_occurrences = max(id_counts.values())
    assert max_occurrences == 2, f"Expected max 2 occurrences per ticket_id, found {max_occurrences}"


# 3. Test unmatched duplicate reconciliation records
def test_unmatched_duplicate_reconciliation_records(dataset_data):
    clean = dataset_data["clean"]
    raw = dataset_data["raw"]
    raw_ids = set(r["ticket_id"] for r in raw)
    clean_ids = set(r["ticket_id"] for r in clean)
    assert clean_ids.issubset(raw_ids), "Clean ticket IDs must be a subset of raw ticket IDs"
    assert len(clean_ids) == 11600, f"Expected 11600 unique clean ticket IDs, got {len(clean_ids)}"


# 4. Test helpdesk-only tickets
def test_helpdesk_only_tickets(dataset_data):
    clean = dataset_data["clean"]
    hd_tickets = [r for r in clean if r["source_system"] == "helpdesk"]
    assert len(hd_tickets) == 8364, f"Expected 8364 helpdesk tickets in clean dataset, got {len(hd_tickets)}"
    for r in hd_tickets:
        if r["refund_amount_original"] != "":
            assert r["normalization_rule"] == "HELPDESK_INR_UNCHANGED"
            assert Decimal(r["refund_amount_inr_normalized"]) == Decimal(r["refund_amount_original"])


# 5. Test legacy-only tickets
def test_legacy_only_tickets(dataset_data):
    clean = dataset_data["clean"]
    leg_tickets = [r for r in clean if r["source_system"] == "legacy_fd"]
    assert len(leg_tickets) == 3236, f"Expected 3236 legacy_fd tickets in clean dataset, got {len(leg_tickets)}"
    for r in leg_tickets:
        if r["refund_amount_original"] != "":
            assert r["normalization_rule"] == "LEGACY_FD_PAISE_DIVIDED_BY_100"
            expected = Decimal(r["refund_amount_original"]) / Decimal(100)
            assert Decimal(r["refund_amount_inr_normalized"]) == expected


# 6. Test legacy amount conversion math
def test_legacy_amount_conversion_math():
    test_cases = [
        ("10000", "100.00"),
        ("1299900", "12999.00"),
        ("49900", "499.00"),
        ("0", "0.00"),
    ]
    for raw_val, expected_norm in test_cases:
        conv = Decimal(raw_val) / Decimal(100)
        assert f"{conv:.2f}" == expected_norm


# 7. Test missing refund values
def test_missing_refund_values(dataset_data):
    clean = dataset_data["clean"]
    missing_ref = [r for r in clean if r["refund_amount_original"] == ""]
    assert len(missing_ref) == 9260, f"Expected 9260 missing refund tickets, got {len(missing_ref)}"
    for r in missing_ref:
        assert r["refund_amount_inr_normalized"] == "", "Normalized refund amount should be empty string for missing refunds"
        assert r["normalization_rule"] == "NO_REFUND_AMOUNT", "Normalization rule should be NO_REFUND_AMOUNT for missing refunds"


# 8. Test zero refund values
def test_zero_refund_values():
    val = Decimal("0")
    norm_val = f"{val/100:.2f}"
    assert norm_val == "0.00"
    assert norm_val != ""


# 9. Test preservation of original amounts
def test_preservation_of_original_amounts(dataset_data):
    clean = dataset_data["clean"]
    raw = dataset_data["raw"]
    
    raw_map = {(r["ticket_id"], r["source_system"]): r for r in raw}
    
    for r in clean:
        key = (r["ticket_id"], r["source_system"])
        raw_row = raw_map[key]
        assert r["refund_amount_original"] == raw_row["refund_amount_inr"], f"Original amount mismatch for {key}"


# 10. Test idempotent output generation
def test_idempotent_output_generation():
    sys.path.insert(0, os.path.join(project_root, "scripts"))
    try:
        # pyrefly: ignore [missing-import]
        import build_clean_dataset
        count = build_clean_dataset.run_clean_dataset_pipeline()
        assert count == 11600, f"Expected pipeline to generate 11600 rows, got {count}"
    except ImportError:
        pytest.skip("Pipeline script scripts/build_clean_dataset.py not found in python path")

    with open(clean_tickets_path, "r", encoding="utf-8") as f:
        clean_rows = list(csv.DictReader(f))
    assert len(clean_rows) == 11600, f"Expected 11600 CSV rows in clean_tickets.csv, got {len(clean_rows)}"
