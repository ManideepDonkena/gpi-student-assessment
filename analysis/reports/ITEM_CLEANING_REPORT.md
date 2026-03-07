# Item Analysis & Cleaning Report 🧹

**Date:** Feb 15, 2026
**Phase:** 2 (Reliability Optimization)
**Dataset:** N = 148 (Cleaned)

## 1. Objective
Identify and remove "noisy" or "bad" questions that lower the internal consistency (reliability) of the personality scales. High reliability (Cronbach's Alpha > 0.7) is a prerequisite for valid Factor Analysis.

## 2. Findings
We analyzed the Cronbach's Alpha for each scale and calculated the "Alpha if Item Deleted".

### 🚨 Critical Issues (Must Fix)
**Scale: Big Five - Openness**
*   **Current Alpha:** `0.540` (Unacceptable < 0.6)
*   **Problem Items:**
    *   `BFI41 (R)`: Removing increases Alpha by **+0.140**.
    *   `BFI35 (R)`: Removing increases Alpha by **+0.072**.
*   **Proposal:** Remove both. **New Alpha ~0.750** (Good).

### ⚠️ Minor Issues (Optimization)
**Scale: SRT - Rajas**
*   **Current Alpha:** `0.848` (Good)
*   **Problem Items:** `R_AV`, `R_BX`
*   **Impact:** Removing them improves Alpha to `0.859`.
*   **Proposal:** Remove to tighten the scale definition.

**Scale: SRT - Sattva & Tamas**
*   **Status:** Excellent reliability (> 0.87).
*   **Action:** No changes needed. Minor detractors (`S_J`, `T_DH`) have negligible impact (< 0.004).

## 3. Recommendation
I recommend applying the following **Item Cleaning** filter:
1.  **Drop** `BFI41`, `BFI35` (Fixes Openness)
2.  **Drop** `R_AV`, `R_BX` (Optimizes Rajas)

**Next Step:**
Create a `refine_items.py` script to generate a `final_dataset_N148.json` with these columns dropped, then proceed to Phase 3 (Factor Analysis).
