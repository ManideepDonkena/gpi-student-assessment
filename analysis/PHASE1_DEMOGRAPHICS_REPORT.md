# Phase 1: Demographics & Distributions Analysis

**Cohort**: BFI-44 | **Sample Size**: N=94

## 1. Demographic Profile

## 2. Guna Distributions (Normality Check)

| Guna | Mean | Std Dev | Skewness | Kurtosis | Shapiro-Wilk p-value | Normality |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sattva | 4.94 | 0.93 | 0.21 | -0.24 | 0.2054 | Yes |
| Rajas | 4.00 | 0.93 | 0.28 | 2.20 | 0.0053 | No (Significant Deviation) |
| Tamas | 3.11 | 1.15 | 0.78 | 1.56 | 0.0016 | No (Significant Deviation) |

### Interpretation Guide
- **Mean & Standard Deviation (SD)**: The average score and the spread. Low SD (< 1.0) means most students score close to the average. High SD (> 1.0) means scores are very spread out.
- **Skewness**:
    - **0**: Perfectly symmetrical (Normal).
    - **Positive (> 0)**: Tail on the right (More low scores).
    - **Negative (< 0)**: Tail on the left (More high scores).
- **Kurtosis**:
    - **0**: Normal "bell curve" peak based on Normal distribution.
    - **Positive**: Very sharp peak (everyone scores the same).
    - **Negative**: Very flat distribution (everyone scores differently).
- **Shapiro-Wilk Test**:
    - **p > 0.05**: Data is Normal (Bell Curve). T-tests are valid.
    - **p < 0.05**: Data is NOT Normal. Use non-parametric tests (Mann-Whitney) if sample is small.
### Interpretation
- **Shapiro-Wilk Test**: A p-value > 0.05 indicates the data is likely normally distributed.
- **Visual Inspection**: See generated `dist_*.png` files.