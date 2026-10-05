# DATA QUALITY & AUDIT FINDINGS REPORT

## 1. Overview
This report details all data quality anomalies identified during the inspection, enrichment, and audit of the Vireo Audio support dataset (12,238 raw tickets).

## 2. Key Data Quality Findings

### A. System Migration Duplicates
- **Anomaly**: 638 `ticket_id` values occur twice in `tickets.csv`.
- **Root Cause**: Freshdesk-to-Helpdesk migration re-import reconciliation.
- **Resolution**: Retained `helpdesk` row as authoritative; excluded `legacy_fd` duplicate. Verified 0 metadata field mismatches.

### B. Legacy Currency Unit Scaling
- **Anomaly**: `legacy_fd` export values stored in paise (scaled x100).
- **Resolution**: Applied exact decimal division by 100 on retained `legacy_fd` records.

### C. Missing Order IDs & Relational Fallback Join
- **Anomaly**: 4,127 tickets (33.72%) lack an `order_id`.
- **Resolution**: Implemented fallback join on `(customer_id, product_sku)` against `orders.csv`. Achieved 100% relational join resolution across all 11,600 clean tickets.

### D. Policy §5 Dual Benefit Compliance
- **Anomaly**: 166 clean tickets contain both `refund_amount_inr_normalized > 0` and `replacement_issued == 'Y'`.
- **Resolution**: Flagged with `REFUND_AND_REPLACEMENT_CONFLICT` for operational audit without excluding from financial reporting.

### E. Goodwill Credit Cap Breaches
- **Anomaly**: 879 tickets with reason `GW-OTHER` exceed the Rs 500 goodwill cap specified in Policy §5.
