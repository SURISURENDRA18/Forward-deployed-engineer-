# EXECUTIVE MEMORANDUM

**TO:** Arjun Mehta, Finance Controller, Vireo Audio  
**FROM:** Senior Analytics & Financial Verification Lead  
**DATE:** 5 October 2026  
**SUBJECT:** Resolution of Support Refund Discrepancy & Operational Audit (Q1 2025 – Q2 2026)  
**DELIVERABLE:** Briefing for Board Presentation (24 September Pack)  

---

### 1. Reconciling the Rs 1 Crore vs Rs 11 Lakh Discrepancy

Your initial data export indicated refund expenditures exceeding **Rs 23.01 Crore across 6 quarters (~Rs 3.83 Crore per quarter)**. Conversely, Helpdesk Management reported an expenditure of approximately **Rs 11 Lakh per quarter**.

Following independent validation, we confirm that **Helpdesk Management’s figure is correct**. Actual net refunds across the 18-month period total **Rs 67,09,932.00 (an average of Rs 11,18,322.00 per quarter)**.

The variance of Rs 22.34 Crore was caused by two technical export artifacts:

| Reconciliation Stage | Impacted Records | Financial Impact (INR) | Cause & Evidence |
|---|---:|---:|---|
| **Raw Export Baseline** | 12,238 rows | Rs 23,01,24,081.00 | Unadjusted initial raw extract. |
| **Migration Re-Import Duplicates** | -638 duplicate rows (125 refunds) | -Rs 3,61,01,100.00 (raw)<br>(-Rs 3,61,011.00 normalized) | Tickets migrated from Freshdesk in Sep 2025 were re-imported, creating duplicate records across both systems. |
| **Legacy Currency Subunit Scaling** | 3,236 legacy tickets | -Rs 18,73,13,049.00 | Freshdesk natively stored amounts in **paise** (subunits). Direct summation inflated legacy figures by a factor of 100. |
| **Final Reconciled Net Refunds** | **11,600 unique tickets (2,340 refunds)** | **Rs 67,09,932.00** | **Average: Rs 11.18 Lakh / quarter (~Rs 11.2 Lakh).** |

---

### 2. Operational Drivers & Agent Attribution Audit

- **Are Agents Giving Away Money? No.**  
  Refund volumes are concentrated in specific agents due to functional division of labor. For example, Ritika D’Souza (Returns Desk) processed Rs 7.74 Lakh across 266 refunds (50.6% refund rate), while Dev Kulkarni (Billing) processed Rs 6.28 Lakh across 235 refunds. Operating Policy §6 explicitly dictates that the Returns Desk and Billing teams handle returns, cancellations, and refunds by design. High volume reflects assigned workload, not rogue behavior.
- **The "Goodwill / Other" Dropdown Trap:**  
  `GW-OTHER` accounts for **Rs 29.07 Lakh (43.3% of total refund value)** across 991 tickets. Because `GW-OTHER` is the top option on the agent dropdown, agents routinely select it as a shortcut for legitimate returns, transit losses, and billing corrections. Crucially, 879 of these tickets exceed the policy's Rs 500 goodwill cap, confirming they represent misclassified product returns rather than discretionary goodwill payouts.
- **Frontline Relaxation & CSAT Reality Check:**  
  Frontline teams were instructed to relax refund standards in Q4 2025, which caused refund spend to jump from Rs 12.07 Lakh (Q3 2025) to Rs 16.28 Lakh (Q4 2025, a +35% surge). However, customer CSAT **did not improve by +0.4** as originally anticipated; overall CSAT remained virtually flat (+0.03 delta, moving from 3.48 to 3.51).

---

### 3. High-Priority Leakage: The Dual-Benefit Exception

Operating Policy §5 strictly prohibits customers from receiving both a refund and a replacement unit for the same order. Our audit identified **166 unique cases** where customers received both.
- **Direct Cash Refund Leakage:** Rs 5,74,191.00
- **Replacement Unit Cost Leakage:** Rs 2,40,530.00
- **Reverse/Forward Shipping Cost:** Rs 56,440.00 (Rs 340 per unit)
- **Total Company Loss:** **Rs 8,71,161.00 (~Rs 1.45 Lakh per quarter)**

---

### 4. Measurable Business Recommendation

> **Target Business Goal:**  
> Implement an automated validation rule in the helpdesk platform preventing refund authorization on any order where a replacement shipment is active without Team Lead approval. This will reduce dual-benefit exceptions from **7.09% of refund tickets to 0%**, saving **Rs 1,45,193.50 per quarter** in avoidable cash and inventory losses.

Additionally, reordering the reason code dropdown to require specific root-cause tags will immediately restore accurate financial visibility over Rs 4.85 Lakh per quarter currently masked under `GW-OTHER`.

---

### 5. Assessment Scope & Limitations
This analysis utilizes support data through 30 June 2026. Payment gateway interchange fees and transit insurance claims are maintained in separate ERP ledgers and were excluded from this support helpdesk audit.
