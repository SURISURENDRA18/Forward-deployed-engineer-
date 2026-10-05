# SYSTEM DOCUMENTATION & DATA DICTIONARY

## Pipeline Architecture & Workflow
1. **Data Inspection**: Verify raw data shapes and fields in `data/`.
2. **Duplicate Reconciliation**: Field-by-field audit of 638 duplicate pairs.
3. **Clean Dataset Creation**: Deduplicate to 11,600 rows and normalize legacy paise amounts to INR ($\div 100$).
4. **Relational Enrichment**: Join with `orders.csv`, `products.csv`, `customers.csv`, `agents.csv`.
5. **Refund Reconciliation**: Reconcile Finance vs Helpdesk figures.
6. **Monthly & AI Analysis**: Aggregations by reason/agent and NLP intent classification.

## Data Dictionary: `clean_tickets.csv`
- `ticket_id`: Unique support ticket identifier (Primary Key).
- `created_at`: Ticket creation timestamp (IST).
- `refund_amount_original`: Original raw refund value exported.
- `refund_amount_inr_normalized`: Normalized refund amount in INR (Decimal-safe).
- `normalization_rule`: Label (`HELPDESK_INR_UNCHANGED`, `LEGACY_FD_PAISE_DIVIDED_BY_100`, `NO_REFUND_AMOUNT`).
- `quality_flags`: Semi-colon separated quality flags.
- `original_row_reference`: 1-indexed row number in raw `data/tickets.csv`.
