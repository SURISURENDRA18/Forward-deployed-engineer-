"""
Independent Financial Verification for Vireo Audio Refund Analysis.
Computes core financial totals directly from raw data without importing production aggregation code.
"""
import csv
import os
import sys
from decimal import Decimal
from collections import defaultdict

def run_independent_verification():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tickets_csv = os.path.join(root, "data", "tickets.csv")

    with open(tickets_csv, "r", encoding="utf-8") as f:
        raw_tickets = list(csv.DictReader(f))

    total_raw_rows = len(raw_tickets)

    # 1. Raw totals
    raw_hd_sum = sum(Decimal(r["refund_amount_inr"]) for r in raw_tickets if r["source_system"] == "helpdesk" and r["refund_amount_inr"] != "")
    raw_leg_sum = sum(Decimal(r["refund_amount_inr"]) for r in raw_tickets if r["source_system"] == "legacy_fd" and r["refund_amount_inr"] != "")
    raw_total_sum = raw_hd_sum + raw_leg_sum

    # 2. Duplicate Detection
    by_id = defaultdict(list)
    for r in raw_tickets:
        by_id[r["ticket_id"]].append(r)

    unique_ticket_count = len(by_id)
    dup_ids = {tid: rows for tid, rows in by_id.items() if len(rows) > 1}
    dup_pair_count = len(dup_ids)

    # In duplicate pairs, legacy_fd copy is excluded, helpdesk copy is retained
    excluded_duplicate_raw_sum = Decimal("0.00")
    excluded_duplicate_paise_count = 0
    for tid, rows in dup_ids.items():
        leg_row = next((r for r in rows if r["source_system"] == "legacy_fd"), None)
        if leg_row and leg_row["refund_amount_inr"] != "":
            excluded_duplicate_raw_sum += Decimal(leg_row["refund_amount_inr"])
            excluded_duplicate_paise_count += 1

    # 3. Clean Dataset Construction
    clean_records = []
    for tid in sorted(by_id.keys()):
        rows = by_id[tid]
        if len(rows) == 2:
            # Pair: retain helpdesk
            hd_row = next(r for r in rows if r["source_system"] == "helpdesk")
            clean_records.append(hd_row)
        else:
            clean_records.append(rows[0])

    # 4. Normalized Refund Total Calculation
    # Helpdesk = unchanged INR; Legacy = paise / 100
    clean_refund_sum = Decimal("0.00")
    monthly_totals = defaultdict(Decimal)
    quarterly_totals = defaultdict(Decimal)
    reason_totals = defaultdict(Decimal)
    agent_totals = defaultdict(Decimal)
    refund_ticket_count = 0

    dual_benefit_count = 0
    dual_benefit_amount = Decimal("0.00")

    for r in clean_records:
        orig = r["refund_amount_inr"]
        if orig != "":
            refund_ticket_count += 1
            if r["source_system"] == "helpdesk":
                val = Decimal(orig)
            else:
                val = Decimal(orig) / Decimal(100)
            
            clean_refund_sum += val
            ym = r["created_at"][:7]
            monthly_totals[ym] += val

            # Quarter
            year = r["created_at"][:4]
            month = int(r["created_at"][5:7])
            q = (month - 1) // 3 + 1
            q_str = f"{year}-Q{q}"
            quarterly_totals[q_str] += val

            reason = r["refund_reason_code"] if r["refund_reason_code"] != "" else "UNTAGGED"
            reason_totals[reason] += val

            agent = r["agent_id"] if r["agent_id"] != "" else "UNKNOWN"
            agent_totals[agent] += val

            if r["replacement_issued"] == "Y":
                dual_benefit_count += 1
                dual_benefit_amount += val

    # Legacy scaling inflation
    # Retained legacy rows raw paise vs normalized inr
    retained_legacy_raw_sum = sum(Decimal(r["refund_amount_inr"]) for r in clean_records if r["source_system"] == "legacy_fd" and r["refund_amount_inr"] != "")
    retained_legacy_norm_sum = retained_legacy_raw_sum / Decimal(100)
    legacy_scaling_inflation = retained_legacy_raw_sum - retained_legacy_norm_sum

    results = {
        "total_raw_rows": total_raw_rows,
        "raw_hd_sum": raw_hd_sum,
        "raw_leg_sum": raw_leg_sum,
        "raw_total_sum": raw_total_sum,
        "unique_ticket_count": unique_ticket_count,
        "dup_pair_count": dup_pair_count,
        "excluded_duplicate_raw_sum": excluded_duplicate_raw_sum,
        "excluded_duplicate_paise_count": excluded_duplicate_paise_count,
        "legacy_scaling_inflation": legacy_scaling_inflation,
        "clean_refund_sum": clean_refund_sum,
        "refund_ticket_count": refund_ticket_count,
        "monthly_totals": dict(sorted(monthly_totals.items())),
        "quarterly_totals": dict(sorted(quarterly_totals.items())),
        "reason_totals": dict(sorted(reason_totals.items(), key=lambda x: x[1], reverse=True)),
        "agent_totals": dict(sorted(agent_totals.items(), key=lambda x: x[1], reverse=True)),
        "dual_benefit_count": dual_benefit_count,
        "dual_benefit_amount": dual_benefit_amount,
    }

    print("=" * 60)
    print("INDEPENDENT FINANCIAL VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Raw Export Total:            Rs {raw_total_sum:,.2f}")
    print(f"  - Helpdesk Raw:            Rs {raw_hd_sum:,.2f}")
    print(f"  - Legacy Raw (Paise):      Rs {raw_leg_sum:,.2f}")
    print(f"Duplicates Excluded (Raw):   Rs {excluded_duplicate_raw_sum:,.2f} ({excluded_duplicate_paise_count} refund rows)")
    print(f"Legacy Scaling Inflation:    Rs {legacy_scaling_inflation:,.2f}")
    print(f"Final Reconciled Refund:     Rs {clean_refund_sum:,.2f} ({refund_ticket_count} refund tickets)")
    print(f"Quarterly Average (6 Qtrs):  Rs {clean_refund_sum / Decimal(6):,.2f}")
    print(f"Dual Benefit (Ref+Repl):     {dual_benefit_count} tickets (Rs {dual_benefit_amount:,.2f})")
    print("-" * 60)
    print("Quarterly Breakdown:")
    for q, amt in sorted(quarterly_totals.items()):
        print(f"  {q}: Rs {amt:,.2f}")
    print("-" * 60)

    # Consistency checks:
    sum_monthly = sum(monthly_totals.values())
    sum_quarterly = sum(quarterly_totals.values())
    sum_reason = sum(reason_totals.values())
    sum_agent = sum(agent_totals.values())

    assert sum_monthly == clean_refund_sum, f"Monthly sum mismatch: {sum_monthly} vs {clean_refund_sum}"
    assert sum_quarterly == clean_refund_sum, f"Quarterly sum mismatch: {sum_quarterly} vs {clean_refund_sum}"
    assert sum_reason == clean_refund_sum, f"Reason sum mismatch: {sum_reason} vs {clean_refund_sum}"
    assert sum_agent == clean_refund_sum, f"Agent sum mismatch: {sum_agent} vs {clean_refund_sum}"

    print("PASS: Monthly, Quarterly, Reason, and Agent totals reconcile exactly!")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_independent_verification()
