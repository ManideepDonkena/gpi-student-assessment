# GPI Research Analysis Workflow 🚀

**Goal**: Full end-to-end pipeline — from Firebase data fetch to psychometric validation and reviewer defense.

## 📂 Directory Structure
```
analysis/
├── data/                          # Raw & processed data
│   ├── firebase_service_account_key.json   # 🔑 Required for data fetch
│   ├── original_gpi_dump.json     # Raw Firebase export
│   ├── bfi44_cleaned.json         # After quality filters
│   ├── final_dataset_refined.json # After item refinement (main dataset)
│   └── DATA_SCHEMA.json           # JSON Schema for future research
├── scripts/                       # Analysis scripts
│   ├── run_full_pipeline.py       # ⭐ Master orchestrator
│   ├── fetch_original_data.py     # Step 0: Firebase → JSON
│   ├── clean_and_analyze.py       # Step 1: Quality filters
│   ├── deep_analysis_phase1.py    # Step 2: Descriptives
│   ├── analyze_cronbach.py        # Step 3: Reliability
│   ├── deep_analysis_phase3.py    # Step 4: Correlations
│   ├── deep_analysis_phase4.py    # Step 5: EFA
│   ├── analyze_item_refinement.py # Step 6: Item refinement
│   ├── deep_analysis_phase6.py    # Step 7: Demographics
│   ├── deep_analysis_phase7.py    # Step 8: Scenario validity
│   ├── deep_analysis_phase8.py    # Step 9: Incremental validity
│   └── deep_analysis_phase9.py    # Step 10: Reviewer defense
├── reports/                       # Generated Markdown reports
├── images/                        # Generated plots & charts
└── WORKFLOW.md                    # This file
```

---

## ⚡ Quick Run (One Command)

```bash
# Analysis only (using existing data):
python scripts/run_full_pipeline.py

# Fetch fresh data from Firebase, then analyze:
python scripts/run_full_pipeline.py --fetch

# Resume from a specific step:
python scripts/run_full_pipeline.py --from-step 7
```

---

## 🔄 Step-by-Step Breakdown

### Step 0: Fetch Data from Firebase (Optional)
**Script**: `python scripts/fetch_original_data.py`
- **Requires**: `data/firebase_service_account_key.json`
- **What it does**: Connects to Firestore, fetches all `original-gpi` sessions
- **Output**: `data/original_gpi_dump.json` + `data/original_gpi_wide.csv`
- **When to run**: When new responses have been collected
- **Flag**: Use `--fetch` with the pipeline to include this step

### Step 1: Clean & Filter Data (Phase 0)
**Script**: `python scripts/clean_and_analyze.py`
- **Input**: `data/original_gpi_dump.json`
- **Filters applied**:
  - ❌ Speed Runners (Guna < 3min, BFI < 2min)
  - ❌ Dummy Data (Male + Homemaker pattern)
  - ❌ Extreme Outliers (Tamas > 4.8)
- **Output**: `data/bfi44_cleaned.json`
- **Report**: `reports/CLEAN_ANALYSIS_REPORT.md`

### Step 2: Descriptive Analysis (Phase 1)
**Script**: `python scripts/deep_analysis_phase1.py`
- **Input**: `data/bfi44_cleaned.json`
- **Analyses**: Mean, SD, Skewness, Kurtosis, Shapiro-Wilk normality tests
- **Output**: `reports/PHASE1_DETAILED_REPORT.md` + distribution plots

### Step 3: Reliability Analysis (Phase 2)
**Script**: `python scripts/analyze_cronbach.py`
- **Input**: `data/bfi44_cleaned.json`
- **Analyses**: Cronbach's α for all Guna subscales and BFI traits
- **Key Results**: Sattva α=.893, Rajas α=.868, Tamas α=.924

### Step 4: Correlation Analysis (Phase 3)
**Script**: `python scripts/deep_analysis_phase3.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**: Guna↔BFI correlations, convergent/discriminant validity
- **Output**: `reports/PHASE3_CORRELATION_REPORT.md` + heatmap

### Step 5: Factor Analysis (Phase 4)
**Script**: `python scripts/deep_analysis_phase4.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**: Joint EFA with Guna + BFI items, scree plot, factor loadings
- **Output**: `reports/PHASE4_FACTOR_ANALYSIS_REPORT.md`

### Step 6: Item Refinement (Phase 5)
**Script**: `python scripts/analyze_item_refinement.py`
- **Input**: `data/bfi44_cleaned.json`
- **What it does**: Drops weak items (low loading, cross-loading), recalculates scores
- **Output**: `data/final_dataset_refined.json` (N=152)
- **Report**: `reports/PHASE5_ITEM_REFINEMENT_REPORT.md`

