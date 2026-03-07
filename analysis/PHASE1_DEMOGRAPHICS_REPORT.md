# Phase 1: Demographics & Distributions Analysis

**Cohort**: BFI-44 | **Sample Size**: N=112

## 1. Demographic Profile

## 2. Guna Distributions (Normality Check)

| Guna | Mean | Std Dev | Skewness | Kurtosis | Shapiro-Wilk p-value | Normality |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sattva | 4.94 | 0.91 | 0.26 | -0.34 | 0.1429 | Yes |
| Rajas | 3.99 | 0.92 | 0.21 | 1.80 | 0.0132 | No (Significant Deviation) |
| Tamas | 3.13 | 1.14 | 0.73 | 1.26 | 0.0018 | No (Significant Deviation) |

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