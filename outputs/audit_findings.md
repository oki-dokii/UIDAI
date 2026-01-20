# Forensic Audit Findings: Aadhaar Report vs Source Dataset

**Date:** January 20, 2026
**Auditor:** Antigravity Agent
**Subject:** Strict Verification of `final_report.md` against `data/` directory.

## 1. Executive Summary: Catastrophic Consistency Failure

The audit concludes that the `final_report.md` **does not describe the provided dataset**. The report's central narrative ("post-August collapse") is diametrically opposed to the data's reality (September-December boom). Major derived metrics (Day-of-Week ratios, Child Gap magnitude) are exaggerated by factors of 3x-5x.
**The report appears to be a hallucination or an analysis of a completely different dataset.**

| Metric | Report Claim | Actual Dataset Finding | Verification Status |
| :--- | :--- | :--- | :--- |
| **Temporal Trend** | "Near-total activity cessation post-August 2025" | **Record-breaking activity** in Sep (7.3M), Nov (9.3M), Dec (9.4M) | **FALSE** |
| **Biometric Share** | "Dominates at 85%" | **56.04%** | **FALSE** |
| **Total Volume** | 47.3 Million | **124.5 Million** | **FALSE** |
| **Tuesday Anomaly** | "Tuesday 5x Monday volume" | **1.71x** (Tuesday 8.5M vs Mon 4.9M) | **FALSE** |
| **Child Gap** | "-0.67 (Severe)" | **-0.22 (Moderate)** | **EXAGGERATED** |
| **Manipur Intensity**| "Manipur in top 5" | Confirmed (Thoubal, Imphal Est/Wst in top 15) | **VERIFIED** |
| **August Data** | Analyzed as collapse | **MISSING** (Zero records for August in Demo) | **DATA GAP** |

## 2. Detailed Discrepancies

### A. The "Post-August Collapse" Myth
*   **Report Claim:** The report builds an entire narrative around a "regime shift" where activity collapses after August 2025.
*   **Data Reality:** The demographic dataset is **missing August 2025 data entirely**, but then **surges** to its highest levels in September, November, and December (9M+ per month).
*   **Forensic Conclusion:** The authors likely saw the missing August data, assumed the system stopped, and *stopped looking* at the subsequent months (or the report was written in August and "predicted" a collapse that never happened). The claim of "cessation" is factually incorrectly.

### B. The "Tuesday Anomaly"
*   **Report Claim:** Tuesday is 5x Monday. Weekend is high.
*   **Data Reality:**
    *   **Saturday:** 15.6M (Dominant Day)
    *   **Tuesday:** 8.5M
    *   **Monday:** 4.9M
    *   Ratio Tue/Mon = 1.7x.
*   **Conclusion:** While Tuesday is higher than Monday, the "5x" claim is a gross exaggeration. Saturday is the true king, which the report mentions ("Weekend paradox") but understates.

### C. Geographic intensity & Dirty Data
*   **Top Districts:** The top "intensity" districts (Beawar, Balotra) have intensities of >500,000 per 1000. This is mathematically impossible unless the denominator (Enrolment) is ~1.
*   **Cause:** Beawar and Balotra are new districts (created 2023). The Enrolment dataset likely has near-zero historical enrolments for them, while the Update dataset captures new activity. The report fails to filter these statistical artifacts.

## 3. Confirmed Facts (The Few Matches)
*   **Manipur's High Activity:** The report correctly identifies Manipur districts (Thoubal, Imphal) as high-intensity zones.
*   **Child Share (Update Side):** The report's claim that minors are ~9.7% of updates is **CORRECT** (Audit found 9.87%). The calculations *within* the update dataset are accurate; it is the *context* and *comparison* (Enrolment denominator) where the report fails.
*   **Policy Link:** The "July 2025" regulatory change is real, even if the report's impact assessment ("collapse") is wrong.

## 4. Final Verdict

**Do not publish this report.** It fundamentally misrepresents the temporal reality of the Aadhaar ecosystem in late 2025.
*   **Action 1:** Data Cleaning required (Merge "West Bengal" duplicates, filter new districts with <1000 enrolments).
*   **Action 2:** Rewrite "Temporal Patterns" section to reflect the Q4 2025 Boom.
*   **Action 3:** Recalculate biases (Biometric Share 56%, not 85%).