### Step 7: Demographic Analysis (Phase 6)
**Script**: `python scripts/deep_analysis_phase6.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**: Gender, year, spiritual practice differences via ANOVA/t-tests
- **Output**: `reports/PHASE6_DEMOGRAPHIC_REPORT.md`

### Step 8: Scenario Validation (Phase 7) — Criterion Validity
**Script**: `python scripts/deep_analysis_phase7.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**: Guna scores → behavioral scenario choices (point-biserial r, ANOVA)
- **Key Results**: Sattva r=.46, Rajas r=.36, Tamas r=.35 (all p < .001)
- **Output**: `reports/PHASE7_SCENARIO_VALIDATION_REPORT.md`

### Step 9: Incremental Validity (Phase 8)
**Script**: `python scripts/deep_analysis_phase8.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**: Hierarchical regression — does Guna predict beyond Big Five?
- **Key Results**: ΔR² = +6.8% to +22.7% (all p < .01)
- **Output**: `reports/PHASE8_INCREMENTAL_VALIDITY_REPORT.md`

### Step 10: Reviewer Defense (Phase 9) — Implicit Variables
**Script**: `python scripts/deep_analysis_phase9.py`
- **Input**: `data/final_dataset_refined.json`
- **Analyses**:
  1. KMO & Bartlett's test (EFA adequacy)
  2. **Implicit behavioral variable analysis** (answerChanges, tabSwitches, hoverCount, reactionTime, cursorDistance)
  3. Reliability-corrected (disattenuated) correlations
  4. Split-half cross-validation
  5. Per-scenario criterion validity
  6. 95% Confidence intervals
  7. Bonferroni-corrected demographic tests
- **Output**: `reports/PHASE9_REVIEWER_DEFENSE_REPORT.md`

---

## 📊 Generated Reports (in order)

| Report | Phase | Content |
|--------|-------|---------|
| `CLEAN_ANALYSIS_REPORT.md` | 0 | Data cleaning summary, N before/after |
| `PHASE1_DETAILED_REPORT.md` | 1 | Descriptive stats, normality |
| `PHASE2_RELIABILITY_REPORT.md` | 2 | Cronbach's alpha per subscale |
| `PHASE3_CORRELATION_REPORT.md` | 3 | Convergent/discriminant validity |
| `PHASE4_FACTOR_ANALYSIS_REPORT.md` | 4 | EFA loadings, scree plot |
| `PHASE5_ITEM_REFINEMENT_REPORT.md` | 5 | Item drops, before/after α |
| `PHASE6_DEMOGRAPHIC_REPORT.md` | 6 | Group differences |
| `PHASE7_SCENARIO_VALIDATION_REPORT.md` | 7 | Criterion validity |
| `PHASE8_INCREMENTAL_VALIDITY_REPORT.md` | 8 | Beyond Big Five |
| `PHASE9_REVIEWER_DEFENSE_REPORT.md` | 9 | Robustness & implicit variables |

---

## 🔑 Implicit Behavioral Variables

The assessment captures **6 categories** of implicit variables to control social desirability:

| Variable | Location in Data | What it Measures |
|----------|-----------------|------------------|
| `answerChanges` | `gunaMetadata` / `bigFiveMetadata` | Times respondent changed their answer |
| `tabSwitches` | `gunaMetadata` / `bigFiveMetadata` | Browser tab switches during section |
| `cursorDistancePx` | `gunaMetadata` / `bigFiveMetadata` | Total mouse movement (engagement) |
| `idleTimeMs` | `gunaMetadata` | Idle/inactive time |
| `hoverCount` | `scenarioResponses[]` | Option hovers before final choice |
| `timeToSelectMs` | `scenarioResponses[]` | Time to finalize scenario choice |
| `reactionTimeMs` | `gunaDetails.*.reactionTimeMs` | Per-item reaction time |

**Schema**: See `data/DATA_SCHEMA.json` for the complete JSON Schema (draft-07).

---

## 🔄 Updating Data (New Responses)

When new survey responses are collected:

1. **Fetch**: `python scripts/run_full_pipeline.py --fetch`
2. **Or manually**:
   ```bash
   python scripts/fetch_original_data.py       # Fetch new data
   python scripts/run_full_pipeline.py          # Re-run analysis
   ```
3. All reports and images will be regenerated with the updated dataset.

---

## 📋 Prerequisites

```bash
pip install pandas numpy scipy scikit-learn matplotlib firebase-admin
```

**Firebase setup** (for data fetch only):
1. Go to Firebase Console → Project Settings → Service Accounts
2. Generate a new private key
3. Save as `analysis/data/firebase_service_account_key.json`
