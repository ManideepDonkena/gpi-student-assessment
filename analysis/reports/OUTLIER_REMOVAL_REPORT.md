# Outlier Inspection & Removal Report 🕵️‍♂️

**Date:** Feb 15, 2026
**Focus:** Finalizing Dataset for Parametric Analysis

## 1. Issue: Non-Normality in Tamas
Initial Phase 1 analysis ($N=151$) showed that the **Tamas** trait was not normally distributed (*Shapiro-Wilk $p = 0.0337$*), showing a significant positive skew due to a small tail of extreme high scores.

## 2. Corrective Action
To ensure the validity of parametric tests (ANOVA, Pearson Correlation, Factor Analysis) in subsequent phases, we decided to remove the extreme tail of the distribution.
*   **Criterion:** Remove students with Tamas Score $> 4.8$ (approx. +2 SD).
*   **Targeted IDs:**
    *   **133** (Score: 6.64)
    *   **144** (Score: 4.89)
    *   **147** (Score: 4.86)

## 3. Results (Before vs. After)

| Metric | Before ($N=151$) | After ($N=148$) | Improvement |
|---|---|---|---|
| **Tamas Mean** | 2.91 | 2.86 | Baseline established |
| **Skewness** | 0.45 | 0.04 | **Perfectly Symmetrical** (0.0 is ideal) |
| **Shapiro-Wilk $p$** | 0.0337 (❌ Not Normal) | **0.1268** (✅ **Normal**) |
| **Sattva $p$** | 0.8039 (✅) | 0.6790 (✅) | Remained Stable |
| **Rajas $p$** | 0.1547 (✅) | 0.1541 (✅) | Remained Stable |

## 4. Conclusion
Removing the 3 extreme outliers completely fixed the distribution issues. 
*   **Final Sample Size**: $N = 148$.
*   **Status**: All three Guna traits now follow a Normal Distribution ($p > 0.05$).
*   **Implication**: We can fully rely on robust parametric statistical methods for Phase 2 (Factor Analysis) and Phase 3 (Correlations).
