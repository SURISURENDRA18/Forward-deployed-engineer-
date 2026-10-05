# VIREO AUDIO — TECHNICAL ASSESSMENT SUBMISSION FORM

## 1. Candidate & Submission Details
- **Candidate Name:** Senior Analytics Engineer & AI QA Auditor
- **Date of Submission:** 5 October 2026
- **Repository Name:** `vireo-refund-analysis`
- **Assessment Track:** Support Data Pack & Financial Reconciliation (Set C)

---

## 2. Core Financial Results & Reconciliation
- **Raw Export Total:** Rs 23,01,24,081.00 (~Rs 23.01 Crore across 6 quarters)
- **Re-import Duplicate Adjustment:** Excluded 638 duplicate records (125 refund-bearing tickets totaling Rs 3,61,01,100.00 raw / Rs 3,61,011.00 normalized)
- **Legacy Currency Subunit Adjustment:** Normalized 3,236 legacy tickets from paise to INR (factor of 100, adjusting Rs 18,73,13,049.00 in artificial subunit inflation)
- **Final Reconciled Net Refund Amount:** **Rs 67,09,932.00**
- **Average Quarterly Refund Spend:** **Rs 11,18,322.00 (~Rs 11.18 Lakh per quarter)**
- **Reconciliation Verdict:** The Helpdesk Management estimate of ~Rs 11 Lakh per quarter is verified as correct with 100% mathematical precision. Finance’s export was unadjusted for migration re-imports and Freshdesk paise subunit storage.

---

## 3. Measurable Business Goal
- **Business Goal Statement:**  
  Reduce the dual-benefit policy exception rate (orders receiving both a cash refund and replacement hardware) from **7.09% of refund tickets (166 tickets) to 0.0%**, delivering a documented recurring savings of **Rs 1,45,193.50 per quarter** (Rs 8,71,161.00 total across 6 quarters in cash refunds, product costs, and courier shipping).
- **Secondary Goal:**  
  Remove `GW-OTHER` as the default dropdown option to reduce unclassified refunds from **42.35% by volume (Rs 29.07 Lakh total spend)** to under 5%, establishing operational visibility over Rs 4.85 Lakh per quarter in misclassified returns.

---

## 4. Engineering Verification & Clean-Room Testing
- **Test Suite Results:** 23 tests collected, 23 passed, 0 failed (100% pass rate in 4.7s).
- **Independent Validation Path:** `scripts/independent_verify.py` independently recalculates raw totals, deduplication, currency conversions, and multidimensional aggregations without relying on production code, achieving 100% exact parity.
- **Cross-Report Consistency:**  
  $\text{Monthly Total} = \text{Quarterly Total} = \text{Reason Code Total} = \text{Agent Total} = \text{Rs 6,709,932.00}$.

---

## 5. AI Tooling, Prompts & Cost Disclosure
- **AI / LLM Tooling Utilized:**
  - Coding & Architecture Assistance: Antigravity IDE (Gemini 3.8 Flash / Claude 3.5 Sonnet architecture).
  - NLP Text Mining: Deterministic keyword-intent mining engine benchmarked against a few-shot structured LLM classification prompt.
- **Total API Spend:** $0.00 (Designed to run deterministically on clean machines without external API tokens or paid cloud keys).
- **AI Prompt Evolution:** Detailed in `docs/PROMPT_EVOLUTION.md` (transitioned from unconstrained generative prompt to structured schema and deterministic audit engine).
- **Validation Accuracy:** 96.00% benchmark accuracy across 50 double-blind evaluated sample tickets.
- **Discarded Approaches:**
  - Autonomous LLM ledger overwrite: Discarded to guarantee zero hallucination risk on financial balances.
  - Sentiment-based refund filtering: Discarded as customer sentiment showed zero correlation with return validity.
  - Paid cloud API dependence for runtime execution: Discarded to ensure clean-machine portability and zero cost.

---

## 6. Scope Decisions & Limitations
- Data window evaluated: 1 January 2025 to 30 June 2026.
- Payment gateway merchant processing fees, chargeback fines, and scrap recovery values are managed in external ERP systems and were excluded from this support helpdesk analysis.
