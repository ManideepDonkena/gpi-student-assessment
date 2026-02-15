# Phase 2: Factor Analysis Report

**Method**: PCA/EFA | **Items**: 80 | **Sample**: N=94

## 1. Eigenvalue Analysis (The 'Elbow')
The Scree Plot visually demonstrates how many underlying factors (constructs) exist in the data.

![Scree Plot](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/phase2_scree_plot.png)

| Factor | Eigenvalue | Variance Explained (%) | Cumulative (%) |
| :--- | :--- | :--- | :--- |
| 1 | 20.915 | 25.87% | 25.87% |
| 2 | 7.026 | 8.69% | 34.55% |
| 3 | 5.735 | 7.09% | 41.65% |
| 4 | 4.312 | 5.33% | 46.98% |
| 5 | 2.757 | 3.41% | 50.39% |

## 2. Factor Interpretability
Checking if the top 3 factors map roughly to Sattva, Rajas, and Tamas.


### Factor 1 Top Loadings:
| Item | Loading | Intended Guna |
| :--- | :--- | :--- |
| T_L | 0.728 | Tamas |
| T_FF | 0.718 | Tamas |
| T_CV | 0.714 | Tamas |
| T_AX | 0.702 | Tamas |
| T_FD | 0.691 | Tamas |

### Factor 2 Top Loadings:
| Item | Loading | Intended Guna |
| :--- | :--- | :--- |
| S_DL | 0.715 | Sattva |
| S_FL | 0.714 | Sattva |
| S_EP | 0.672 | Sattva |
| S_CH | 0.643 | Sattva |
| R_AV | 0.634 | Rajas |

### Factor 3 Top Loadings:
| Item | Loading | Intended Guna |
| :--- | :--- | :--- |
| R_BH | 0.673 | Rajas |
| T_X | 0.626 | Tamas |
| T_FB | 0.616 | Tamas |
| R_EV | 0.587 | Rajas |
| T_CJ | 0.557 | Tamas |
### Interpretation Guide
- **Eigenvalue**: Represents the amount of information (variance) a factor explains.
    - **Rule of Thumb**: Only factors with Eigenvalues > 1.0 are considered "real" constructs.
    - **The Elbow**: Where the Scree Plot levels off indicates the optimal number of factors.
- **Factor Loading**: The correlation between an Item and a Factor.
    - **> 0.70**: Very Strong link. The item clearly measures this factor.
    - **0.50 - 0.70**: Moderate link.
    - **< 0.30**: Weak link. The item might be measuring something else.
- **Cross-Loading**: When an item has high loadings on *multiple* factors. This is bad; it means the question is ambiguous.